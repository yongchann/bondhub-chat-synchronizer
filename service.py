import logging
from api_client import apiClient

logger = logging.getLogger(__name__)

def login(username, password):
    if not username or not password:
        return False
    body = {
        "username": username,
        "password": password
    }
    try:
        result = apiClient.post('/api/v1/login', params=None, body=body)
        token = result.get('token')
        apiClient.set_token(token)
        return True
    except Exception as e:
        logger.error("login error", e)
        raise Exception("로그인 실패")

def get_bond_setting(base_date):
    try:
        params = {  
            'date': base_date
        }
        result = apiClient.get('/api/v1/bond/setting', params=params)
        logger.info("bond setting summary below")
        logger.info(f"- normal bond count: {result.get('countByStatus').get('OK')}")
        logger.info(f"- discarded bond count: {result.get('countByStatus').get('DISCARDED')}")
        for i in range(len(result.get('ktbBenchmarks'))):
            logger.info(f"- {i+1}th ktb benchmark: {result.get('ktbBenchmarks')[i]}")
            
        return result
    except Exception as e:
        logger.error(f"bond setting of {base_date} get error", e)
        raise Exception("채권 기준정보 조회 실패")

def append_log(base_date, file_name, offset, logs):
    body = {
        "baseDate": base_date,
        "fileName": file_name,
        "offset": offset,
        "logs": logs
    }
    try:    
        result = apiClient.post('/api/v1/chat/log', params=None, body=body)
        current_offset = result.get('currentOffset')
        return current_offset
    except Exception as e:
        logger.error(f"log synchronization failed - file: {file_name}, offset: {offset}, error: {str(e)}")
        raise Exception("로그 동기화 실패")