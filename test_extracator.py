from PIL import Image
import pytesseract
from llama_index.core.tools import FunctionTool

# Function to extract text from an image
def extract_text_from_image(path: str, lang: str)-> str :
    """extracts text from imges and returns the extracted text"""
    try:
        # Open the image()
        image = Image.open(path)
        
        # Extract text using Tesseract OCR
        extracted_text = pytesseract.image_to_string(image, lang)
        
        return extracted_text
    except Exception as e:
        return f"Error: {e}"

# Tool function
text_extraction_tool = FunctionTool.from_defaults(fn=extract_text_from_image)
    
