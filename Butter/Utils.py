import os
import time
import json
import base64
import requests

''''二分查找'''
def binarySearch(alist, item):
    first = 0
    last = len(alist) - 1
    while first <= last:
        mid_point = (first+last)//2
        if alist[mid_point] == item:
            return True
        elif item < alist[mid_point]:
            last = mid_point - 1
        else:
            first = mid_point + 1
    return False

''''字典转Object'''
class DictToObject(dict):
    def __init__(self, *args, **kwargs):
        super(DictToObject, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        value = self[key]
        if isinstance(value, dict):
            value = DictToObject(value)
        return value

''''时间戳转日期'''
Date = lambda ts, ft='%Y-%M-%d': str(time.strftime(ft, time.localtime(ts)))

''''元组去重'''
def deleteDuplicate(l): return [dict(t) for t in set([tuple(d.items()) for d in li])]

''''获取指定目录下的指定格式的所有文件'''
def getFileList(path, format_): return [i.split('.')[0] for i in os.listdir(path)if i.endswith(f'.{format_}')]

''''获取指定目录下的所有文件夹'''
def getDirList(path): return [i for i in os.listdir(path) if '.' not in i]

''''新建文件夹'''
def createDir(path): return os.makedirs(path) if not os.path.exists(path) else False

''''http 操作类'''
class Http(object):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }

    def __init__(self, url='http://www.itjoker.cn', headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36 Edg/83.0.478.54'
    }, params='', verify=True):

        self.url = url
        self.headers = headers
        self.verify = verify
        self.params = params

    def setHeaders(self, headers:dict):
        self.headers = headers

    def setParams(params):
        self.params = params

    def setVerify(self, verify:bool):
        self.verify = verify

    def setUrl(self, url:str):
        self.url = url

    def get(self):  # http Get
        return requests.get(url=self.url, params=self.params, headers=self.headers, verify=self.verify)

    def post(self, postData:str):  # http Post
        return requests.post(url=self.url, params=self.params, data=postData, headers=self.headers, verify=self.verify)

'''文件操作类'''
class File(object):
    filePath = str
    encoding = str

    def __init__(self, filePath:str, encoding='utf-8'):
        self.filePath = filePath
        self.encoding = encoding

    def __open(self, mode:str):
        return open(self.filePath, mode, encoding=self.encoding)

    def read(self,mode = 'r+'):
        try:
            with self.__open(mode) as file:
                result = file.read()
        except Exception as identifier:
            return False
        return result

    def isExists(self):
        return os.path.exists(self.filePath)

    def json(self):
        try:
            with self.__open('r') as file:
                result = file.read()
        except Exception as identifier:
            return False
        return json.loads(result)

    def base64(self):
        try:
            with self.__open('rb') as file:
                result = file.read()
        except Exception as identifier:
            return False
        return base64.b64encode(result).decode()

    def write(self, data,mode = 'w+'):
        try:
            with self.__open(mode) as file:
                file.write(data)
        except Exception as identifier:
            return False
        return True

class Functions():
    _functions_ = {}

    def __init__(self, newClassFunc):
        ([self._functions_.update({str(key): newClassFunc().__class__.__dict__[str(
            key)]}) for key in newClassFunc().__class__.__dict__ if not key.startswith('_')])

    def dict(self):
        return self._functions_

'''Functions
class myfunction():
    
    def __init__(self):
        print()
    
    def baidu():
        return 'ok'

print(Functions(myfunction).dict())
'''

#print(Functions().dict()['baidu']())
#print(list(map(lambda x,y:x+y,[1],[1]))[0])
