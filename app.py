import os
from fastapi import FastAPI, Form, HTTPException, Request  # Import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app and templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Groq API endpoint and headers
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
    "Content-Type": "application/json"
}

# Home route
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Translation route
@app.post("/translate", response_class=HTMLResponse)
async def translate(request: Request, text: str = Form(...), language: str = Form(...)):
    prompt = f"Translate the following text to {language}: {text}"

    payload = {
        "model": "llama-3.3-70b-versatile",  # Example model; adjust as needed
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        translated_text = response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {e}")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "original": text,
        "language": language,
        "translated": translated_text
    })
