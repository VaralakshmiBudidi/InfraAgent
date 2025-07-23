import os
import json
import uuid
from typing import Dict, Optional, List
from openai import OpenAI
from app.models.deployment import ChatRequest, ChatResponse, ChatMessage, MessageType

class ConversationManager:
    def __init__(self):
        self.conversations = {}  # Store conversation history
    
    def get_conversation(self, conversation_id: str) -> List[ChatMessage]:
        return self.conversations.get(conversation_id, [])
    
    def add_message(self, conversation_id: str, message: ChatMessage):
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        self.conversations[conversation_id].append(message)
    
    def get_conversation_context(self, conversation_id: str) -> str:
        messages = self.get_conversation(conversation_id)
        context = ""
        for msg in messages[-5:]:  # Last 5 messages for context
            role = "User" if msg.type == MessageType.user else "AI"
            context += f"{role}: {msg.content}\n"
        return context

conversation_manager = ConversationManager()

def process_chat_message(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and generate an AI response.
    """
    # Generate conversation ID if not provided
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Add user message to conversation
    user_message = ChatMessage(
        type=MessageType.user,
        content=request.message
    )
    conversation_manager.add_message(conversation_id, user_message)
    
    # Get conversation context
    context = conversation_manager.get_conversation_context(conversation_id)
    
    # Generate AI response
    ai_response = generate_ai_response(request.message, context)
    
    # Add AI message to conversation
    ai_message = ChatMessage(
        type=MessageType.ai,
        content=ai_response["message"]
    )
    conversation_manager.add_message(conversation_id, ai_message)
    
    return ChatResponse(
        message=ai_response["message"],
        conversation_id=conversation_id,
        needs_input=ai_response.get("needs_input", False),
        input_type=ai_response.get("input_type"),
        suggestions=ai_response.get("suggestions")
    )

def generate_ai_response(user_message: str, context: str) -> Dict:
    """
    Generate an AI response using OpenAI.
    """
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            print("OPENAI_API_KEY not found in environment variables")
            return {
                "message": "Configuration error: OpenAI API key not found. Please contact support.",
                "needs_input": False
            }
        
        client = OpenAI(api_key=api_key)
        
        system_prompt = """
        You are InfraAgent, a friendly and helpful AI assistant. You can help with general questions, coding, and infrastructure deployment.

        Your capabilities:
        1. Answer general questions and have casual conversations
        2. Help with coding and technical questions
        3. Help users deploy applications to different environments (dev, qa, beta, prod)
        4. Provide helpful suggestions and examples
        5. Be conversational, friendly, and engaging like ChatGPT

        When users want to deploy something:
        - If they don't provide a repository URL, ask for it naturally
        - If they don't specify an environment, ask for it conversationally
        - Provide helpful examples
        - Be conversational and helpful

        Available environments: dev, qa, beta, prod

        IMPORTANT: Be conversational and friendly. Don't just ask for information - engage in natural conversation. If someone says "hi" or asks general questions, respond naturally like ChatGPT would.
        """
        
        # Create the conversation context
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation context if available
        if context.strip():
            messages.append({"role": "system", "content": f"Previous conversation:\n{context}"})
        
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_message = response.choices[0].message.content.strip()
        
        # Only analyze for deployment-specific needs, not general chat
        needs_info = analyze_needs_information(user_message, ai_message)
        
        return {
            "message": ai_message,
            "needs_input": needs_info["needs_input"],
            "input_type": needs_info["input_type"],
            "suggestions": needs_info["suggestions"]
        }
        
    except Exception as e:
        print(f"Error in AI response generation: {str(e)}")
        return {
            "message": "I'm having trouble processing your request right now. Please try again or contact support.",
            "needs_input": False
        }

def analyze_needs_information(user_message: str, ai_response: str) -> Dict:
    """
    Analyze if the AI response indicates we need more information from the user.
    Only trigger for explicit deployment requests.
    """
    user_lower = user_message.lower()
    ai_lower = ai_response.lower()
    
    needs_input = False
    input_type = None
    suggestions = []
    
    # Only analyze if user explicitly mentions deployment
    if any(phrase in user_lower for phrase in ["deploy", "deployment", "deploy my"]):
        # Check if AI is asking for repository URL
        if any(phrase in ai_lower for phrase in ["repository", "github", "repo", "url"]):
            needs_input = True
            input_type = "repo_url"
            suggestions = [
                "https://github.com/username/my-app",
                "https://github.com/VaralakshmiBudidi/sample-app"
            ]
        
        # Check if AI is asking for environment
        elif any(phrase in ai_lower for phrase in ["environment", "where", "which environment"]):
            needs_input = True
            input_type = "environment"
            suggestions = ["dev", "qa", "beta", "prod"]
        
        # Check if repository URL is missing
        elif "github.com" not in user_lower:
            needs_input = True
            input_type = "repo_url"
            suggestions = [
                "https://github.com/username/my-app",
                "https://github.com/VaralakshmiBudidi/sample-app"
            ]
        
        # Check if environment is missing
        elif not any(env in user_lower for env in ["dev", "qa", "beta", "prod", "production", "staging"]):
            needs_input = True
            input_type = "environment"
            suggestions = ["dev", "qa", "beta", "prod"]
    
    return {
        "needs_input": needs_input,
        "input_type": input_type,
        "suggestions": suggestions
    } 