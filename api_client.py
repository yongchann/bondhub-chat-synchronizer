import requests
import json
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)
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
    
    result = post("/api/v1/login", params=None, payload=payload)
    global token
    
    token = result.get('token')
    if not token:
        return False
    return True

def check_status(chat_date):
    params = {
        "date": chat_date
    }
    count = get("/api/v1/bond/price/status", params=params)
    return count
    
def get_offset_map(chat_date):
    params = {
        "date": chat_date
    }
    from collections import defaultdict
    offsets = get("/api/v1/chat/offset", params=params)
    offset_map = defaultdict(int)
    for data in offsets.get('offsets'):
        fileName = data.get('fileName')
        offset = data.get('offset')
        offset_map[fileName] = offset
    return offset_map
    
def append_chat_log(chat_date, chat_log_infos):
    payload = {
        "chatDate": chat_date,
        "chatLogs": chat_log_infos
        
    }
    post("/api/v1/chat/recent", params=None, payload=payload)
    