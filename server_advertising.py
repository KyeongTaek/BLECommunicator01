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
class Advertisement(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/advertisement'

    def __init__(self, bus, index, advertising_type):
        self.path = self.PATH_BASE + str(index)
        self.bus = bus
        self.ad_type = advertising_type

        self.service_uuids = bluetooth_constants.ENVIRONMENT_SENSING_UUID
        self.manufacturer_data = None
        self.solicit_uuids = None

        # Add 13byte dummy data to service_data
        self.service_data = {
                bluetooth_constants.ENVIRONMENT_SENSING_UUID: dbus.ByteArray(bytes([0xF6, 0x09, 0xA0, 0x0F, 0x02, 0x96, 0x00, 0x58, 0x02, 0xF0, 0x0B, 0x0c, 0x66]))
        }

        self.local_name = "Opensrc_team5"
        self.include_tx_power = False
        self.data = None
        self.discoverable = True

        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        properties = {
                'Type': self.ad_type,
                'LocalName': dbus.String(self.local_name),
                'ServiceUUIDs': dbus.Array(self.service_uuids, signature='s'),
                'ServiceData': dbus.Dictionary(self.service_data, signature='sv'),
        }

        if self.include_tx_power:
            properties['Includes'] = dbus.Boolean(True)
        
        print(properties)
        return {'org.bluez.LEAdvertisement1': properties}

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(bluetooth_constants.DBUS_PROPERTIES,
            in_signature='s',
            out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != bluetooth_constants.ADVERTISEMENT_INTERFACE:
            raise bluetooth_exceptions.InvalidArgsException()
        return self.get_properties()[bluetooth_constants.ADVERTISING_MANAGER_INTERFACE]

    @dbus.service.method(bluetooth_constants.ADVERTISING_MANAGER_INTERFACE,
            in_signature='',
            out_signature='')
    def Release(self):
        print('%s: Released' % self.path)

def register_ad_cb():
    print('Advertisement registered OK')

def register_ad_error_cb(error):
    print('Error: Failed to register advertisement: ' + str(error))
    mainloop.quit()

def start_advertising():
    global adv
    global adv_mgr_interface
    # we're only registering one advertisement object so index (arg2) is hard coded as 0
    print("Registering advertisement",adv.get_path())
    adv_mgr_interface.RegisterAdvertisement(adv.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)

dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SystemBus()
# we're assuming the adapter supports advertising
adapter_path = bluetooth_constants.BLUEZ_NAMESPACE + bluetooth_constants.ADAPTER_NAME
print(adapter_path)

adv_mgr_interface = dbus.Interface(bus.get_object(bluetooth_constants.BLUEZ_SERVICE_NAME,adapter_path), bluetooth_constants.ADVERTISING_MANAGER_INTERFACE)
# we're only registering one advertisement object so index (arg2) is hard coded as 0
adv = Advertisement(bus, 0, 'peripheral')
start_advertising()

print("Advertising as "+adv.local_name)

mainloop = GLib.MainLoop()
mainloop.run()
