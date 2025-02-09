import sys
from PyQt5.QtWidgets import QApplication
from main_window import BondHubChatSynchronizer 
from log_config import setup_logging
import logging

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    logger.info("BondHub start!")
    app = QApplication(sys.argv)
    window = BondHubChatSynchronizer()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()