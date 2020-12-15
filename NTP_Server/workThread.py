import threading, queue
from ntp_server import ntp_server
from NTPPacket import NTPPacket

class WorkThread(threading.Thread):
    def __init__(self,socket):
        threading.Thread.__init__(self)
        self.socket = socket
    def run(self):
        while True:
            if ntp_server().getStopFlag() == True:
                print("WorkThread Ended")
                break
            try:
                taskQueue = ntp_server().getTaskQueue()
                data, addr, recvTimestamp = taskQueue.get(timeout=1)
                taskBool = True
            except queue.Empty:
                taskBool = False
                continue
            if taskBool == True:
                recvPacket = NTPPacket()
                recvPacket.from_data(data)
                timeStamp_high, timeStamp_low = recvPacket.GetTxTimeStamp()
                print(5)
                sendPacket = NTPPacket(version=3, mode=4)
                sendPacket.stratum = 2
                sendPacket.poll = 10
                sendPacket.ref_timestamp = recvTimestamp-5
                sendPacket.SetOriginTimeStamp(timeStamp_high,timeStamp_low)
                sendPacket.recv_timestamp = recvTimestamp
                sendPacket.tx_timestamp = system_to_ntp_time(time.time())
                socket.sendto(sendPacket.to_data(),addr)
                print("Sended to %s:%d" % (addr[0],addr[1]))
