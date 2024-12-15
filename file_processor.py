import os
from unicodedata import normalize
import logging
logger = logging.getLogger(__name__)

def read_file_content(filename):
    try:
        with open(filename, 'r', encoding='euc-kr', errors='ignore') as file:
            return file.readlines()
    except Exception as e:
        logger.error(f"파일 읽기 오류 ({filename}): {str(e)}")
        return []

def find_target_file_names(prefixes):
    target_files = []
    for filename in os.listdir('.'):
        normalized_filename = normalize('NFC', filename)
        for prefix in prefixes:
            if normalized_filename.startswith(prefix) and normalized_filename.endswith('.txt'):
                target_files.append(filename)
    return target_files

def get_new_chat_logs(file_name, offset):
    lines = read_file_content(file_name)
    return lines[offset:]