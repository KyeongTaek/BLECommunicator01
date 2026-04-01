import csv
import os
from datetime import datetime

# 저장할 파일 경로
FILE_PATH = "./sensor_data.csv"

def save_to_csv(data):
    """
    데이터 객체를 받아 CSV 형식으로 저장합니다.
    데이터 순서: timestamp, temp, humi, aqi, tvoc, eco2 [cite: 26]
    """
    file_exists = os.path.isfile(FILE_PATH)
    
    try:
        with open(FILE_PATH, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 파일이 처음 생성될 때만 헤더 추가
            if not file_exists:
                writer.writerow(['timestamp', 'temp', 'humi', 'aqi', 'tvoc', 'eco2'])
            
            # 계획서에 명시된 순서대로 데이터 추출 [cite: 26, 35-46]
            writer.writerow([
                data.get('time', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                data.get('temp', 'N/A'),
                data.get('humi', 'N/A'),
                data.get('aqi', 'N/A'),
                data.get('tvoc', 'N/A'),
                data.get('eco2', 'N/A')
            ])
    except Exception as e:
        # 터미널 없이 실행되므로 로그 파일에 에러 기록 
        with open("./error.log", "a") as log_f:
            log_f.write(f"[{datetime.now()}] Save Error: {e}\n")