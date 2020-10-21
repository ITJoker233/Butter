import requests

''''http 操作类'''
class Http(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }

    def __init__(self, url='http://www.itjoker.cn', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }, params=(),data={}, verify=True):
        self.data = data
        self.url = url
        self.headers = headers
        self.verify = verify
        self.params = params

    def setHeaders(self, headers:dict):
        self.headers = headers

    def setParams(self,params):
        self.params = params

    def setData(self,data):
        self.data = data

    def setVerify(self, verify:bool):
        self.verify = verify

    def setUrl(self, url:str):
        self.url = url

    def get(self):  # http Get
        return requests.get(url=self.url, params=self.params, headers=self.headers, verify=self.verify)

    def post(self):  # http Post
        return requests.post(url=self.url, params=self.params, data=self.data, headers=self.headers, verify=self.verify)

class ApiServer:

    def __init__(self,apiObject:dict,host='0.0.0.0',port='3333'):
        self.host = host
        self.port = port
        self.apiObject = apiObject

    def run(self):
        pass

class WebServer:

    def __init__(self,host='0.0.0.0',port='80'):
        self.host = host
        self.port = port
        
    def run(self):
        pass