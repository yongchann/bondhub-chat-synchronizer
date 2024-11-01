import sys
from PyQt5.QtWidgets import QApplication
from app import FileMonitorApp
from log_config import setup_logging

if __name__ == '__main__':
    logger = setup_logging()
    logger.info("BondHub Chat Synchronizer start")
    app = QApplication(sys.argv)
    ex = FileMonitorApp()
    ex.show()
    sys.exit(app.exec_())