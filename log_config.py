import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='app.log', log_level=logging.INFO):
    # �α� ���丮 ���� (�������� �ʴ� ���)
    log_dir = 'bondhub/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file_path = os.path.join(log_dir, log_file)

    # ��Ʈ �ΰ� ����
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # ���� �ڵ鷯 ���� (RotatingFileHandler ���)
    file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # �ڵ鷯 �߰�
    logger.addHandler(file_handler)

    return logger