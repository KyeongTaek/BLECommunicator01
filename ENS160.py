import smbus2
import time

# ENS160 센서 주소
ENS160_ADDR = 0x53

def init_ens160(bus): # i2c bus 주입
    """ 초기 설정 함수입니다! 통합 시 처음에 한번 호출해주세요!"""
    OP_REG = 0x10
    OP_MODE_STANDARD = 0x02

    try:
        bus.write_byte_data(ENS160_ADDR, OP_REG, OP_MODE_STANDARD) # 센서의 동작 모드를 standard로 설정
        time.sleep(0.1) # 설정 적용 대기

        # standard로 설정되었는지 확인
        op_reg = bus.read_i2c_block_data(ENS160_ADDR, OP_REG, 1)
        if op_reg[0] != OP_MODE_STANDARD:
            raise Exception("동작 모드가 써지지 않음!")

    except Exception as e:
        print(f"ENS160 초기화 실패: {e}")

def get_ens160_status(bus):
    STATUS_REG = 0x20 # 센서 상태 정보 저장 reg
    
    try:
        status_byte = bus.read_i2c_block_data(ENS160_ADDR, STATUS_REG, 1) # 센서 상태 정보 가져옴
    except Exception as e:
        print(f"ENS160 상태 정보 읽기 실패:  {e}")
        return None

    status = (status_byte[0] & 0x0C) >> 2 # bit 3:2 부분만 가져와 decimal로 만듦

    if status == 0:
        if (status_byte[0] & 0x01) == 1: # 센서 데이터가 들어왔으면
            return "OPERATING"
        else:
            return "NOT_YET"
    elif status == 1:
        return "WARMUP"
    elif status == 2:
        return "STARTUP"
    else:
        return "INVALID"

def get_ens160(bus):
    status = get_ens160_status(bus)

    if status != "OPERATING":
        print(f"ENS160 현재 상태: {status} (데이터 기다리는 중...)")
        return None    

    try:
        DATA_AQI = 0x21
        # 0x21(AQI)부터 5바이트 읽기
        block = bus.read_i2c_block_data(ENS160_ADDR, DATA_AQI, 5)

        aqi = block[0] & 0x07 # 하위 3비트만 남김
    
        bytes_tvoc = block[1:3] # 2 byte of DATA_TVOC
        tvoc = int.from_bytes(bytes_tvoc, byteorder='little', signed=False) # convert little endian to big endian integer
    
        bytes_eco2 = block[3:5] # 2 byte of DATA_ECO2
        eco2 = int.from_bytes(bytes_eco2, byteorder='little', signed=False) # convert little endian to big endian integer
        
        return {'aqi': aqi, 'tvoc': tvoc, 'eco2': eco2}

    except Exception as e: 
  # 센서 불량 등 물리적 에러
        print(f"I2C 통신 에러 발생: {e}")
        return None
