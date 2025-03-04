from fastapi import FastAPI, Request
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import ollama
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

USE_LOCAL_MODEL = True  # Toggle between Ollama (local) and OpenAI API

@app.post("/analyze_diagram")
async def analyze_diagram(request: Request):
    data = await request.json()
    diagram_xml = data.get("xml")

    if not diagram_xml or not isinstance(diagram_xml, str):
        return {"feedback": "Invalid XML data received"}

    prompt = f"""
    You are an expert in UML modeling. Analyze the following UML diagram XML:

    {diagram_xml}

    Provide feedback on structure, relationships, and best practices.
    """

    if USE_LOCAL_MODEL:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        feedback = response['message']['content']
    else:
        llm = ChatOpenAI(model_name="gpt-4", openai_api_key="your-api-key")
        feedback = llm([SystemMessage(content="Analyze UML"), HumanMessage(content=prompt)]).content

    return {"feedback": feedback}
