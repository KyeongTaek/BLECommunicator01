from AHT21 import get_aht21

try:
    print("start...")
    result = get_aht21()
    print(result)
except Exception as error:
    print("read failed: ", error)

