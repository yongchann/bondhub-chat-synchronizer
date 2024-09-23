import re, os

# API 관련 설정
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8080')
LOGIN_ENDPOINT = "/api/v1/login"
CHAT_ENDPOINT = "/api/v1/chat/recent"

# 파일 처리 관련 설정
FILE_ENCODING = 'euc-kr'
FILE_PREFIX_FORMAT = "{prefix}_{date}"

# 정규표현식 패턴
CHAT_MESSAGE_PATTERN = re.compile(r'^([A-Za-z\\.가-힣0-9 女]+) \((\d{2}:\d{2}:\d{2})\) :\s*(.*?)$')
SENDER_ADDRESS_PATTERN = re.compile(r"\s*\([^)]*\)\s*$|\s*\[[^]]*\]\s*$|\s*\{[^}]*\}\s*$|\s*<[^>]*>\s*$|\s*▨[^▨]*▨\s*$|\s*【[^】]*】\s*$")

# 콘텐츠 정제를 위한 패턴
REPLACE_PATTERNS = {
    r"\[부국채영\]368-9532": "([부국채영]368-9532])",
    r"\(DS투자증권 채권전략팀 02\)709-2701\)": "(DS투자증권 채권전략팀 02-709-2701)",
    r"\[흥국채금 6260-2460\)": "[흥국채금 6260-2460]",
    r"김성훈\(부국\)": "김성훈부국"
}

# 모니터링 관련 설정
MONITOR_INTERVAL = 30000  # 30초