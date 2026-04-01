import pandas as pd
import time

def getLevel(di):
    if di <= 68:
        return "대부분 쾌적"
    elif di < 75:
        return "10% 정도가 불쾌감 느낌"
    elif di < 80:
        return "50% 정도가 불쾌감 느낌"
    else:
        return "대부분이 매우 불쾌"

while True:
    df = pd.read_csv('./sensor_data.csv')
    last_row = df.iloc[-1]

    t = float(last_row['temp'])
    rh = float(last_row['humi']) / 100

    di = (9/5)*t-0.55*(1-rh)*((9/5)*t-26)+32
    print("di: " + str(di) + ", " + getLevel(di))
    time.sleep(2)
