import os
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
from typing import Optional
import openai
from preorder_chatbot.main import PreorderAgent, AudioProcessor
from report_chatbot.main import EmergencyReportingBot
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# --- Instantiate the Chatbot Agent ---
# This is created once when the server starts
preorder_chatbot = PreorderAgent()
report_chatbot = EmergencyReportingBot()
audio_processor = AudioProcessor()

# Start FastAPI
app = FastAPI()

# --- Pydantic Models for Request/Response ---

class ChatRequest(BaseModel):
    query: str
    image_data: Optional[str] = None  # Optional base64 encoded image

class ChatResponse(BaseModel):
    response: str

# Store conversation memory for each chatbot
preorder_memory = []
report_memory = []

# --- API Endpoint ---
@app.post("/pchat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Process a user query using the preorder chatbot.

    - **query**: The user's message.
    - **image_data**: Optional base64 encoded image.
    """
    global preorder_memory
    
    try:
        result = preorder_chatbot.process_order(
            query=request.query, 
            memory_input=preorder_memory
        )
        
        # Update global memory with new conversation
        preorder_memory = result["memory"]
        
        # Return only the response
        return {"response": result["response"]}
    
    except Exception as e:
        print(f"Error processing request: {e}")  # Log the exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/rchat", response_model=ChatResponse)
async def handle_emergency_report(request: ChatRequest):
    """
    Process a query using the emergency reporting chatbot.
    
    - **query**: The user's message.
    - **image_data**: Optional base64 encoded image.
    """
    global report_memory
    
    try:
        # Call the bot's processing method
        result = report_chatbot.process_message(
            message=request.query,
            image_data=request.image_data,
            conversation_history=report_memory
        )
        
        # Update memory
        report_memory = result["conversation"]
        
        # Return only the response
        return {"response": result["response"]}
        
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.post("/audio-chat", response_model=ChatResponse)
async def handle_audio_chat(file: UploadFile = File(...)):
    """
    Process an audio file by:
    1. Converting speech to text
    2. Sending the transcribed text to the preorder chatbot
    3. Returning the chatbot's response
    
    - **audio**: An audio file containing speech
    """
    global preorder_memory
    
    try:
        # Convert speech to text
        print(f'received {file.filename}')
        transcribed_text = audio_processor.transcribe_audio(file.file)
        
        print(f"Transcribed text: {transcribed_text[:20]}")
        
        # Process the transcribed text with the preorder chatbot
        result = preorder_chatbot.process_order(
            query=transcribed_text, 
            memory_input=preorder_memory
        )
        
        # Update global memory with new conversation
        preorder_memory = result["memory"]
        
        # Return only the response
        return {"response": result["response"]}
    
    except Exception as e:
        print(f"Error processing audio request: {e}")  # Log the exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")



@app.post("/clear")
async def clear_memory():
    """Clear the chatbot's memory"""
    global preorder_memory
    global report_memory
    preorder_memory = []
    report_memory = []
    return {"message": "chatbot memory cleared successfully"}
