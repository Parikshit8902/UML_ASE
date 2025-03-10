import os
import base64
import zlib
import urllib.parse
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
import ollama
import xml.etree.ElementTree as ET

app = FastAPI()

# Get absolute paths
# Here, provide correct paths of the respective directories
static_dir = r"C:\Users\Parikshit V. Joshi\OneDrive\Desktop\DAIICT_M.Tech\Sem_2\ASE\ASE_Proj\v3\static"
drawio_dir = r"C:\Users\Parikshit V. Joshi\OneDrive\Desktop\DAIICT_M.Tech\Sem_2\ASE\ASE_Proj\v3\drawio-26.1.0\drawio-26.1.0"

# Ensure directories exist
if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory '{static_dir}' does not exist. Please create it.")

if not os.path.exists(drawio_dir):
    raise RuntimeError(f"Draw.io directory '{drawio_dir}' does not exist. Check the path!")

# Mount static and Draw.io directories
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/drawio-26.1.0/drawio-26.1.0", StaticFiles(directory=drawio_dir), name="drawio-26.1.0")

# Serve index.html at "/"
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

def decode_drawio_diagram(encoded_data):
    """
    Decodes Draw.io UML diagram data:
    1. Base64 decode
    2. Deflate decompress
    3. URL decode (if needed)
    """
    try:
        # Step 1: Base64 Decode
        compressed_data = base64.b64decode(encoded_data)

        # Step 2: Decompress using Deflate
        decompressed_data = zlib.decompress(compressed_data, -15).decode("utf-8")

        # Step 3: URL Decode (if applicable)
        if "%3C" in decompressed_data:  # URL encoding check ('<' encoded as '%3C')
            decompressed_data = urllib.parse.unquote(decompressed_data)

        return decompressed_data
    except Exception as e:
        print("❌ Error decoding UML diagram:", str(e))
        return None

@app.post("/upload_xml")
async def upload_xml(file: UploadFile = File(...)):
    try:
        # Ensure it's an XML file
        if not file.filename.endswith(".xml"):
            raise HTTPException(status_code=400, detail="Only XML files are allowed.")

        # Read file content
        content = await file.read()
        xml_data = content.decode("utf-8")

        # Parse XML to extract encoded UML data
        try:
            root = ET.fromstring(xml_data)
            diagram_element = root.find("diagram")
            if diagram_element is None or not diagram_element.text.strip():
                raise ValueError("Missing or empty <diagram> element in XML.")

            encoded_diagram_data = diagram_element.text.strip()
            decoded_xml = decode_drawio_diagram(encoded_diagram_data)

            if not decoded_xml:
                raise ValueError("Failed to decode UML diagram data.")

        except ET.ParseError as e:
            raise HTTPException(status_code=400, detail="Invalid XML format.")

        # Debugging: Print decoded UML XML
        print("✅ Decoded UML XML:\n", decoded_xml)

        # Send clean XML data to LLM
        prompt = f"""
        You are an expert in software architecture and UML modeling. Given the following UML diagram in XML format from Draw.io, analyze and provide insights.  

## **Instructions:**  
1. **Extract Key Elements**  
   - Identify all **classes**, their **attributes**, and **methods (if any)**.  
   - Identify all **relationships** (e.g., **associations, dependencies, generalizations, aggregations, compositions**).  
   - Extract **multiplicities** if present.  

2. **Analyze Model Quality**  
   - Are any **classes missing key attributes** or **methods**?  
   - Are there **redundant** or **ambiguous relationships**?  
   - Are there **unnecessary** or **unused classes**?  

3. **Suggest Improvements**  
   - How can the UML model be **optimized** for clarity and maintainability?  
   - Recommend **better class structures**, **naming conventions**, or **missing relationships**.  
   - Highlight any **potential design flaws** and propose **alternative approaches**.  

### **UML XML Input:**
{decoded_xml}  

## **Expected Output:**
Provide a structured response as follows:
- **Classes & Attributes:** `<list of extracted elements>`
- **Relationships & Multiplicities:** `<list of detected connections>`
- **Potential Issues:** `<list of issues in the UML>`
- **Improvement Suggestions:** `<recommendations for improving the UML model>`

        """

        # Call Ollama LLM
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

        # ✅ FIX: Extract the content safely
        llm_output = response.get("message", {}).get("content", "No response from AI.")

        return JSONResponse(content={"feedback": llm_output})

    except Exception as e:
        print("❌ Error processing XML file:", str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)


#http://127.0.0.1:8000