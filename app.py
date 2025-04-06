# app.py

import os
import base64
import zlib
import urllib.parse
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import xml.etree.ElementTree as ET
from RAG import analyze_uml

app = FastAPI()

# Directory setup
static_dir = r"C:\Users\Parikshit V. Joshi\OneDrive\Desktop\v3 - Copy\static"
drawio_dir = r"C:\Users\Parikshit V. Joshi\OneDrive\Desktop\v3 - Copy\drawio-26.1.0\drawio-26.1.0"

if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory '{static_dir}' does not exist.")
if not os.path.exists(drawio_dir):
    raise RuntimeError(f"Draw.io directory '{drawio_dir}' does not exist.")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/drawio-26.1.0/drawio-26.1.0", StaticFiles(directory=drawio_dir), name="drawio")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

def decode_drawio_diagram(encoded_data: str) -> str:
    try:
        compressed_data = base64.b64decode(encoded_data)
        decompressed_data = zlib.decompress(compressed_data, -15).decode("utf-8")
        if "%3C" in decompressed_data:
            decompressed_data = urllib.parse.unquote(decompressed_data)
        return decompressed_data
    except Exception as e:
        print("❌ Error decoding UML diagram:", str(e))
        return None

@app.post("/upload_xml")
async def upload_xml(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".xml"):
            raise HTTPException(status_code=400, detail="Only XML files are allowed.")

        content = await file.read()
        root = ET.fromstring(content.decode("utf-8"))
        diagram_element = root.find("diagram")
        if diagram_element is None or not diagram_element.text.strip():
            raise ValueError("Missing or empty <diagram> element in XML.")

        decoded_xml = decode_drawio_diagram(diagram_element.text.strip())
        if not decoded_xml:
            raise ValueError("Failed to decode UML diagram data.")

        feedback = analyze_uml(decoded_xml)
        return JSONResponse(content={"feedback": feedback})

    except Exception as e:
        print("❌ Error processing XML file:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5500, reload=True)

#http://127.0.0.1:5500
