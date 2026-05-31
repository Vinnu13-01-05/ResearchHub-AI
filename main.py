from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
import os
import requests

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI()

# Groq Client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Store uploaded PDF text globally
pdf_text_storage = ""

# Chat Request Model
class ChatRequest(BaseModel):
    message: str

# Home Endpoint
@app.get("/")
def home():
    return {"message": "ResearchHub AI Running"}

# AI Chat Endpoint
@app.post("/chat")
def chat(request: ChatRequest):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": request.message
            }
        ]
    )

    return {
        "response": response.choices[0].message.content
    }

# Research Paper Search Endpoint
@app.get("/search")
def search_papers(query: str):

    url = f"http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"

    response = requests.get(url)

    return {
        "query": query,
        "results": response.text
    }

# PDF Upload Endpoint
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    global pdf_text_storage

    pdf = PdfReader(file.file)

    text = ""

    for page in pdf.pages:
        text += page.extract_text() or ""

    pdf_text_storage = text

    return {
        "filename": file.filename,
        "characters_extracted": len(text),
        "preview": text[:1000]
    }

# PDF Summarization Endpoint
@app.post("/summarize-pdf")
async def summarize_pdf(file: UploadFile = File(...)):

    pdf = PdfReader(file.file)

    text = ""

    for page in pdf.pages:
        text += page.extract_text() or ""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"Summarize this research paper:\n\n{text[:5000]}"
            }
        ]
    )

    return {
        "filename": file.filename,
        "summary": response.choices[0].message.content
    }

# Ask Questions About Uploaded PDF
@app.post("/ask-pdf")
def ask_pdf(request: ChatRequest):

    global pdf_text_storage

    if not pdf_text_storage:
        return {
            "error": "Please upload a PDF first using /upload-pdf"
        }

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Answer questions only from the uploaded PDF content."
            },
            {
                "role": "user",
                "content": f"PDF Content:\n{pdf_text_storage[:5000]}\n\nQuestion: {request.message}"
            }
        ]
    )

    return {
        "answer": response.choices[0].message.content
    }