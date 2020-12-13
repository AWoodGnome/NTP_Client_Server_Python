class ntp_server():
    def __init__(self):
        import queue
        self.precition = 2**32
        self.stopFlag = False
        self.host = "127.0.0.1"
        self.port = 5000
        self.taskQueue = queue.Queue()

    def getStopFlag(self):
        return self.stopFlag

    def setStopFlag(self,setting):
        if setting is True or setting is False:
            self.stopFlag = setting
        else:
            print(str(setting) + " is not allowed")

    def getTaskQueue(self):
        return self.taskQueue

    def server(self):
        import datetime, socket, struct, time, select
        from recvThread import RecvThread
        from workThread import WorkThread

        socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        socket.bind((self.host, self.port))
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
                self.setstopFlag(True)
                recvThread.join()
                workThread.join()
                socket.close()
                print("Exited")
                break
