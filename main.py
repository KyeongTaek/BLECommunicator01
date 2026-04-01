import time
from datetime import datetime
import smbus2
import sys
sys.path.append("/home/rasp5/opensrc5")

from AHT21 import get_aht21
from ENS160 import get_ens160, init_ens160
from save import save_to_csv

# I2C bus 생성
bus = smbus2.SMBus(1)

# ENS160 초기화 (한 번만)
init_ens160(bus)

# 이전 데이터 저장용
prev_data = {
    "temp": None,
    "humi": None,
    "aqi": None,
    "tvoc": None,
    "eco2": None
}

def main():
    print("System started")
    
    while True:
        try:
            # AHT21 센서 읽기
            aht = get_aht21() 

            if aht:
                prev_data["temp"] = aht.get("temp")
                prev_data["humi"] = aht.get("humi")

            # ENS160 센서 읽기
            ens = get_ens160(bus)

            if ens:
                prev_data["aqi"] = ens.get("aqi")
                prev_data["tvoc"] = ens.get("tvoc")
                prev_data["eco2"] = ens.get("eco2")

            # 최종 데이터 객체 (팀 규격)
            data = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "temp": prev_data["temp"],
                "humi": prev_data["humi"],
                "aqi": prev_data["aqi"],
                "tvoc": prev_data["tvoc"],
                "eco2": prev_data["eco2"]
            }

            # CSV 저장
            save_to_csv(data)

            # 콘솔 출력
            print(data)

        except Exception as e:
            print("Error:", e)

        # 1초마다 반복
        time.sleep(1)


if __name__ == "__main__":
    main()
