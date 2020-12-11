#!/usr/bin/env python
from contextlib import closing
from socket import socket, AF_INET, SOCK_DGRAM
import struct, time

NTP_PACKET_FORMAT = "!12I"
NTP_Unix_DELTA = 2208988800 #Seconds between 1900-01-01 (NTP-timestamp) and 1970-01-01 (Unix timestamp)
NTP_QUERY = b'\x1b' + 47 * b'\0'  
host='ptbtime1.ptb.de'
port=123
packetsize=1024
precition = 2**32
NTP_Structure = {0: "Root Delay",
                 1: "Root Dispersion",
                 2: "Reference Identifier",
                 3: "Reference Timestamp Seconds",
                 4: "Reference Timestamp Fraction",
                 5: "Originate Timestamp Seconds",
                 6: "Originate Timestamp Fraction",
                 7: "Receive Timestamp Seconds",
                 8: "Receive Timestamp Fraction",
                 9: "Transmit Timestamp Seconds",
                10: "Transmit Timestamp Fraction"}

def get_ntp(host, port):
    with closing(socket( AF_INET, SOCK_DGRAM)) as s:
        s.sendto(NTP_QUERY, (host, port))
        msg, address = s.recvfrom(packetsize)
    unpacked = struct.unpack(NTP_PACKET_FORMAT, msg[0:struct.calcsize(NTP_PACKET_FORMAT)])
    intpart=unpacked[10]
    floatpart=float(unpacked[11]) / precition
    NTP_time = intpart + floatpart
    Unix_time = NTP_time - NTP_Unix_DELTA
    iso_time = time.ctime(Unix_time).replace("  ", " ")
    iso_time = iso_time[-4:]+" "+ iso_time[4:-4]

    for section in range(0,11):
        print(NTP_Structure[section] + " : " + str(unpacked[section]))
    print("NTP-timestamp:"+str(NTP_time))
    print("Unix-timestamp:"+str(Unix_time))
    print("NTP-timestamp:"+str(iso_time))

if __name__ == "__main__":
    get_ntp(host, port)
