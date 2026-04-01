from save import save_to_csv

dummy_data={
        "time": "2026-03-27 14:30:05",
        "temp": 24.5,
        "humi": 55.2,
        "aqi": 1,
        "tvoc": 110,
        "eco2": 405
}

save_to_csv(dummy_data) # csv로 저장하는 함수
