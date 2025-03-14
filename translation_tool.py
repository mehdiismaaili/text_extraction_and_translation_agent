import textwrap
from googletrans import Translator
import asyncio
import nest_asyncio
from llama_index.core.tools import FunctionTool

# Apply nest_asyncio to handle nested event loops in FastAPI
nest_asyncio.apply()

# ✅ Main async translation function
async def translate_large_text(text, src, dest, chunk_size=5000):
    translator = Translator()
    chunks = textwrap.wrap(text, chunk_size)  # Split text into smaller chunks
    translated_chunks = []

    for chunk in chunks:
        translated = await translator.translate(chunk, src=src, dest=dest)  # ✅ Await the coroutine
        translated_chunks.append(translated.text)

    return " ".join(translated_chunks)  # ✅ Join translated chunks into one text

# ✅ Async function for FastAPI
async def translation_tool(text, src, dest):
    return await translate_large_text(text, src, dest)  # ✅ Await the function call

# Translation tool for the agent
text_translation_tool = FunctionTool.from_defaults(fn=translation_tool)
