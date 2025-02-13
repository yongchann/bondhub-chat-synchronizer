import requests
import json
import logging
from config import API_BASE_URL

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.token = ""

    def set_token(self, token):
        self.token = token

    def get(self, url, params=None):
        return self._request('GET', url, params=params)

    def post(self, url, params=None, body=None): 
        return self._request('POST', url, params=params, body=body)

    def _request(self, method, url, params=None, body=None):
        try:
            if method == 'GET':
                headers = {"Content-Type": "application/json","Authorization": f"Bearer {self.token}"}
                response = requests.get(f"{API_BASE_URL}{url}", verify=False, headers=headers, params=params)
            elif method == 'POST':
                headers = {"Content-Type": "application/json","Authorization": f"Bearer {self.token}"}
                response = requests.post(f"{API_BASE_URL}{url}", verify=False, headers=headers, params=params, data=json.dumps(body))
            else:
                raise ValueError(f"Invalid method: {method}")
            self.handle_response_error(response)
            return response.json().get("data")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"{method} 요청 실패: {str(e)}")
            raise Exception(f"{method} 요청 실패: {str(e)}")

    def handle_response_error(self, response):
        if response.status_code == 400:
            logger.error("잘못된 요청입니다.")
            raise Exception("잘못된 요청입니다.")
        elif response.status_code == 401:
            logger.error("인증이 필요합니다. 다시 로그인해주세요.")
            raise Exception("인증이 필요합니다. 다시 로그인해주세요.")
        elif response.status_code == 403:
            logger.error("권한이 없습니다.")
            raise Exception("권한이 없습니다.")
        elif response.status_code == 404:
            logger.error("요청한 리소스가 존재하지 않습니다.")
            raise Exception("요청한 리소스가 존재하지 않습니다.")
        elif response.status_code == 405:
            logger.error("요청한 메서드가 허용되지 않습니다.")
            raise Exception("요청한 메서드가 허용되지 않습니다.")
        elif response.status_code == 429:
            logger.error("요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
            raise Exception("요청이 너무 많습니다. 잠시 후 다시 시도해주세요.")
        elif response.status_code == 500:
            logger.error("서버 오류가 발생했습니다.")
            raise Exception("서버 오류가 발생했습니다.")

apiClient = APIClient()