import sys
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox, QCalendarWidget, QGroupBox, QApplication
from PyQt5.QtCore import QDate, Qt, QThread
from file_monitor import MonitoringProcessor
from service import authenticate
from api_client import AuthenticationRequired
from datetime import datetime

logger = logging.getLogger(__name__)

def global_exception_handler(exctype, value, traceback):
    if exctype == AuthenticationRequired:
        active_window = QApplication.activeWindow()
        if active_window:
            active_window.showLoginDialog()
    else:
        sys.__excepthook__(exctype, value, traceback)

sys.excepthook = global_exception_handler

class BondHubAppender(QWidget):
    WINDOW_TITLE = 'BondHub'
    WINDOW_GEOMETRY = (100, 100, 900, 700)

    def __init__(self):
        super().__init__()
        self.selected_date = QDate.currentDate().toString('yyyy-MM-dd')
        self.monitoring_processor = None
        self.monitoring_thread = None
        self.initUI()
        logger.info(f"BondHubAppender initialized with date: {self.selected_date}")

    def initUI(self):
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setGeometry(*self.WINDOW_GEOMETRY)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.initTitleSection())
        main_layout.addLayout(self.initLoginSection())
        main_layout.addLayout(self.initDateSection())
        main_layout.addLayout(self.initControlSection())
        main_layout.addLayout(self.initStatusSection())
        
        self.setLayout(main_layout)

    def initTitleSection(self):
        title_layout = QHBoxLayout()
        title_label = QLabel("BondHub", self)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        return title_layout

    def initLoginSection(self):
        login_layout = QHBoxLayout()
        
        self.username_input = self.createLineEdit('아이디', width=120)
        self.password_input = self.createLineEdit('비밀번호', width=120, echo_mode=QLineEdit.Password)
        self.login_button = self.createButton('로그인', self.handleLogin, width=60)
        self.status_label = QLabel('', self)
        
        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(self.login_button)
        login_layout.addWidget(self.status_label)
        login_layout.addStretch()
        
        return login_layout

    def initDateSection(self):
        date_group = QGroupBox("날짜를 선택해주세요")
        date_layout = QVBoxLayout()
        
        self.date_label = QLabel(QDate.currentDate().toString('yyyy-MM-dd'), self)
        self.calendar = QCalendarWidget(self)
        self.calendar.clicked.connect(self.updateSelectedDate)
        self.calendar.hide()
        self.calendar.setFixedSize(400, 300)
        self.calendar.setWindowFlags(Qt.Popup)
        
        self.date_label.mousePressEvent = lambda e: self.showCalendarAtLabel()
        
        date_layout.addWidget(self.date_label)
        date_group.setLayout(date_layout)
        
        wrapper_layout = QHBoxLayout()
        wrapper_layout.addWidget(date_group)
        return wrapper_layout

    def initControlSection(self):
        control_group = QGroupBox("조작 영역")
        control_layout = QHBoxLayout()
        
        self.prepare_button = self.createButton('모니터링 준비', self.handlePrepare)
        control_layout.addWidget(self.prepare_button)
        
        self.run_button = self.createButton('모니터링 실행', self.handleRunMonitoring)
        self.run_button.setEnabled(False)
        control_layout.addWidget(self.run_button)
        
        control_group.setLayout(control_layout)
        
        wrapper_layout = QHBoxLayout()
        wrapper_layout.addWidget(control_group)
        return wrapper_layout

    def initStatusSection(self):
        status_layout = QHBoxLayout()
        
        files_group = QGroupBox("모니터링 현황")
        files_layout = QVBoxLayout()
        self.files_area = QTextEdit(self)
        self.files_area.setReadOnly(True)
        files_layout.addWidget(self.files_area)
        files_group.setLayout(files_layout)
        
        status_group = QGroupBox("실행 로그")
        status_layout_right = QVBoxLayout()
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        status_layout_right.addWidget(self.log_area)
        status_group.setLayout(status_layout_right)
        
        status_layout.addWidget(files_group)
        status_layout.addWidget(status_group)
        
        return status_layout

    def handleLogin(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        success, message = authenticate(username, password)
        
        if success:
            logger.info(f"{username}님, 안녕하세요")
            self.status_label.setText(f"{username}님, 안녕하세요")
            self.login_button.hide()
            self.username_input.hide()
            self.password_input.hide()
        else:
            QMessageBox.warning(self, "Login Error", message)

    def handleRunMonitoring(self):
        if self.monitoring_processor and self.monitoring_processor.running:
            self.log("모니터링 중단")
            self.monitoring_processor.stop()
            self.monitoring_thread.quit()
            self.monitoring_thread.wait()
            self.run_button.setText('모니터링 재시작')
            self.log_area.append("모니터링이 중단되었습니다.")
        else:
            self.log("모니터링 시작")
            self.monitoring_processor = MonitoringProcessor(self.selected_date)
            self.monitoring_thread = QThread()
            self.monitoring_processor.moveToThread(self.monitoring_thread)
            self.monitoring_processor.update_signal.connect(self.updateMonitoringStatus)
            self.monitoring_thread.started.connect(self.monitoring_processor.start)
            self.monitoring_thread.start()
            self.run_button.setText('모니터링 중단')

    def updateMonitoringStatus(self, result):
        self.files_area.clear()
        scan_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.files_area.append(f"스캔시각: {scan_time}\n")
        
        for _, (file_name, data) in enumerate(result.items(), start=1):
            offset = data['offset']
            self.files_area.append(f"파일명: {file_name}\n오프셋: {offset}\n--------------------------------")

    def handlePrepare(self):
        self.log("모니터링 준비 완료")
        self.run_button.setEnabled(True)

    def updateSelectedDate(self):
        selected_date = self.calendar.selectedDate()
        self.selected_date = selected_date.toString('yyyy-MM-dd')
        self.date_label.setText(self.selected_date)
        self.calendar.hide()

    def showCalendarAtLabel(self):
        pos = self.date_label.mapToGlobal(self.date_label.rect().bottomLeft())
        self.calendar.move(pos)
        self.calendar.show()

    def showLoginDialog(self):
        self.username_input.show()
        self.password_input.show()
        self.login_button.show()
        self.status_label.setText("")
        QMessageBox.information(self, "인증 실패", "로그인 ")

    def createLineEdit(self, placeholder, width=None, echo_mode=QLineEdit.Normal):
        line_edit = QLineEdit(self)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setEchoMode(echo_mode)
        if width:
            line_edit.setFixedWidth(width)
        return line_edit

    def createButton(self, text, callback, width=None, enabled=True):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        button.setEnabled(enabled)
        if width:
            button.setFixedWidth(width)
        return button

    def log(self, message: str, level: str = 'INFO'):
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{current_time}] [{level}] {message}"
        self.log_area.append(formatted_message)
        
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum()) 