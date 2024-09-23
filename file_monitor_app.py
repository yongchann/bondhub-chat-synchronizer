import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit
from PyQt5.QtCore import QTimer
from api_client import login, send_messages_to_api
from file_processor import process_files
from config import MONITOR_INTERVAL

class FileMonitorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.offsets = {}
        self.token = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_files)

    def initUI(self):
        self.setWindowTitle('파일 모니터링 애플리케이션')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # 로그인 섹션
        login_layout = QHBoxLayout()
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('사용자 이름')
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('비밀번호')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton('로그인', self)
        self.login_button.clicked.connect(self.login)

        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.login_button)

        layout.addLayout(login_layout)

        # 상태 표시 레이블
        self.status_label = QLabel('로그인하세요', self)
        layout.addWidget(self.status_label)

        # 로그 출력 영역
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # 시작/정지 버튼
        self.toggle_button = QPushButton('시작', self)
        self.toggle_button.clicked.connect(self.toggle_monitoring)
        self.toggle_button.setEnabled(False)
        layout.addWidget(self.toggle_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.token = login(username, password)
        if self.token:
            self.status_label.setText("로그인 성공! 모니터링을 시작할 수 있습니다.")
            self.toggle_button.setEnabled(True)
        else:
            self.status_label.setText("로그인 실패: 토큰을 찾을 수 없습니다.")

    def toggle_monitoring(self):
        if self.timer.isActive():
            self.timer.stop()
            self.toggle_button.setText('시작')
            self.status_label.setText('모니터링 정지됨')
        else:
            self.timer.start(MONITOR_INTERVAL)
            self.toggle_button.setText('정지')
            self.status_label.setText('모니터링 중...')

    def check_files(self):
        new_messages = process_files(self.offsets)
        if new_messages:
            self.log_new_messages(new_messages)
            all_messages = [msg for msgs in new_messages.values() for msg in msgs]
            send_messages_to_api(all_messages, self.token)
        self.log_area.append("파일 확인 완료\n")
        self.log_area.moveCursor(self.log_area.textCursor().End)
        logging.info("모든 파일 확인이 완료되었습니다.")

    def log_new_messages(self, messages):
        for filename, file_messages in messages.items():
            self.log_area.append(f"\n파일명: {filename}")
            self.log_area.append(f"새로 추가된 메시지 수: {len(file_messages)}")
            for message in file_messages:
                self.log_area.append(str(message))