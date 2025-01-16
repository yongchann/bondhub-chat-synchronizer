import requests
import json
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

class AuthenticationRequired(Exception):
    """인증이 필요한 경우 발생하는 예외"""
    pass

class APIClient:
    def __init__(self):
        self.token = ""

    def set_token(self, token):
        self.token = token

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    def build_url(self, endpoint):
        return f"{API_BASE_URL}{endpoint}"

    def request(self, method, url, params=None, payload=None):
        try:
            full_url = self.build_url(url)
            if method == 'GET':
                response = requests.get(full_url, headers=self.get_headers(), params=params)
            elif method == 'POST':
                response = requests.post(full_url, headers=self.get_headers(), params=params, data=json.dumps(payload))
            else:
                raise ValueError("Unsupported HTTP method")
            
            # 401 응답 처리
            if response.status_code == 401:
                logger.error("인증이 필요합니다. 다시 로그인해주세요.")
                raise AuthenticationRequired("인증이 필요합니다. 다시 로그인해주세요.")
            
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("data")
            else:
                logger.error(f"요청 실패: {str(result.get('errorCode'))}")
                raise Exception(f"요청 실패: {str(result.get('errorCode'))}")
        except requests.exceptions.RequestException as e:
            logger.error(f"{method} 요청 실패: {str(e)}")
            raise Exception(f"요청 실패: {str(e)}")
    