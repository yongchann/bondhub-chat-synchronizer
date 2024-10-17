import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='app.log', log_level=logging.INFO):
    # 로그 디렉토리 생성 (존재하지 않는 경우)
    log_dir = 'bondhub/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file_path = os.path.join(log_dir, log_file)

    # 루트 로거 설정
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # 파일 핸들러 설정 (RotatingFileHandler 사용)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)

    return logger