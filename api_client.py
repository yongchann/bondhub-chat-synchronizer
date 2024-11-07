import requests
import json
from datetime import datetime
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

LOGIN_ENDPOINT = "/api/v1/login"
CHAT_ENDPOINT = "/api/v1/chat/recent"

def login(username, password):
    url = f"{API_BASE_URL}{LOGIN_ENDPOINT}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json().get("data").get("token")
    except requests.exceptions.RequestException as e:
        logger.error(f"로그인 실패: {str(e)}")
        return None

def send_messages_to_api(messages, token):
    url = f"{API_BASE_URL}{CHAT_ENDPOINT}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    chat_date = datetime.now().strftime("%Y-%m-%d")
    recent_chats = [
        {
            "senderName": msg.sender,
            "chatDateTime": msg.chat_date_time,
            "content": msg.content,
            "senderAddress": msg.sender_address
        } for msg in messages
    ]
    
    payload = {
        "chatDate": chat_date,
        "chats": recent_chats
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logger.info(f"{len(messages)}개의 메시지를 성공적으로 전송했습니다.")
    except requests.exceptions.RequestException as e:
        logger.error(f"API 전송 실패: {str(e)}")
        raise
