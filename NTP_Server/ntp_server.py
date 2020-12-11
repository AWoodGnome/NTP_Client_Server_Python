import datetime, socket, struct, time, queue, threading, select

precition = 2**32
taskQueue = queue.Queue()
stopFlag = False

def system_to_ntp_time(timestamp):
    return timestamp + NTP.NTP_DELTA

def _to_int(timestamp):
    return int(timestamp)

def _to_frac(timestamp):
    return int(abs(timestamp - _to_int(timestamp)) * precition)

def _to_time(integ, frac):
    return integ + float(frac) / precition

class NTPException(Exception):
    pass

class NTP:
    _SYSTEM_EPOCH = datetime.date(*time.gmtime(0)[0:3])
    _NTP_EPOCH = datetime.date(1900, 1, 1)
    NTP_DELTA = (_SYSTEM_EPOCH - _NTP_EPOCH).days * 24 * 3600
    REF_ID_TABLE = {'DNC' : "DNC routing protocol",
                    'NIST' : "NIST public modem",
                    'TSP' : "TSP time protocol",
                    'DTS' : "Digital Time Service",
                    'ATOM' : "Atomic clock (calibrated)",
                    'VLF' : "VLF radio (OMEGA, etc)",
                    'callsign' : "Generic radio",
                    'LORC' : "LORAN-C radionavidation",
                    'GOES' : "GOES UHF environment satellite",
                    'GPS' : "GPS UHF satellite positioning",
                    }
    STRATUM_TABLE = {0 : "unspecified",
                     1 : "primary reference"
                     }
    MODE_TABLE = {0 : "unspecified",
                  1 : "symmetric active",
                  2 : "symmetric passive",
                3: "client",
        4: "server",
        5: "broadcast",
        6: "reserved for NTP control messages",
        7: "reserved for private use",
    }
    LEAP_TABLE = {
        0: "no warning",
        1: "last minute has 61 seconds",
        2: "last minute has 59 seconds",
        3: "alarm condition (clock not synchronized)",
    }

class NTPPacket:
    _PACKET_FORMAT = "!B B B b 11I"

    def __init__(self, version=2, mode=3, tx_timestamp=0):
        self.leap = 0
        self.version = version
        self.mode = mode
        self.stratum = 0
        self.poll = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.ref_id = 0
        self.ref_timestamp = 0
        self.orig_timestamp = 0
        self.orig_timestamp_high = 0
        self.orig_timestamp_low = 0
        self.recv_timestamp = 0
        self.tx_timestamp = tx_timestamp
        self.tx_timestamp_high = 0
        self.tx_timestamp_low = 0
        
    def to_data(self):
        try:
            packed = struct.pack(NTPPacket._PACKET_FORMAT,
                (self.leap << 6 | self.version << 3 | self.mode),
                self.stratum,
                self.poll,
                self.precision,
                _to_int(self.root_delay) << 16 | _to_frac(self.root_delay, 16),
                _to_int(self.root_dispersion) << 16 |
                _to_frac(self.root_dispersion, 16),
                self.ref_id,
                _to_int(self.ref_timestamp),
                _to_frac(self.ref_timestamp),
                self.orig_timestamp_high,
                self.orig_timestamp_low,
                _to_int(self.recv_timestamp),
                _to_frac(self.recv_timestamp),
                _to_int(self.tx_timestamp),
                _to_frac(self.tx_timestamp))
        except struct.error:
            raise NTPException("Invalid NTP packet fields.")
        return packed

    def from_data(self, data):
        try:
            unpacked = struct.unpack(NTPPacket._PACKET_FORMAT,
                    data[0:struct.calcsize(NTPPacket._PACKET_FORMAT)])
        except struct.error:
            raise NTPException("Invalid NTP packet.")

        self.leap = unpacked[0] >> 6 & 0x3
        self.version = unpacked[0] >> 3 & 0x7
        self.mode = unpacked[0] & 0x7
        self.stratum = unpacked[1]
        self.poll = unpacked[2]
        self.precision = unpacked[3]
        self.root_delay = float(unpacked[4])/2**16
        self.root_dispersion = float(unpacked[5])/2**16
        self.ref_id = unpacked[6]
        self.ref_timestamp = _to_time(unpacked[7], unpacked[8])
        self.orig_timestamp = _to_time(unpacked[9], unpacked[10])
        self.orig_timestamp_high = unpacked[9]
        self.orig_timestamp_low = unpacked[10]
        self.recv_timestamp = _to_time(unpacked[11], unpacked[12])
        self.tx_timestamp = _to_time(unpacked[13], unpacked[14])
        self.tx_timestamp_high = unpacked[13]
        self.tx_timestamp_low = unpacked[14]

    def GetTxTimeStamp(self):
        return (self.tx_timestamp_high,self.tx_timestamp_low)

    def SetOriginTimeStamp(self,high,low):
        self.orig_timestamp_high = high
        self.orig_timestamp_low = low

class RecvThread(threading.Thread):
    def __init__(self,socket):
        threading.Thread.__init__(self)
        self.socket = socket
    def run(self):
        global taskQueue, stopFlag
        while True:
            if stopFlag == True:
                print("RecvThread Ended")
                break
            rlist,wlist,elist = select.select([self.socket],[],[],1);
            if len(rlist) != 0:
                print("Received %d packets" % len(rlist))
                for tempSocket in rlist:
                    try:
                        data,addr = tempSocket.recvfrom(1024)
                        recvTimestamp = recvTimestamp = system_to_ntp_time(time.time())
                        taskQueue.put((data,addr,recvTimestamp))
                    except socket.error:
                        print(msg)

class WorkThread(threading.Thread):
    def __init__(self,socket):
        threading.Thread.__init__(self)
        self.socket = socket
    def run(self):
        global taskQueue, stopFlag
        while True:
            if stopFlag == True:
                print("WorkThread Ended")
                break
            try:
                data,addr,recvTimestamp = taskQueue.get(timeout=1)
                recvPacket = NTPPacket()
                recvPacket.from_data(data)
                timeStamp_high,timeStamp_low = recvPacket.GetTxTimeStamp()
                sendPacket = NTPPacket(version=3,mode=4)
                sendPacket.stratum = 2
                sendPacket.poll = 10
                sendPacket.ref_timestamp = recvTimestamp-5
                sendPacket.SetOriginTimeStamp(timeStamp_high,timeStamp_low)
                sendPacket.recv_timestamp = recvTimestamp
                sendPacket.tx_timestamp = system_to_ntp_time(time.time())
                socket.sendto(sendPacket.to_data(),addr)
                print("Sended to %s:%d" % (addr[0],addr[1]))
            except queue.Empty:
                continue
                
listenIp = "192.168.2.101"
listenPort = 5000
socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket.bind((listenIp,listenPort))
print("local socket: ", socket.getsockname())
recvThread = RecvThread(socket)
recvThread.start()
workThread = WorkThread(socket)
workThread.start()

while True:
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting...")
        stopFlag = True
        recvThread.join()
        workThread.join()
        socket.close()
        print("Exited")
        break