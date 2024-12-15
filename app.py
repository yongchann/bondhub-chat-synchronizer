import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QCalendarWidget
from PyQt5.QtCore import QTimer
from api_client import login, check_status, get_offset_map, append_chat_log
from file_processor import find_target_file_names, get_new_chat_logs
from config import MONITOR_INTERVAL
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.offsets = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.synchronize_chat)

    def initUI(self):
        self.setWindowTitle('BondHub Chat Synchronizer')
        self.setGeometry(100, 100, 900, 700)

        layout = QVBoxLayout()

        # 로그인 섹션
        login_layout = QHBoxLayout()
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Username')
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('Login', self)
        self.login_button.clicked.connect(self.handle_login)

        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.login_button)

        layout.addLayout(login_layout)

        # 상태 표시 레이블
        self.status_label = QLabel('BondHub Chat Synchronizer', self)
        layout.addWidget(self.status_label)
        
        self.calendar = QCalendarWidget(self)
        layout.addWidget(self.calendar)

        # 시작/정지 버튼
        self.run_button = QPushButton('RUN!', self)
        self.run_button.clicked.connect(self.handle_run)
        self.run_button.setEnabled(False)
        layout.addWidget(self.run_button)

        # 로그 출력 영역
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        self.setLayout(layout)
        

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if username and password:
            result = login(username, password)
            if result:
                self.status_label.setText("Press RUN!")
                self.run_button.setEnabled(True)
            else:
                self.status_label.setText("Login Failed.")

    def handle_run(self):
        if self.timer.isActive():
            self.timer.stop()
            self.run_button.setText('RUN!')
            self.status_label.setText('stopped...')
        # elif self.check_status():
        elif True:
                self.synchronize_chat()
                self.timer.start(MONITOR_INTERVAL)
                self.run_button.setText('Stop Running')
                self.status_label.setText('running...')

    def check_status(self):
        selected_date = self.calendar.selectedDate()
        chat_date = selected_date.toString("yyyy-MM-dd")
        count = check_status(chat_date)
        if count < 1:
            self.log_area.append(f"{chat_date} 일자의 채권 가격을 먼저 업로드 해주세요.\n")
            return False
        return True

    def synchronize_chat(self):
        self.log_area.append(f"================================{datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')}================================\n")
        
        chat_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        target_prefixes = [f"{room_name}_{chat_date.replace('-', '')}" for room_name in ["채권_블커본드", "채권_레드본드", "채권_막무가내"]]
        file_names = find_target_file_names(target_prefixes)
        offset_map = get_offset_map(chat_date)
        
        chat_log_infos = []
        for file_name in file_names:
            offset = offset_map[file_name]
            chat_log = get_new_chat_logs(file_name, offset)
            if chat_log:
                chat_log_infos.append({
                    "baseDate": chat_date,
                    "fileName": file_name,
                    "content": chat_log,
                    "offset": offset
                })
        
        append_chat_log(chat_date, chat_log_infos)
        
        