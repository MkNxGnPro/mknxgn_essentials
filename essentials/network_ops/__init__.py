import netifaces
import socket
import time
import threading

def Get_IP():
    ips = {"ext": [], "local": []}
    for inface in netifaces.interfaces():
        try:
            ip = netifaces.ifaddresses(inface)[netifaces.AF_INET][0]['addr']
            if "127" == ip[:3]:
                ips['local'].append(ip)
            elif "169" == ip[:3]:
                ips['local'].append(ip)
            else:
                ips['ext'].append(ip)
        except:
            pass
    return ips

def Get_GW():
    gateways = netifaces.gateways()
    return gateways['default'][netifaces.AF_INET][0]

class Device(object):
    def __init__(self, ip):
        self.ip = ip
        self.Mk_Device = False
        self.Mk_Data = {}
        self.Mk_Type = False
        self.ports = []
        self.hostname = None

    @property
    def rtsp(self):
        return 554 in self.ports

    @property
    def http(self):
        return 80 in self.ports
    
    @property
    def json(self):
        data = {"ip": self.ip, "ports": self.ports, "hostname": self.hostname}
        if self.Mk_Device:
            data['mk_device'] = self.Mk_Data
        return data 

class Devices(object):
    def __init__(self):
        self.All = {}

    @property
    def json(self):
        data = {}
        for item in self.All:
            data[self.Devices[item].IP] = self.All[item].json
        return data

class Port_Scanner(object):

    def __init__(self, check_ports):
        self.GW = Get_GW()
        self.IP = Get_IP()
        self.check_ports = check_ports
        self.base = ".".join(self.GW.split(".")[:3]) + "."
        self.running = 0
        self.Devices = Devices()

    def Collect(self):
        time.sleep(2)
        self.Devices = Devices()
        self.counted = 0

        for port in self.check_ports:
            start = 0
            for i in range(1, 6):
                threading.Thread(target=self.__ripper__, args=[start, i*52, port]).start()
                self.running += 1
                start += 52

        while self.running > 0:
            print("[ DDS ] - Device Discovery Scan. Addresses Scanned:", self.counted, end="\r")
            time.sleep(0.01)
        print("[ DDS ] - Device Discovery Scan. Addresses Scanned:", self.counted)

        return self.Devices
        

    def __ripper__(self, start, end, port):
        while start <= end:
            try:
                rmIP = self.base + str(start)
                self.counted += 1
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                sock.connect((rmIP, port))
                time.sleep(0.2)
                if rmIP not in self.Devices.All:
                    device = Device(rmIP)
                    self.Devices.All[rmIP] = device
                #self.Devices.All[rmIP].hostname = hostname TODO Impliment this
                self.Devices.All[rmIP].ports.append(port)                    
            except KeyboardInterrupt:
                print("[ UKI ] - User Keyboard Interupt")
                exit()
            except TimeoutError:
                pass
            except Exception as e:
                #print(e)
                pass
            start += 1
        self.running -= 1
