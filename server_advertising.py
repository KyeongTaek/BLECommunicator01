import bluetooth_constants
import bluetooth_exceptions
import dbus
import dbus.exceptions
import dbus.service
import dbus.mainloop.glib
import sys
from gi.repository import GLib
sys.path.insert(0, '.')

bus = None
adapter_path = None
adv_mgr_interface = None

# much of this code was copied from bluetooth.com/bluetooth-resources/bluetooth-for-linux
class Advertisement(dbus.service.Object): # 광고 패킷의 내용 담는 클래스
    PATH_BASE = '/org/bluez/example/advertisement' # 광고 객체 d-bus 경로의 base 주소

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type

        # 환경 센서 기기(181A)임을 선언함
        self.service_uuids = [dbus.String(bluetooth_constants.ENVIRONMENT_SENSING_UUID)] # BlueZ가 이해할 수 있도록, uuid를 리스트로 둘러쌈.
        
        # Add 13byte dummy data to service_data
        self.service_data = {
                dbus.String(bluetooth_constants.ENVIRONMENT_SENSING_UUID): dbus.ByteArray([0xF6, 0x09, 0xA0, 0x0F, 0x02, 0x96, 0x00, 0x58, 0x02, 0xF0, 0x0B, 0x0c, 0x66]) # dbus.String으로 변환
        }

        self.local_name = "Opensrc_team5"
        self.include_tx_power = False # 송신 전력 레벨 포함 여부
        self.discoverable = True
        self._last_payload = None # 이전 패킷 담는 변수

        self.manufacturer_data = None
        self.solicit_uuids = None
        self.data = None

        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self): # BlueZ가 광고할 데이터를 요청하면, 딕셔너리를 반환
        properties = {
                'Type': self.ad_type,
                'LocalName': dbus.String(self.local_name),
                'ServiceUUIDs': dbus.Array(self.service_uuids, signature='s'),
                'ServiceData': dbus.Dictionary(self.service_data, signature='sv'),
        }

        if self.include_tx_power: # 송신 전력 레벨 포함하고 싶다면
            properties['Includes'] = dbus.Boolean(True) # properties에 추가
        
        print(properties)
        return {'org.bluez.LEAdvertisement1': properties} # 'org.bluez.LEAdvertisement1'을 키로 하는 값(딕셔너리) 반환

    def get_path(self):                   # 광고 객체의 d-bus 경로(BlueZ가 d-bus를 통해 광고 객체를 찾을 수 있는 경로)임을 알려주기 위해,
        return dbus.ObjectPath(self.path) # BlueZ가 이해할 수 있는 타입으로 규격화

    # 해당 메서드를 외부 프로그램(여기선 BlueZ)이 호출할 수 있게 함.
    @dbus.service.method(bluetooth_constants.DBUS_PROPERTIES,
            in_signature='s',       # 외부에서 메서드의 인자로 넣을 데이터의 타입(s: 문자열)
            out_signature='a{sv}')  # 메서드가 반환할 데이터의 타입(a{sv}: key 값은 문자열이고 value 값으로는 뭐가 올지 모르는 딕셔너리)
    def GetAll(self, interface):  # 인터페이스에서 모든 속성 한번에 조회하는 메서드(d-bus 표준 인터페이스)
        if interface != bluetooth_constants.ADVERTISEMENT_INTERFACE: # 인터페이스가 '광고 데이터 인터페이스'가 아니라면
            raise bluetooth_exceptions.InvalidArgsException() # '인자가 올바르지 않음' 에러 일으킴
        return self.get_properties()['org.bluez.LEAdvertisement1'] # 속성을 꺼낼 인터페이스를 '광고 데이터 인터페이스'로 설정

    @dbus.service.method(bluetooth_constants.ADVERTISING_MANAGER_INTERFACE,
            in_signature='',    # d-bus는 엄격한 타입을 요구하기에, in_sig와 out_sig를 미리 설명해야 함
            out_signature='')
    def Release(self):
        print('%s: Released' % self.path)

def register_ad_cb(): # 광고 객체 등록 성공 시 작동하는 콜백 함수
    print('Advertisement registered OK')

def register_ad_error_cb(error): # 광고 객체 등록 실패 시 작동하는 콜백 함수
    print('Error: Failed to register advertisement: ' + str(error))
    mainloop.quit() # BlueZ와의 통신 중단(-> 이후 광고 중단됨)

def start_advertising():
    global adv # 광고 객체(전역변수)
    global adv_mgr_interface # 광고 관리 기능 전용 객체(전역변수)
    # we're only registering one advertisement object so index (arg2) is hard coded as 0
    print("Registering advertisement",adv.get_path())

    # 블루투스 어댑터에게 광고 객체의 광고 시작 요청(내부적: 파이썬에서 RegisterAdvertisement 호출하면 dbus.interface가 dbus 메시지로 변환해 BlueZ에 전달)
    adv_mgr_interface.RegisterAdvertisement(adv.get_path(), {},
                                        reply_handler=register_ad_cb, # 성공 시 콜백 함수 지정
                                        error_handler=register_ad_error_cb) # 실패 시 콜백 함수 지정

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True) # d-bus 신호를 mainloop이 이해할 수 있게 변환하고, 이를 mainloop이 처리하도록 설정
bus = dbus.SystemBus()
# we're assuming the adapter supports advertising
adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME # 어댑터 경로 설정
print(adapter_path)

# dbus.Interface: 상대방(BlueZ)이 제공하는 메서드를 파이썬 함수처럼 직접 호출할 수 있게 하는 프록시 객체 반환.
adv_mgr_interface = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path), bluetooth_constants.ADVERTISING_MANAGER_INTERFACE) # bus.getObject()로 받아온 서비스 전체 주소에서, 광고 관리(AdvertisingManager1) 관련 기능만 모아줌.

# we're only registering one advertisement object so index (arg2) is hard coded as 0
adv = Advertisement(bus, 0, 'peripheral')
start_advertising()

print("Advertising as "+adv.local_name)

# 혼자 있다면 단순히 프로그램이 무한루프를 돌게 하는 코드. 아직은 d-bus 신호 받을 줄 모름.
# DBusGMainLoop이 d-bus의 이벤트를 mainloop이 이해할 수 있는 신호로 변환해, 루프가 d-bus를 통해 들어오는 모든 호출(ex. BlueZ의 광고 객체 요청)을 처리할 수 있게 함.
mainloop = GLib.MainLoop()
mainloop.run()
