import logging
import time
import os
import unicodedata
from PyQt5.QtCore import QObject, pyqtSignal
from service import append_log
from config import MONITOR_INTERVAL

logger = logging.getLogger(__name__)

class MonitoringProcessor(QObject):
    update_signal = pyqtSignal(dict)

    def __init__(self, selected_date):
        super().__init__()
        self.selected_date = selected_date
        self.running = False
        self.files = {}  
        self.period = MONITOR_INTERVAL
        
    def start(self):
        self.running = True
        logger.info("monitoring started")
        while self.running:
            self.scan_files()
            for file_name in self.files:
                before_offset = self.files[file_name]["offset"]
                updated_offset = self.process_file(file_name)
                if updated_offset != before_offset:
                    logger.info(f"file processed: {file_name}, offset: {before_offset} -> {updated_offset}")
            self.update_signal.emit(self.files)
            time.sleep(self.period) 

    def stop(self):
        self.running = False
        logger.info("monitoring stopped")

    def scan_files(self):
        for file_name in os.listdir('.'):
            normalized_file_name = unicodedata.normalize('NFC', file_name)
            if normalized_file_name.endswith('.txt'):
                parts = normalized_file_name.split('_')
                if len(parts) > 2 and parts[2] == self.selected_date.replace('-', ''):
                    if normalized_file_name not in self.files:
                        self.files[normalized_file_name] = {'offset': 0}
                        logger.info(f"new file detected: {normalized_file_name}, total file count: {len(self.files)}")


    def process_file(self, file_name):
        try:
            with open(file_name, 'r', encoding='cp949') as file:
                lines = [line.strip() for line in file.readlines()]
                offset = self.files[file_name]["offset"]
                new_logs = lines[offset:]
                updated_offset = append_log(
                    base_date=self.selected_date,
                    file_name=file_name,
                    offset=offset,
                    logs = new_logs
                )
                self.files[file_name]["offset"] = updated_offset
                return  updated_offset
        except Exception as e:
            logger.error(f"file processing error: {file_name}, error: {str(e)}")