# File: main.py (root directory)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import datetime
import os

# Import existing components
from chatbot.main import PreorderAgent
from chatbot.main import FansAssistant
from roadmap.roadmap_generator import RoadmapGenerator
from audio_description.processor import AudioDescriptionProcessor

# Import new emergency chatbot components
from report_chatbot.main import EmergencyReportingBot

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
preorder_bot = PreorderAgent()
fans_bot = FansAssistant()
roadmap_gen = RoadmapGenerator()
audio_processor = AudioDescriptionProcessor()
emergency_bot = EmergencyReportingBot()


# Existing endpoints
@app.post("/preorder/chat")
async def handle_preorder(request: dict):
    response = PreorderAgent.process_order(request["query"], request["memory"])
    return response


@app.post("/roadmap/generate")
async def generate_roadmap(request: dict):
    user_inputs = process_flutter_input(request["data"])
    image = roadmap_gen(user_input)  # input: json file, output: image
    return image


@app.post("/audio/process")
async def process_audio(request: dict):
    return audio_processor.handle_flutter_upload(request["video"])


# New endpoint for emergency reporting chatbot
@app.post("/emergency/chat")
async def handle_emergency_report(request: dict):
    """
    Process emergency report messages and return AI response
    Request format:
    {
        "message": "User message text",
        "image_data": "Optional base64 encoded image",
        "conversation_history": [{"role": "user/assistant", "content": "message"}]
    }
    """
    try:
        response = emergency_bot.process_message(
            message=request.get("message", ""),
            image_data=request.get("image_data"),
            conversation_history=request.get("conversation_history", []),
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing emergency report: {str(e)}"
        )


class DeleteChatHistoryRequest(BaseModel):
    conversation_id: Optional[str] = None  # If None, clear all conversations

@app.post("/chat/delete_history")
async def delete_chat_history(request: DeleteChatHistoryRequest):
    """
    Deletes chat history for a specific conversation or all conversations.
    
    If conversation_id is provided, only that conversation's history will be deleted.
    If conversation_id is None, all chat histories will be deleted.
    
    Returns:
        dict: Status message indicating success or failure
    """
    try:
        # For the PreorderAgent specifically
        if request.conversation_id:
            # If you're tracking conversations by ID in the future
            # This would need to be adapted to your conversation storage mechanism
            if hasattr(preorder_bot, 'conversations') and request.conversation_id in preorder_bot.conversations:
                preorder_bot.conversations[request.conversation_id].memory = ConversationMemory()
                return {"status": "success", "message": f"Chat history for conversation {request.conversation_id} cleared successfully"}
            else:
                return {"status": "error", "message": f"Conversation {request.conversation_id} not found"}
        else:
            # Clear the default memory
            preorder_bot.memory = ConversationMemory()
            
            # Also clear emergency_bot memory if it exists
            if hasattr(emergency_bot, 'memory'):
                emergency_bot.memory = ConversationMemory()
            
            return {"status": "success", "message": "All chat histories cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error deleting chat history: {str(e)}"
        )