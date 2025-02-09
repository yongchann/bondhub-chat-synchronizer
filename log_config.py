import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(log_file='bondhub.log', log_level=logging.INFO):
    log_dir = 'bondhub/log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    today = datetime.now().strftime('%Y%m%d')
    log_file_name = f'bondhub_{today}.log'
    log_file_path = os.path.join(log_dir, log_file_name)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    file_handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=50*1024*1024,
        backupCount=3
    )
    file_formatter = logging.Formatter('%(asctime)s [%(filename)15s:%(lineno)3d] [%(levelname)5s] %(message)s')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    return logger