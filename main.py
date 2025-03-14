import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from test_extracator import text_extraction_tool
from translation_tool import text_translation_tool
from text_proccessing import process_text  # ✅ Ensure text correctness
from prompts import context
from languges import google_translate_languages, tesseract_languages

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# ✅ Mount static files correctly
static_path = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")

# ✅ Configure templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ✅ Ensure temp directory exists and is writable
TEMP_DIR = BASE_DIR / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)  # ✅ Create the folder if it doesn’t exist

# ✅ Ensure permissions for the temp folder
if not os.access(TEMP_DIR, os.W_OK):
    raise PermissionError(f"البرنامج لا يملك إذن الكتابة إلى المجلد: {TEMP_DIR}. يرجى التحقق من الصلاحيات.")

llm = OpenAI(model="chatgpt-4o-latest", temperature=0)
agent = ReActAgent.from_tools(tools=[text_extraction_tool, text_translation_tool], llm=llm, verbose=True, context=context)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("text_extraction_ui.html", {"request": request})

@app.post("/process")
async def process(
    image_file: UploadFile = File(None),  # ✅ Set default to None to handle missing files
    action: str = Form(...),  
    in_lang: str = Form(...),
    dest_lang: str = Form(None)
):
    # ✅ Server-Side Validation: Ensure all required fields are present
    if not image_file:
        raise HTTPException(status_code=400, detail="يرجى تحميل صورة قبل المتابعة.")

    if not action:
        raise HTTPException(status_code=400, detail="يرجى تحديد ما إذا كنت تريد استخراج النص فقط أو الترجمة.")

    if not in_lang:
        raise HTTPException(status_code=400, detail="يرجى تحديد لغة النص في الصورة.")

    if action == "translate" and not dest_lang:
        raise HTTPException(status_code=400, detail="يرجى تحديد لغة الترجمة.")

    # ✅ Construct file path safely
    file_path = TEMP_DIR / image_file.filename

    try:
        with open(file_path, "wb") as f:
            f.write(await image_file.read())
    except PermissionError:
        raise HTTPException(status_code=500, detail="خطأ في الصلاحيات! لا يمكن حفظ الملف. يرجى التحقق من إذونات المجلد.")

    text_lang = tesseract_languages.get(in_lang, "eng")
    src = google_translate_languages.get(in_lang, "en")
    dest = google_translate_languages.get(dest_lang, "en") if dest_lang else None

    if action == "extract":
        prompt = f"Extract text from image with path: {file_path} language of the text in image {text_lang}"
        response = agent.query(prompt)
    elif action == "translate":
        prompt = (
            f"Extract text from image with path: {file_path} "
            f"language of the text in image {text_lang}, and then translate the "
            f"extracted text from {src} language to {dest} language"
        )
        response = agent.query(prompt)
    else:
        return JSONResponse(content={"error": "طلب غير صالح."}, status_code=400)

    response_text = str(response) if isinstance(response, (str, bytes)) else response.response  

    # ✅ Delete the temp file after processing
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"خطأ أثناء حذف الملف: {e}")

    return JSONResponse(content={"result": response_text})  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
