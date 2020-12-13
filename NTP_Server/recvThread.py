import threading, select, socket, time
from ntp_server import ntp_server
from calculation import calculation

class RecvThread(threading.Thread):
    def __init__(self,socket):
        threading.Thread.__init__(self)
        self.socket = socket
    def run(self):
        global taskQueue, stopFlag
        while True:
            if ntp_server().getStopFlag() == True:
                print("RecvThread Ended")
                break
            rlist,wlist,elist = select.select([self.socket],[],[],1);
            if len(rlist) != 0:
                print("Received %d packets" % len(rlist))
                for tempSocket in rlist:
                    try:
                        data,addr = tempSocket.recvfrom(1024)
                        recvTimestamp = recvTimestamp = calculation().system_to_ntp_time(time.time())
                        ntp_server().getTaskQueue().put((data,addr,recvTimestamp))
                    except socket.error:
                        print(msg)
