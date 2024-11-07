import re
from chat import Chat
from datetime import datetime, timezone, timedelta
from operator import attrgetter
from itertools import groupby

utc_time = datetime.now(timezone.utc)
seoul_time = utc_time + timedelta(hours=9)
formatted_date = seoul_time.strftime("%Y-%m-%d")

CHAT_MESSAGE_PATTERN = re.compile(r'^([\w\s.가-힣()\u4e00-\u9fff]+) \((\d{2}:\d{2}:\d{2})\) :\s*(.*?)(?:\s*((?:\([^()]*\)|\[[^[\]]*\]|\{[^{}]*\}|<[^<>]*>|▨[^▨]*▨|【[^【】]*】)))?\s*$', re.UNICODE)
NEW_CHAT_PATTERN = re.compile(r'\((\d{2}:\d{2}:\d{2})\)')
YIELD_PATTERN = re.compile(r'민\s*(?:평\s*)?[:~]?\s*(\d\.\d{2,3})(?:\s*[,/]|[)])?')

REPLACE_PATTERNS = {
    "[부국채영]368-9532": "[부국채영 368-9532]",
    "(DS투자증권 채권전략팀 02)709-2701)": "(DS투자증권 채권전략팀 02-709-2701)",
    "[흥국채금 6260-2460)": "[흥국채금 6260-2460]",
    "(한양증권 CMS 3770-5489": "(한양증권 CMS 3770-5489)",
    "[케이프 인수금융팀 02-6923-7656": "[케이프 인수금융팀 02-6923-7656]"
}


def process_duplication(chats):
    sorted_chats = sorted(chats, key=attrgetter('content', 'sender', 'chat_date_time'))
    
    grouped = groupby(sorted_chats, key=attrgetter('content', 'sender'))
    
    return [max(group, key=attrgetter('chat_date_time')) for _, group in grouped]

def extract_bond_yield(content):
    matches = YIELD_PATTERN.findall(content)
    if len(matches) > 0:
        return matches[0]
    return ''
        
def parse_chat_message(line):
    if match := CHAT_MESSAGE_PATTERN.match(line):
        sender, send_time, content, address = match.groups()
        if send_time and content.strip():
            return Chat(sender, formatted_date+'T'+send_time, content, address)
    return None

def adjust_replace_rule(content):
    for pattern, replacement in REPLACE_PATTERNS.items():
        content = content.replace(pattern, replacement)
    return content.strip()

def is_new_chat(line):
    return bool(NEW_CHAT_PATTERN.search(line))    

def process_chat_lines(lines):
    chats = []
    current_text = ""

    for line in map(adjust_replace_rule, lines):
        if is_new_chat(line):
            if current_text:
                parsed_chat = parse_chat_message(current_text.strip())
                if parsed_chat:
                    chats.append(parsed_chat)
            current_text = line
        else:
            current_text += ' ' + line
    
    if current_text:
        parsed_chat = parse_chat_message(current_text.strip())
        if parsed_chat:
            chats.append(parsed_chat)
        
    return chats



