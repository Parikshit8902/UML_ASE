import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import json
import ollama

app = FastAPI()

# Get absolute paths
static_dir = r"C:\Users\Student\Desktop\ASE_Proj\v2\static"
drawio_dir = r"C:\Users\Student\Desktop\ASE_Proj\v2\drawio"

# Ensure directories exist
if not os.path.exists(static_dir):
    raise RuntimeError(f"Static directory '{static_dir}' does not exist. Please create it.")

if not os.path.exists(drawio_dir):
    raise RuntimeError(f"Draw.io directory '{drawio_dir}' does not exist. Check the path!")

# Mount static and Draw.io directories
app.mount("/static", StaticFiles(directory=static_dir), name="static")
app.mount("/drawio", StaticFiles(directory=drawio_dir), name="drawio")

# Serve index.html at "/"
@app.get("/")
async def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/get_ai_feedback")
async def get_ai_feedback(request: Request):
    try:
        data = await request.json()
        diagram_data = data.get("diagramData", "")

        if not diagram_data:
            return {"error": "No diagram data received"}

        # Send diagram data to an AI model for feedback
        prompt = f"Analyze the following UML diagram data and provide feedback:\n\n{diagram_data}"
        response = ollama.chat(model="llama3.2", messages=[{"role": "user", "content": prompt}])

        return {"feedback": response["message"]}
    
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
