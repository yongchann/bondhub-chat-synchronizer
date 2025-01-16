import logging
import time
import os
import unicodedata
from PyQt5.QtCore import QObject, pyqtSignal
from service import append_log
from datetime import datetime

logger = logging.getLogger(__name__)

class MonitoringProcessor(QObject):
    update_signal = pyqtSignal(dict)

    def __init__(self, selected_date):
        super().__init__()
        self.selected_date = selected_date
        self.running = False
        self.files = {}  # 파일 정보를 저장할 딕셔너리
        

    def start(self):
        """모니터링 시작"""
        self.running = True
        while self.running:
            start_time = time.time()  # 전체 처리 시작 시간
            
            self.scan_files()
            processed_files = 0  # 처리된 파일 수 카운트
            
            for file_name in self.files:
                print(file_name, '파일 처리 시작', datetime.now())
                self.process_file(file_name)
                processed_files += 1
                
            end_time = time.time()  # 전체 처리 종료 시간
            processing_time = end_time - start_time
            
            logger.info(f"총 {processed_files}개 파일 처리 완료. 소요시간: {processing_time:.2f}초")
            
            self.update_signal.emit(self.files)  # 시그널을 통해 결과 전달
            time.sleep(5)  # PERIOD

    def stop(self):
        """모니터링 중단"""
        self.running = False
        logger.info("모니터링이 중단되었습니다.")

    def scan_files(self):
        """파일 스캔 및 조건에 맞는 파일 관리"""
        for file_name in os.listdir('.'):
            normalized_file_name = unicodedata.normalize('NFC', file_name)
            if normalized_file_name.endswith('.txt'):
                parts = normalized_file_name.split('_')
                if len(parts) > 2 and parts[2] == self.selected_date.replace('-', ''):
                    if normalized_file_name not in self.files:
                        # 새로운 파일인 경우 오프셋과 line_count를 초기화
                        print(normalized_file_name, '새로운 파일')
                        self.files[normalized_file_name] = {
                            'offset': 0,
                            'line_count': 0
                        }

        logger.info(f"스캔된 파일: {self.files}")

    def process_file(self, file_name):
        """파일에 대한 처리 로직을 추가할 메서드"""
        try:
            with open(file_name, 'r', encoding='cp949') as file:
                content = file.readlines()
                offset = self.files[file_name]["offset"]
                new_logs = content[offset:]
                if not self.send_logs_with_retry(file_name, offset, new_logs):
                    self.stop()  # 모든 재시도 실패 시 프로세스 중단
                
        except Exception as e:
            logger.error(f"파일 처리 중 오류 발생: {file_name}, 오류: {str(e)}")

    def send_logs_with_retry(self, file_name, offset, new_logs, max_retries=3, retry_interval=2):
        """로그를 서버로 전송하며 재시도 로직을 포함"""
        retries = 0
        while retries < max_retries:
            try:
                result = append_log(
                    chat_date=self.selected_date,
                    file_name=file_name,
                    offset=offset,
                    line_count=len(new_logs),
                    log=''.join(new_logs)
                )
                # 오프셋 업데이트
                self.files[file_name]["offset"] = result.get("currentOffset")
                return True  # 성공 시 True 반환
            except Exception as e:
                logger.error(f"로그 전송 실패: {file_name}, 재시도 {retries + 1}/{max_retries}, 오류: {str(e)}")
                retries += 1
                time.sleep(retry_interval)  # 재시도 간격

        logger.error(f"모든 재시도 실패: {file_name}. 프로세스를 중단합니다.")
        return False  # 모든 재시도 실패 시 False 반환
