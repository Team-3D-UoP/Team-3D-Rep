"""
Database Chat Manager
Handles all chat-related database operations for the support chat system
"""

from datetime import datetime
from models import db, ChatMessage

# In-memory storage for chat sessions (for MVP)
# In production, this should be in a database
CHAT_SESSIONS = {}
CHAT_COUNTER = 0


def create_or_get_chat_session(user_id, username, email):
    """Create a new chat session or return existing one for a user"""
    global CHAT_COUNTER

    # Check if session exists
    for chat_id, session in CHAT_SESSIONS.items():
        if session.get('user_id') == user_id:
            return chat_id

    # Create new session
    CHAT_COUNTER += 1
    chat_id = CHAT_COUNTER

    CHAT_SESSIONS[chat_id] = {
        'chat_id': chat_id,
        'user_id': user_id,
        'username': username,
        'email': email,
        'created_at': datetime.utcnow().isoformat(),
        'status': 'active',
        'messages': []
    }

    return chat_id


def send_message(chat_id, sender_id, sender_type, message):
    """Send a message in a chat session"""
    if chat_id not in CHAT_SESSIONS:
        raise ValueError(f"Chat session {chat_id} not found")

    message_data = {
        'message_id': len(CHAT_SESSIONS[chat_id]['messages']) + 1,
        'sender_id': sender_id,
        'sender_type': sender_type,  # 'user' or 'support'
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'read': False
    }

    CHAT_SESSIONS[chat_id]['messages'].append(message_data)

    return message_data['message_id']


def get_chat_messages(chat_id):
    """Get all messages from a chat session"""
    if chat_id not in CHAT_SESSIONS:
        return []

    return CHAT_SESSIONS[chat_id].get('messages', [])


def get_all_chat_sessions():
    """Get all chat sessions for the support dashboard"""
    sessions = []
    for chat_id, session in CHAT_SESSIONS.items():
        # Get last message preview
        messages = session.get('messages', [])
        last_message = messages[-1] if messages else None

        sessions.append({
            'chat_id': chat_id,
            'user_id': session['user_id'],
            'username': session['username'],
            'email': session['email'],
            'status': session['status'],
            'created_at': session['created_at'],
            'last_message': last_message.get('message') if last_message else 'No messages',
            'last_message_time': last_message.get('timestamp') if last_message else None,
            'message_count': len(messages),
            'unread_count': len([m for m in messages if not m.get('read') and m.get('sender_type') == 'user'])
        })

    # Sort by last message time (most recent first)
    sessions.sort(key=lambda x: x['last_message_time'] or '', reverse=True)

    return sessions


def get_chat_session_info(chat_id):
    """Get information about a specific chat session"""
    if chat_id not in CHAT_SESSIONS:
        return None

    session = CHAT_SESSIONS[chat_id]
    messages = session.get('messages', [])

    return {
        'chat_id': chat_id,
        'user_id': session['user_id'],
        'username': session['username'],
        'email': session['email'],
        'status': session['status'],
        'created_at': session['created_at'],
        'message_count': len(messages),
        'last_message': messages[-1] if messages else None
    }


def mark_messages_as_read(chat_id):
    """Mark all messages in a chat as read"""
    if chat_id not in CHAT_SESSIONS:
        return False

    for message in CHAT_SESSIONS[chat_id]['messages']:
        message['read'] = True

    return True


def close_chat_session(chat_id):
    """Close a chat session"""
    if chat_id not in CHAT_SESSIONS:
        raise ValueError(f"Chat session {chat_id} not found")

    CHAT_SESSIONS[chat_id]['status'] = 'closed'
    CHAT_SESSIONS[chat_id]['closed_at'] = datetime.utcnow().isoformat()

    return True


def get_chat_messages_api(chat_id):
    """Get messages for API endpoint"""
    return get_chat_messages(chat_id)


def save_chat_message(user_id, message):
    """Save a chat message (legacy function)"""
    # Try to find or create session for user
    for chat_id, session in CHAT_SESSIONS.items():
        if session.get('user_id') == user_id:
            send_message(chat_id, user_id, 'user', message)
            return True

    return False


def get_chat_history(user_id):
    """Get chat history for a user (legacy function)"""
    for chat_id, session in CHAT_SESSIONS.items():
        if session.get('user_id') == user_id:
            return get_chat_messages(chat_id)

    return []
