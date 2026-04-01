import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from seungmin.AHT21 import get_aht21
from ENS160 import init_ens160, get_ens160
from junhee.save import save_to_csv

import smbus2


# test ENS160 & AHT21 interface
shared_bus = smbus2.SMBus(1)
init_ens160(shared_bus) # 초기에 먼저 호출해주셔야 합니다!

ens = get_ens160(shared_bus)
aht = get_aht21()

rst = ens
rst.update(aht)

save_to_csv(rst)

for key in rst.keys():
    print(key + ": " + str(rst[key]), end=' ')

print()
