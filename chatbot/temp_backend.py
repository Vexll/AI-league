from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import openai
from main import PreorderAgent

# API_key
app = FastAPI()

# --- Pydantic Models for Request/Response ---


class MemoryItem(BaseModel):
    user: str
    bot: str


class ChatRequest(BaseModel):
    query: str
    memory_input: List[MemoryItem] = Field(
        default_factory=list
    )  # Use default_factory for mutable default


class ChatResponse(BaseModel):
    response: str
    memory: List[MemoryItem]
    category: str


# --- Instantiate the Chatbot Agent ---
# This is created once when the server starts
chatbot_agent = PreorderAgent()

# --- API Endpoint ---


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Process a user query using the chatbot.

    - **query**: The user's message.
    - **memory_input**: The conversation history (list of user/bot interactions).
                       Send an empty list `[]` for the start of a conversation.
    """
    print(f"Received query: {request.query}")  # Log received query
    print(f"Received memory length: {len(request.memory_input)}")  # Log memory length

    # Convert Pydantic MemoryItem objects to simple dicts for the chatbot logic
    memory_dict_list = [item.model_dump() for item in request.memory_input]

    try:
        result = chatbot_agent.process_order(
            query=request.query, memory_input=memory_dict_list
        )
        # No need to manually create ChatResponse, FastAPI handles it via response_model
        return result
    except Exception as e:
        print(f"Error processing request: {e}")  # Log the exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/")
async def root():
    return {"message": "Chatbot API is running. Use the /chat endpoint to interact."}
