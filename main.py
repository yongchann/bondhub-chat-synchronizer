import sys
from PyQt5.QtWidgets import QApplication
from main_window import BondHubAppender
from log_config import setup_logging

def main():
    setup_logging()
    app = QApplication(sys.argv)
    window = BondHubAppender()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()