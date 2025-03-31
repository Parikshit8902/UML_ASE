import os
import base64
import zlib
import urllib.parse
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import xml.etree.ElementTree as ET

app = FastAPI()

# Groq API Configuration
GROQ_API_KEY = "paste_api_key_here"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"  # Change this based on the model you want to use

# Get absolute paths
static_dir = r"C:\Users\Parikshit V. Joshi\OneDrive\Desktop\v3\static"
drawio_dir = r"C:\Users\Parikshit V. Joshi\OneDrive\Desktop\v3\drawio-26.1.0\drawio-26.1.0"

# Ensure directories exist
if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory '{static_dir}' does not exist. Please create it.")

if not os.path.exists(drawio_dir):
    raise RuntimeError(f"Draw.io directory '{drawio_dir}' does not exist. Check the path!")

# Mount static and Draw.io directories
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/drawio-26.1.0/drawio-26.1.0", StaticFiles(directory=drawio_dir), name="drawio-26.1.0")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

def decode_drawio_diagram(encoded_data):
    try:
        compressed_data = base64.b64decode(encoded_data)
        decompressed_data = zlib.decompress(compressed_data, -15).decode("utf-8")
        if "%3C" in decompressed_data:
            decompressed_data = urllib.parse.unquote(decompressed_data)
        return decompressed_data
    except Exception as e:
        print("❌ Error decoding UML diagram:", str(e))
        return None

def call_groq_llm(prompt):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}]}
    
    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    else:
        return f"Error from Groq API: {response.text}"

@app.post("/upload_xml")
async def upload_xml(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".xml"):
            raise HTTPException(status_code=400, detail="Only XML files are allowed.")

        content = await file.read()
        xml_data = content.decode("utf-8")
        root = ET.fromstring(xml_data)
        diagram_element = root.find("diagram")
        if diagram_element is None or not diagram_element.text.strip():
            raise ValueError("Missing or empty <diagram> element in XML.")

        decoded_xml = decode_drawio_diagram(diagram_element.text.strip())
        if not decoded_xml:
            raise ValueError("Failed to decode UML diagram data.")

        prompt = f"""
        You are an expert in software architecture and UML modeling. Given the following UML diagram in XML format from Draw.io, analyze and provide insights.

        ## UML XML Input:
        {decoded_xml}

        ## Expected Output:
        - **Classes & Attributes:** `<list of extracted elements>`
        - **Relationships & Multiplicities:** `<list of detected connections>`
        - **Potential Issues:** `<list of issues in the UML>`
        - **Improvement Suggestions:** `<recommendations for improving the UML model>`
        """
        
        llm_output = call_groq_llm(prompt)
        return JSONResponse(content={"feedback": llm_output})
    
    except Exception as e:
        print("❌ Error processing XML file:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5500, reload=True)

#http://127.0.0.1:5500
