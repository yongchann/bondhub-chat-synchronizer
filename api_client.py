import requests
import json
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

LOGIN_ENDPOINT = "/api/v1/login"
CHAT_ENDPOINT = "/api/v1/chat/recent"
CHECK_ENDPOINT = "/api/v1/bond/price/status"

token = ""


def get(url, params):
    url = f"{API_BASE_URL}{url}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return result.get("data")
        else:
            logger.error(f"요청 실패: {str(result.get('errorCode'))}")   
            return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"GET 요청 실패: {str(e)}")
        return None
    
def post(url, params, payload):
    url = f"{API_BASE_URL}{url}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
        
    try:
        response = requests.post(url, headers=headers, params=params, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        if result.get("success"):
            return result.get("data")
        else:
            logger.error(f"요청 실패: {str(result.get('errorCode'))}")   
            return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"POST 요청 실패: {str(e)}")   
        return None
    

def login(username, password):
    payload = {
        "username": username,
        "password": password
    }
    
    result = post(LOGIN_ENDPOINT, params=None, payload=payload)
    print(result)
    
    global token
    token = result.get('token')
    if not token:
        return False
    return True

def append(chat_date, messages):
    payload = {
        "chatDate": chat_date,
        "chats": [
            {
                "senderName": msg.sender,
                "chatDateTime": msg.chat_date_time,
                "content": msg.content,
                "senderAddress": msg.sender_address
            } for msg in messages
        ]
    }
    return post(CHAT_ENDPOINT, params=None, payload=payload)

def check_status(chat_date):
    params = {
        "date": chat_date
    }
    count = get(CHECK_ENDPOINT, params=params)
    return count
    