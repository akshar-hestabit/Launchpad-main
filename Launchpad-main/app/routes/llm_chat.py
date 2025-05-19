from fastapi import FastAPI, APIRouter, HTTPException
import requests
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

# Hugging Face API settings
HF_API_URL = "https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = os.getenv("HF_API_TOKEN")  # Get your free token from huggingface.co/settings/tokens

@router.post("/chat")
async def llm_chat(req: ChatRequest):
    try:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        # Format the prompt for Mistral
        prompt = f"""<s>[INST] <<SYS>>
        You are a helpful assistant.
        <</SYS>>
        {req.message} [/INST]"""
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": 0.7
            }
        }
        
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for bad status codes
        
        reply = response.json()[0]["generated_text"]
        
        # Clean up the response (remove the prompt if present)
        if prompt in reply:
            reply = reply.split(prompt)[1].strip()
            
        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))