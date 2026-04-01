import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import time

CSV_PATH = '/home/rasp5/opensrc5/yeyoung/sensor_data.csv'
OUTPUT_PATH = '/home/rasp5/opensrc5/yeyoung/eco2_tvoc_graph.png'

while True:
    try:
        df = pd.read_csv(CSV_PATH)
        df['time'] = pd.to_datetime(df['timestamp'])
        df = df.dropna(subset=['time'])
        df = df.sort_values('time')
        start_time = pd.to_datetime("2026-03-29 10:00:00")
        df = df[df['time'] >= start_time]

        df['eco2'] = pd.to_numeric(df['eco2'], errors='coerce')
        df['tvoc'] = pd.to_numeric(df['tvoc'], errors='coerce')
        df = df.dropna(subset=['eco2','tvoc'])

        df_sampled = df.iloc[::60, :]

        plt.figure(figsize=(12,6))
        plt.plot(df_sampled['time'], df_sampled['eco2'], label='eCO2 (ppm)', color='blue', linestyle='-')
        plt.plot(df_sampled['time'], df_sampled['tvoc'], label='TVOC (ppb)', color='green', linestyle='-')
        plt.axhline(y=1000, color='red', linestyle='--', label='eCO2 Threshold (1000 ppm)')
        plt.title('Time Series of eCO2 & TVOC')
        plt.xlabel('Time')
        plt.ylabel('Sensor Values')
        plt.legend()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(OUTPUT_PATH)
        plt.close()

        print(f"Graph updated: {OUTPUT_PATH}")

    except Exception as e:
        print("Error:", e)

    time.sleep(5)