import smbus2
from ENS160 import init_ens160, get_ens160

bus = smbus2.SMBus(1)

# test ENS160 interface
init_ens160(bus) # 초기에 먼저 호출해주셔야 합니다!

rst = get_ens160(bus)
for key in rst.keys():
    print(key + ": " + str(rst[key]), end=' ')

print()
