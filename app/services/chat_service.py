from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.models.chat import ChatSession
from app.schemas.chat import ChatMessage, ChatResponse
from datetime import datetime
import uuid
import json

def create_chat_session(db: Session, user_id: Optional[int] = None) -> ChatSession:
    """Create a new chat session"""
    session_id = str(uuid.uuid4())
    db_session = ChatSession(
        user_id=user_id,
        session_id=session_id,
        messages=[],
        chat_count=0
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: str, user_id: Optional[int] = None) -> Optional[ChatSession]:
    """Get chat session by session_id"""
    query = db.query(ChatSession).filter(ChatSession.session_id == session_id)
    if user_id:
        query = query.filter(ChatSession.user_id == user_id)
    return query.first()

def send_chat_message(db: Session, message: ChatMessage, user_id: Optional[int] = None) -> ChatResponse:
    """Send a chat message and get AI response"""
    # Get or create session
    session = None
    if message.session_id:
        session = get_chat_session(db, message.session_id, user_id)
    
    if not session:
        session = create_chat_session(db, user_id)
    
    # Check chat limits
    if session.chat_count >= 100:
        raise Exception("Chat limit reached for this session")
    
    # Add user message to session
    user_message = {
        "role": "user",
        "content": message.message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if session.messages is None:
        session.messages = []
    session.messages.append(user_message)
    
    # Generate AI response
    ai_response = chat_ai_stub(message.message, session.messages)
    
    # Add AI response to session
    assistant_message = {
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.utcnow().isoformat()
    }
    session.messages.append(assistant_message)
    
    # Update session
    session.chat_count += 1
    db.commit()
    
    return ChatResponse(
        response=ai_response,
        session_id=session.session_id,
        timestamp=datetime.utcnow(),
        mode="ai"
    )

def get_chat_history(db: Session, session_id: Optional[str] = None, user_id: Optional[int] = None) -> List[dict]:
    """Get chat history for a session"""
    if session_id:
        session = get_chat_session(db, session_id, user_id)
        if session and session.messages:
            return session.messages
    else:
        # Get all sessions for user
        sessions = get_user_chat_sessions(db, user_id)
        all_messages = []
        for session in sessions:
            if session.messages:
                all_messages.extend(session.messages)
        return all_messages
    
    return []

def get_user_chat_sessions(db: Session, user_id: int) -> List[ChatSession]:
    """Get all chat sessions for a user"""
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def delete_chat_session(db: Session, session_id: Optional[str] = None, user_id: Optional[int] = None) -> bool:
    """Delete chat session"""
    if session_id:
        session = get_chat_session(db, session_id, user_id)
        if session:
            db.delete(session)
            db.commit()
            return True
    else:
        # Delete all sessions for user
        sessions = get_user_chat_sessions(db, user_id)
        for session in sessions:
            db.delete(session)
        db.commit()
        return True
    
    return False

def chat_ai_stub(message: str, history: List[dict]) -> str:
    """Enhanced AI chat function with better responses"""
    try:
        # Try to use the LLM model from chat API
        from app.api.chat import load_tinyllama_model
        
        model = load_tinyllama_model()
        if model:
            # Prepare context from history
            context = ""
            for msg in history[-5:]:  # Last 5 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                context += f"{role.capitalize()}: {content}\n"
            
            # Create a comprehensive prompt for Vastu consultation
            system_prompt = """You are an expert Vastu Shastra consultant with deep knowledge of ancient Indian architecture principles. 
            Provide helpful, practical advice about:
            - Room placement and directions
            - Energy flow and balance
            - Color and material recommendations
            - Remedies for Vastu defects
            - Modern applications of ancient principles
            
            Keep responses concise, practical, and helpful. Always relate advice to specific Vastu principles."""
            
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\nUser: {message}\nAssistant:"
            
            # Generate response
            response = model(
                full_prompt,
                max_new_tokens=150,
                temperature=0.7,
                stop=["User:", "\n\n", "Context:"]
            )
            
            cleaned_response = response.strip()
            if cleaned_response and len(cleaned_response) > 10:
                return cleaned_response
    
    except Exception as e:
        print(f"Error in AI chat: {e}")
    
    # Enhanced fallback responses
    message_lower = message.lower()
    
    vastu_responses = {
        "hello": "Hello! I'm your Vastu consultant. How can I help you create a harmonious living space today?",
        "hi": "Hi there! I'm here to help with Vastu Shastra principles. What would you like to know?",
        "help": "I can assist you with: \n• Room placement and directions\n• Energy flow optimization\n• Color and material recommendations\n• Vastu remedies\n• Floor plan analysis\n\nWhat specific area interests you?",
        "kitchen": "For kitchen Vastu: Place your kitchen in the Southeast direction. The cooking stove should face East. Avoid placing it directly opposite the main entrance. Would you like specific tips for your kitchen layout?",
        "bedroom": "For bedroom Vastu: The master bedroom should be in the Southwest direction. Sleep with your head towards South or East. Avoid mirrors facing the bed. Need more specific bedroom advice?",
        "entrance": "For entrance Vastu: The main entrance should ideally face North, East, or Northeast. Keep it well-lit and clutter-free. Place a threshold (threshold) at the entrance. What's your current entrance direction?",
        "toilet": "For toilet Vastu: Place toilets in the Northwest or Southeast corners. Avoid Northeast direction. Keep the door closed and ensure good ventilation. Any specific toilet placement concerns?",
        "colors": "Vastu colors: Use light, soothing colors. East - light blue/green, South - red/orange, West - white/yellow, North - blue/green. Avoid dark colors in Northeast. Which room are you planning to color?",
        "direction": "Vastu directions are crucial: North (wealth), East (health), South (fame), West (gains), Northeast (spirituality), Southeast (fire), Southwest (stability), Northwest (air). Which direction concerns you?",
        "remedies": "Common Vastu remedies: Use mirrors to redirect energy, place plants for positive vibes, use crystals for energy enhancement, ensure proper lighting, and maintain cleanliness. What specific issue needs a remedy?"
    }
    
    # Find matching response
    for key, response in vastu_responses.items():
        if key in message_lower:
            return response
    
    # Check for room-specific queries
    if any(word in message_lower for word in ['living room', 'hall', 'drawing room']):
        return "For living room Vastu: Place it in the North or East direction. Keep it clutter-free and well-lit. Use light colors and place the main furniture along the South or West walls. Any specific living room questions?"
    
    if any(word in message_lower for word in ['study', 'office', 'work']):
        return "For study/office Vastu: Face East or North while working. Place the desk in the Southwest corner. Keep the area clutter-free and well-lit. Avoid sitting with your back to the door. Need specific workspace advice?"
    
    # Default response with helpful suggestions
    return f"Thank you for your question: '{message}'. I'm here to help with Vastu principles! You can ask me about:\n• Room placement and directions\n• Energy flow and balance\n• Color recommendations\n• Vastu remedies\n• Specific room layouts\n\nWhat aspect of Vastu interests you most?"
