# RAG.py

import requests

# Groq API setup
GROQ_API_KEY = "api_key"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

def retrieve_context(xml_text: str) -> str:
    """
    Placeholder retrieval logic. In a full implementation, this would
    search a knowledge base or documents relevant to UML best practices.
    """
    return """
    # UML Best Practices:
    - Use clear and consistent naming for classes and attributes.
    - Avoid overly complex relationships and cyclic dependencies.
    - Ensure that multiplicities are well defined.
    - Favor composition over inheritance when appropriate.
    - Ensure responsibilities are distributed properly following SOLID principles.
    """

def build_prompt(xml_text: str, context: str) -> str:
    return f"""
    You are an expert in software architecture and UML modeling. Analyze the following UML model.

    ## Context:
    {context}

    ## UML XML Input:
    {xml_text}

    ## Expected Output:
    - **Classes & Attributes:** `<list of extracted elements>`
    - **Relationships & Multiplicities:** `<list of detected connections>`
    - **Potential Issues:** `<list of issues in the UML>`
    - **Improvement Suggestions:** `<recommendations for improving the UML model>`

    Be thorough and detailed.
    """

def query_groq(prompt: str) -> str:
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(GROQ_API_URL, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("choices", [{}])[0].get("message", {}).get("content", "No response from AI.")
    else:
        return f"Error from Groq API: {response.text}"

def analyze_uml(xml_text: str) -> str:
    context = retrieve_context(xml_text)
    prompt = build_prompt(xml_text, context)
    return query_groq(prompt)
