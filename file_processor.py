import os
from datetime import datetime
from unicodedata import normalize
import logging
from chat_processor import process_chat_lines

logger = logging.getLogger(__name__)

# 파일 처리 관련 설정
FILE_ENCODING = 'euc-kr'
FILE_PREFIX_FORMAT = "{prefix}_{date}"

def read_file_content(filename):
    try:
        with open(filename, 'r', encoding=FILE_ENCODING, errors='ignore') as file:
            return file.readlines()
    except Exception as e:
        logger.error(f"파일 읽기 오류 ({filename}): {str(e)}")
        return []

def process_file(filename, prefix, current_offset):
    lines = read_file_content(filename)
    new_lines = lines[current_offset:]
    new_messages = process_chat_lines(new_lines)
    new_offset = len(lines)
    return new_messages, new_offset

def process_files(offsets):
    today = datetime.now().strftime("%Y%m%d")
    file_prefixes = [
        normalize('NFC', FILE_PREFIX_FORMAT.format(prefix=prefix, date=today))
        for prefix in ["채권_블커본드", "채권_레드본드", "채권_막무가내"]
    ]
    
    all_new_messages = {}
    
    for filename in os.listdir('.'):
        normalized_filename = normalize('NFC', filename)
        for prefix in file_prefixes:
            if normalized_filename.startswith(prefix) and normalized_filename.endswith('.txt'):
                current_offset = offsets.get(prefix, 0)
                new_messages, new_offset = process_file(filename, prefix, current_offset)
                if new_messages:
                    all_new_messages[normalized_filename] = new_messages
                    offsets[prefix] = new_offset
                    logger.info(f"{normalized_filename}에서 {len(new_messages)}개의 새 메시지를 발견했습니다.")
    
    return all_new_messages
