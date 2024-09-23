import sys
from PyQt5.QtWidgets import QApplication
from file_monitor_app import FileMonitorApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileMonitorApp()
    ex.show()
    sys.exit(app.exec_())