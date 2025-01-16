from api_client import APIClient
import logging

logger = logging.getLogger(__name__)

api_client = APIClient()

def authenticate(username, password):
    """사용자 인증 및 로그인 처리"""
    if not (username and password):
        return False, "아이디와 패스워드를 입력해주세요."
    
    try:
        response = api_client.request('POST', "/api/v1/login", 
                                    payload={"username": username, "password": password})
        
        if not response or not response.get('token'):
            return False, "로그인에 실패했습니다. 아이디와 패스워드를 확인해주세요."
            
        api_client.set_token(response['token'])
        return True, "로그인에 성공했습니다."
        
    except Exception as e:
        logger.error(f"로그인 중 오류 발생: {str(e)}")
        return False, "로그인 처리 중 오류가 발생했습니다."

def validate_monitoring_date(selected_date):
    """모니터링 날짜 유효성 검증"""
    try:
        params = {
            "date": selected_date
        }
        result = api_client.request('GET', "/api/v1/bond/price/status", params=params)
        
        if result is None or result < 1:
            logger.info(f"{selected_date} 일자의 채권 가격을 먼저 업로드 해주세요.")
            return False
        return True
        
    except Exception as e:
        logger.error(f"모니터링 날짜 검증 중 오류 발생: {str(e)}")
        return False

def append(chat_date, messages):
    """채팅 메시지 추가"""
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
    return api_client.request('POST', "/api/v1/chat/recent", payload=payload)

def append_log(chat_date, file_name, offset, line_count, log):
    """로그 추가"""
    payload = {
        "baseDate": chat_date,
        "fileName": file_name,
        "offset": offset,
        "lineCount": line_count,
        "log": log
    }
    response = api_client.request('POST', "/api/v1/chat/log", payload=payload)
    if response is None:
        raise Exception("Failed to send log to server.")
    return response