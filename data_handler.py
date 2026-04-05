from AHT21 import get_aht21
from ENS160 import get_ens160, init_ens160

import struct
import time
import csv
import smbus2
import server_advertising

bus = smbus2.SMBus(1)
init_ens160(bus)

def make_packet(temp, humi, aqi, tvoc, eco2):
    return struct.pack(
        '<hhBHHI',
        int(temp * 100),    # 온도
        int(humi * 100),    # 습도
        int(aqi),           # 공기질
        int(tvoc),          # 가스
        int(eco2),          # 이산화탄소
        int(time.time())    # 타임스탬프
    )

prev_data = None

def update_ble(packet):
    server_advertising.adv.update_service_data(packet) #패킷 전달

while True:
    try:
        aht = get_aht21()
        ens = get_ens160(bus)

        temp = aht["temp"]
        humi = aht["humi"]
        aqi = ens["aqi"]
        tvoc = ens["tvoc"]
        eco2 = ens["eco2"]

        data_tuple = (temp, humi, aqi, tvoc, eco2)

        if data_tuple != prev_data:
            packet = make_packet(temp, humi, aqi, tvoc, eco2)

            print("업데이트 발생:", data_tuple)
            print("패킷 길이:", len(packet))  #13이면 정상

            with open("data.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([time.time(), temp, humi, aqi, tvoc, eco2])

            update_ble(packet)
            prev_data = data_tuple

        time.sleep(1)

    except Exception as e:
        print("에러:", e)
        time.sleep(1)
