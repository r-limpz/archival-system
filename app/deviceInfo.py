import socket
import httpagentparser
from device_detector import DeviceDetector

#generate device information of user
def deviceID_selector(agent):
    device_data = {'device': '', 'os': '', 'browser': '', 'ip_address': ''}
    ip_address = socket.gethostbyname(socket.gethostname())
    browser_info = httpagentparser.detect(agent)

    browser_name = browser_info.get('browser', {}).get('name', 'Unknown')
    device = DeviceDetector(agent).parse()
    deviceType= device.device_type()
    os = f"{device.os_name()} {device.os_version()}" 

    device_data = {'device': (deviceType), 'os': os, 'browser': browser_name, 'ip_address': ip_address}
    return device_data