import json
import base64
import os

'''文件操作类'''
class File(object):
    filePath = str
    encoding = str

    def __init__(self, filePath:str, encoding='utf-8'):
        self.filePath = filePath
        self.encoding = encoding

    def __open(self, mode:str):
        return open(self.filePath, mode, encoding=self.encoding)

    def touch(self):
        f = self.__open('w')
        f.close()

    def read(self,mode = 'r+'):
        try:
            with self.__open(mode) as file:
                result = file.read()
        except Exception as identifier:
            print(identifier)
            return False
        return result
    
    def write(self, data,mode = 'w+'):
        try:
            with self.__open(mode) as file:
                file.write(data)
        except Exception as identifier:
            print(identifier)
            return False
        return True

    def isExists(self):
        return os.path.exists(self.filePath)

    def json(self):
        try:
            with self.__open('r') as file:
                result = file.read()
        except Exception as identifier:
            print(identifier)
            return False
        return json.loads(result)

    def b64encode(self):
        try:
            with self.__open('rb') as file:
                result = file.read()
        except Exception as identifier:
            print(identifier)
            return False
        return base64.b64encode(result).decode(self.encoding)
    
    def b64decode(self):
        try:
            with self.__open('r') as file:
                result = file.read()
        except Exception as identifier:
            print(identifier)
            return False
        return base64.b64decode(result).decode(self.encoding)

    ''''获取指定目录下的指定格式的所有文件'''
    def getFiles(self, format_): return [i.split('.')[0] for i in os.listdir(self.filePath)if i.endswith(f'.{format_}')]

    ''''获取指定目录下的所有文件夹'''
    def getDirs(self): return [i for i in os.listdir(self.filePath) if '.' not in i]

    ''''新建文件夹'''
    def createDir(self): return os.makedirs(self.filePath) if not os.path.exists(self.filePath) else False