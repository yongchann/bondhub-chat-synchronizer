import os
import re
from datetime import datetime
from unicodedata import normalize
import logging
from chat_message import ChatMessage
from config import REPLACE_PATTERNS, FILE_ENCODING, CHAT_MESSAGE_PATTERN, SENDER_ADDRESS_PATTERN, FILE_PREFIX_FORMAT

logger = logging.getLogger(__name__)

from datetime import datetime
from zoneinfo import ZoneInfo
seoul_now = datetime.now(ZoneInfo("Asia/Seoul"))
formatted_date = seoul_now.strftime("%Y-%m-%d")

def read_file_content(filename):
    try:
        with open(filename, 'r', encoding=FILE_ENCODING, errors='ignore') as file:
            return file.readlines()
    except Exception as e:
        logger.error(f"파일 읽기 오류 ({filename}): {str(e)}")
        return []

def parse_chat_message(line):
    match = CHAT_MESSAGE_PATTERN.match(line)
    if match:
        sender, send_time, content = match.groups()
        return ChatMessage(sender, formatted_date+'T'+send_time, content, "")
    return None

def clean_content(content):
    for pattern, replacement in REPLACE_PATTERNS.items():
        content = content.replace(pattern, replacement)
    return content.strip()

def extract_sender_address(content):
    address_match = SENDER_ADDRESS_PATTERN.search(content)
    if address_match:
        sender_address = address_match.group().strip()
        content = SENDER_ADDRESS_PATTERN.sub("", content).strip()
        return content, sender_address
    return content, ""

def process_chat_lines(lines):
    chat_messages = []
    current_message = None

    for line in lines:
        line = line.strip()
        new_message = parse_chat_message(line)
        if new_message:
            if current_message:
                current_message.content = clean_content(current_message.content)
                current_message.content, current_message.sender_address = extract_sender_address(current_message.content)
                chat_messages.append(current_message)
            current_message = new_message
        elif current_message:
            current_message.content += " " + line
    
    if current_message:
        current_message.content = clean_content(current_message.content)
        current_message.content, current_message.sender_address = extract_sender_address(current_message.content)
        chat_messages.append(current_message)
    
    return chat_messages

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
