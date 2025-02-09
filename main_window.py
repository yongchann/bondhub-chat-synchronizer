from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit, QMessageBox, QCalendarWidget, QGroupBox, QApplication
from PyQt5.QtCore import QDate, Qt, QThread
from file_monitor import MonitoringProcessor
from service import login, get_bond_setting
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BondHubChatSynchronizer(QWidget):
    WINDOW_TITLE = 'BondHub Chat Synchronizer'
    WINDOW_GEOMETRY = (100, 100, 1200, 800)

    def __init__(self):
        super().__init__()
        self.selected_date = QDate.currentDate().toString('yyyy-MM-dd')
        self.monitoring_processor = None
        self.monitoring_thread = None
        self.initUI()
        self.setupGlobalExceptionHandler()
        logger.info("initialization completed")

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
        control_group = QGroupBox("")
        control_layout = QHBoxLayout()
        
        self.prepare_button = self.createButton('모니터링 준비', self.handlePrepare)
        control_layout.addWidget(self.prepare_button)
        
        self.run_button = self.createButton('모니터링 시작', self.handleRunMonitoring)
        self.run_button.setEnabled(False)
        control_layout.addWidget(self.run_button)
        
        control_group.setLayout(control_layout)
        
        wrapper_layout = QHBoxLayout()
        wrapper_layout.addWidget(control_group)
        return wrapper_layout

    def initStatusSection(self):
        status_layout = QHBoxLayout()
        
        files_group = QGroupBox("파일 동기화 현황")
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
        if not username or not password:
            QMessageBox.warning(self, "Login Error", "아이디 또는 비밀번호를 입력해주세요.")
            return
    
        success = login(username, password)
        if success:
            self.status_label.setText(f"{username}님, 안녕하세요")
            self.login_button.hide()
            self.username_input.hide()
            self.password_input.hide()
            logger.info(f"login success: username: {username}")
        else:
            QMessageBox.warning(self, "Login Error", "아이디 또는 비밀번호가 틀렸습니다.")
            logger.error(f"login failed: username: {username} password: {password}")
            
    def handleRunMonitoring(self):
        if self.monitoring_processor and self.monitoring_processor.running:
            logger.info("monitoring stop button clicked")
            self.log("모니터링 중단")
            self.monitoring_processor.stop()
            self.monitoring_thread.quit()
            self.monitoring_thread.wait()
            self.run_button.setText('모니터링 재시작')
        else:
            logger.info("monitoring start button clicked")
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
        self.files_area.append(f"[기준시각]: {scan_time}\n")
        
        for idx, (file_name, data) in enumerate(result.items(), start=1):
            offset = data['offset']
            self.files_area.append(f"[{idx}] {file_name}\n > {offset} lines processed\n\n")

    def handlePrepare(self):
        setting = get_bond_setting(self.selected_date)
        ok_count = setting.get("countByStatus").get("OK")
        discarded_count = setting.get("countByStatus").get("DISCARDED")
        ktb_benchmarks = setting.get("ktbBenchmarks")
        ktb_str = '\n'.join([f"{info.get('benchmarkType')[1:]}년 - {info.get('code')}({info.get('bondName')[13:-1]}) " for info in ktb_benchmarks])
        
        if not ok_count or not discarded_count or not ktb_benchmarks:
            QMessageBox.warning(self, "채권 상태", f"{self.selected_date} 채권 기준정보 \n\n[크레딧]\n정상 크레딧: {ok_count if ok_count else 0}\n제외 크레딧: {discarded_count if discarded_count else 0}\n\n[국고 지표]\n{ktb_str}")
            self.run_button.setEnabled(False)
            self.log(f"모니터링 시작 불가. {self.selected_date} 의 채권 기준정보가 없습니다.")
            logger.error(f"monitoring start failed. {self.selected_date} 의 채권 기준정보가 없습니다.")
        else:
            QMessageBox.information(self, "채권 상태", f"{self.selected_date} 채권 기준정보 \n\n[크레딧]\n정상 크레딧: {ok_count}\n제외 크레딧: {discarded_count}\n\n[국고 지표]\n{ktb_str}")
            self.run_button.setEnabled(True)
            self.log(f"모니터링 준비 완료. 모니터링 시작 버튼을 누르세요")
            logger.info(f"monitoring prepare success: {self.selected_date}")
    def updateSelectedDate(self):
        selected_date = self.calendar.selectedDate()
        self.selected_date = selected_date.toString('yyyy-MM-dd')
        self.date_label.setText(self.selected_date)
        self.calendar.hide()
        self.log(f"날짜를 변경했습니다: {self.selected_date}")

    def showCalendarAtLabel(self):
        pos = self.date_label.mapToGlobal(self.date_label.rect().bottomLeft())
        self.calendar.move(pos)
        self.calendar.show()

    def showLoginDialog(self):
        self.username_input.show()
        self.password_input.show()
        self.login_button.show()
        self.status_label.setText("")

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
        formatted_message = f"[{level}] {current_time} : {message}\n-----------------------------------------------------------------------------------------"
        self.log_area.append(formatted_message)
        
        scrollbar = self.log_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def setupGlobalExceptionHandler(self):
        import sys
        sys._excepthook = sys.excepthook
        def exception_hook(exctype, value, traceback):
            sys._excepthook(exctype, value, traceback)
            self.handleGlobalException(exctype, value, traceback)
        sys.excepthook = exception_hook

    def handleGlobalException(self, exctype, value, traceback):
        from api_client import AuthenticationRequired
        
        error_message = str(value)
        error_position = traceback.tb_frame.f_code.co_name
        error_line = traceback.tb_lineno
        title = "오류"
        
        if isinstance(value, AuthenticationRequired):
            title = "인증 오류"
            self.showLoginDialog()
        
        QMessageBox.warning(self, title, error_message)
        self.log(f"\nMESSAGE: {error_message}\nPOSITION: {error_position}:{error_line}", level='ERROR') 