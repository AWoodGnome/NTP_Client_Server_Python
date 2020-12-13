class NTP:
    import datetime, time
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
                          3 : "client",
                          4 : "server",
                          5 : "broadcast",
                          6 : "reserved for NTP control messages",
                          7 : "reserved for private use",
                         }
    LEAP_TABLE = {0 : "no warning",
                          1 : "last minute has 61 seconds",
                          2 : "last minute has 59 seconds",
                          3 : "alarm condition (clock not synchronized)",
                        }

