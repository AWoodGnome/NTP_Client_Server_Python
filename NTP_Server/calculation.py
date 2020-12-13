from NTP import NTP

class calculation:
    def __init__(self):
        self.precition = 2**32

    def system_to_ntp_time(self, timestamp):
        return timestamp + NTP().NTP_DELTA

    def _to_int(self, timestamp):
        return int(timestamp)

    def _to_frac(self, timestamp):
        return int(abs(timestamp - _to_int(timestamp)) * self.precition)

    def _to_time(self, integ, frac):
        return integ + float(frac) / self.precition

