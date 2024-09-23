import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
from PyQt5.QtCore import QTimer
from api_client import login, send_messages_to_api
from file_processor import process_files
from config import MONITOR_INTERVAL
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.offsets = {}
        self.token = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_files)

    def initUI(self):
        self.setWindowTitle('OTC Bridge Runner')
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
        self.login_button.clicked.connect(self.login)

        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.login_button)

        layout.addLayout(login_layout)

        # 상태 표시 레이블
        self.status_label = QLabel('Welcome to OTC Runner', self)
        layout.addWidget(self.status_label)

        # 시작/정지 버튼
        self.toggle_button = QPushButton('RUN!', self)
        self.toggle_button.clicked.connect(self.toggle_monitoring)
        self.toggle_button.setEnabled(False)
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)
        # 로그 출력 영역
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)


    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.token = login(username, password)
        if self.token:
            self.status_label.setText("Press RUN!")
            self.toggle_button.setEnabled(True)
        else:
            self.status_label.setText("Login Failed.")

    def toggle_monitoring(self):
        if self.timer.isActive():
            self.timer.stop()
            self.toggle_button.setText('RUN!')
            self.status_label.setText('stopped...')
        else:
            self.check_files()
            self.timer.start(MONITOR_INTERVAL)
            self.toggle_button.setText('Stop Running')
            self.status_label.setText('running...')

    def check_files(self):
        self.log_area.append(f"================================{datetime.now().strftime('%Y-%m-%d %H시 %M분 %S초')}================================\n")
        
        new_messages = process_files(self.offsets)
        if new_messages:
            # self.log_new_messages(new_messages)
            for filename, messages in new_messages.items():
                if messages:
                    self.log_area.append(f"✅ {filename} 파일의 ({messages[-1].timestamp}) 에 생성된 채팅까지 업데이트 되었습니다.\n{messages[-1].content}\n")
            all_messages = [msg for msgs in new_messages.values() for msg in msgs]
            send_messages_to_api(all_messages, self.token)
        else:
            self.log_area.append(f"💬 새 메시지가 없습니다.\n")