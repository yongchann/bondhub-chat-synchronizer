import re, os

# API 관련 설정
API_BASE_URL = 'http://3.36.90.23:8080'
LOGIN_ENDPOINT = "/api/v1/login"
CHAT_ENDPOINT = "/api/v1/chat/recent"

# 파일 처리 관련 설정
FILE_ENCODING = 'euc-kr'
FILE_PREFIX_FORMAT = "{prefix}_{date}"

# 정규표현식 패턴
CHAT_MESSAGE_PATTERN = re.compile(r'^([\w\s.가-힣女]+) \((\d{2}:\d{2}:\d{2})\) :\s*(.*?)$', re.UNICODE)
SENDER_ADDRESS_PATTERN = re.compile(r"\s*\([^)]*\)\s*$|\s*\[[^]]*\]\s*$|\s*\{[^}]*\}\s*$|\s*<[^>]*>\s*$|\s*▨[^▨]*▨\s*$|\s*【[^】]*】\s*$")

# 콘텐츠 정제를 위한 패턴
REPLACE_PATTERNS = {
    "[부국채영]368-9532": "([부국채영]368-9532])",
    "(DS투자증권 채권전략팀 02)709-2701)": "(DS투자증권 채권전략팀 02-709-2701)",
    "[흥국채금 6260-2460)": "[흥국채금 6260-2460]",
    "김성훈(부국)": "김성훈부국",
    "(한양증권 CMS 3770-5489": "(한양증권 CMS 3770-5489)"
}

# 모니터링 관련 설정
MONITOR_INTERVAL = 30000  # 30초