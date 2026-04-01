print("AHT221.py started")
from smbus2 import SMBus, i2c_msg
import time

AHT21_ADDRESS = 0x38
I2C_BUS_NUMBER = 1

def first(bus):
    with SMBus(I2C_BUS_NUMBER) as bus:
        time.sleep(0.1)
        bus.write_i2c_block_data(AHT21_ADDRESS, 0xAC, [0x33, 0x00])
        data = None
        for _ in range(100):
            time.sleep(0.01)

            read_message = i2c_msg.read(AHT21_ADDRESS, 6)
            bus.i2c_rdwr(read_message)
            data = list(read_message)


            if (data[0] & 0x80) == 0:
                break

        else:
            raise RuntimeError("busy")

        






 
        humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
        temperature_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
        humidity = (humidity_raw / 1048576.0) * 100.0
        temperature = (temperature_raw / 1048576.0) * 200.0 - 50.0
        #dictionary
        return {
                "temp" : round(temperature, 1),
                "humi" : round(humidity, 1)
          }


def get_aht21():
    with SMBus(I2C_BUS_NUMBER) as bus:
        time.sleep(0.1)
        first(bus)
        time.sleep(0.1)
        return first(bus)



