from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import openai
from preorder_chatbot.main import PreorderAgent
from report_chatbot.main import EmergencyReportingBot

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


class ConversationItem(BaseModel):
    role: str
    content: str


class ReportRequest(BaseModel):
    message: Optional[str] = None
    image_data: Optional[str] = None  # Expecting base64 encoded string
    conversation_history: List[ConversationItem] = Field(default_factory=list)


class ReportResponse(BaseModel):
    response: str
    conversation: List[ConversationItem]
    report_saved: bool
    report_path: Optional[str]


# --- Instantiate the Chatbot Agent ---
# This is created once when the server starts
preorder_chatbot = PreorderAgent()
report_chatbot = EmergencyReportingBot()

# --- API Endpoint ---


@app.post("/pchat", response_model=ChatResponse)
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
        result = preorder_chatbot.process_order(
            query=request.query, memory_input=memory_dict_list
        )
        # No need to manually create ChatResponse, FastAPI handles it via response_model
        return result
    except Exception as e:
        print(f"Error processing request: {e}")  # Log the exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.post("/rchat", response_model=ReportResponse)
async def handle_emergency_report(request: ReportRequest):
    """
    Receives user message and optional image (base64) for emergency reporting.
    """
    if not request.message and not request.image_data:
        raise HTTPException(status_code=400, detail="Request must contain at least a message or image_data.")

    # Convert Pydantic models back to simple dicts for the bot function if needed
    history_list = [item.model_dump() for item in request.conversation_history]

    try:
        # Call the bot's processing method
        result = report_chatbot.process_message(
            message=request.message,
            image_data=request.image_data,
            conversation_history=history_list
        )

        # Convert result conversation back to Pydantic model for validation (optional but good practice)
        # If the bot returns the correct structure, direct return is fine with response_model
        # result["conversation"] = [ConversationItem(**item) for item in result.get("conversation", [])]

        return result

    except Exception as e:
        print(f"Error processing request: {e}")  # Log the exception
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.get("/")
async def root():
    return {"message": "Chatbot API is running. Use the /chat endpoint to interact."}
