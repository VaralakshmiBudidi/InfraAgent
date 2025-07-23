from fastapi import APIRouter, HTTPException
from app.models.deployment import ChatRequest, ChatResponse
from app.services.chat_service import process_chat_message

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI assistant for deployment help.
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=400,
                detail="Please provide a message to chat with the AI."
            )
        
        response = process_chat_message(request)
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        ) 