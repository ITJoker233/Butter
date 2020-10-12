import time

''''时间戳转日期'''
class Date:
    def __init__(self,timestamp):
        self.timestamp = timestamp
    
    def parse(self,format='%Y-%M-%d'):
        return str(time.strftime(format, time.localtime(self.timestamp)))