import re
import sys
import json
import base64
import hashlib
from xml.sax import parseString,ContentHandler 
try:
    from .Utils import Http,File
except Exception as identifier:
    from Utils import Http,File


class MessageType():

    _functions_ = {}
    XML = 1
    JSON = 2
    TEXT = 3
    IMAGE = 4
    VOICE = 5
    TEXT_IMAGE = 7
    UNKNOWN = 0
    def __init__(self):
        ([self._functions_.update({str(key): self.__class__.__dict__[str(
            key)]}) for key in self.__class__.__dict__ if not key.startswith('_')])

    def dict(self):
        del self._functions_[str(sys._getframe().f_code.co_name)]
        return self._functions_

class Messages():
    msg = {}
    msgType = MessageType().dict()
    fileType = {
        'jpg':'IMAGE',
        'jpeg':'IMAGE',
        'png':'IMAGE',
        'bmp':'IMAGE',
        'gif':'IMAGE',
        'wav':'VOICE',
        'mp3':'VOICE',
        'wma':'VOICE',
        'txt':'TEXT',
        'json':'JSON',
        'xml':'XML',
    }
    file_head_type = {  
        'FFD8FF': 'jpeg',
        '89504E': 'png',
        '47494638':'gif',
        '424D':'bmp',
        '3C3F78':'xml',
        'FFFE3C00':'xml',
        '49492A00 ':'tif',
        '4D4D002A':'tif',
        '4D4D2A':'tif',
        '4D4D002B':'tif',
        '49443303':'mp3',
        'FFFB50':'mp3',
        '3026B2':'wma',
        '52494646':'wav',
        '57415645':'wav'
    }  
    get_file_regex = re.compile(r'\.([jpg|jpeg|png|bmp|gif|wav|mp3|wma|txt|json|xml]+)')
    is_url_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    is_xml_regex = re.compile(r'<\?xml.*')


    def __init__(self,inputData:str,is_cache = False):
        self.msg['TYPE'] = 0
        self.msg['XML'] = ''
        self.msg['JSON'] = ''
        self.msg['TEXT'] = ''
        self.msg['IMAGE'] = ''
        self.msg['VOICE'] = ''
        self.msg['TEXT_IMAGE'] = ''
        self.msg['RAW'] = inputData
        self.msg['BASE64'] = False

        def judgeFileType(self,data):
            import struct
            def bytes2hex(bytes):  
                num = len(bytes)  
                hexstr = u""  
                for i in range(num):  
                    t = u"%x" % bytes[i]  
                    if len(t) % 2:  
                        hexstr += u"0"
                    hexstr += t  
                return hexstr.upper()  
            ftype = 'UNKNOWN'
            for hcode in self.file_head_type.keys():
                numOfBytes = int(len(hcode) / 2) # needed byte length
                hbytes = struct.unpack_from("B"*numOfBytes, (data[0:numOfBytes])) # B is byte
                f_hcode = bytes2hex(hbytes)  
                if f_hcode == hcode:  
                    ftype = tl[hcode]  
                    break
            return ftype

        '''need to fix Optimization'''
        def judgeData(self,inputData):
            is_url = re.match(self.is_url_regex,inputData)
            url_file_type = re.findall(self.get_file_regex,inputData)
            url_file_type = [x for x in url_file_type if x in self.fileType]
            while(self.msg['TYPE'] != ''):
                if(is_url):
                    url_file_type = url_file_type[0] if len(url_file_type)>0 else str(url_file_type)
                    if url_file_type in self.fileType:
                        self.msg['TYPE'] = self.msgType[self.fileType[url_file_type]]
                        self.msg[self.fileType[url_file_type]] = inputData
                    else:
                        self.msg['TYPE'] = MessageType().TEXT      
                    break
                else:
                    if url_file_type and File.isExists(inputData):
                        self.msg['TYPE'] = self.msgType[self.fileType[url_file_type]]
                        binData = self.__read(inputData,'rb')
                        self.msg[self.fileType[url_file_type]] = base64.b64encode(binData)
                        self.msg['BASE64'] = True
                        break
                    if self.__isXML(inputData):
                        self.msg['XML'] = (inputData)
                        self.msg['TYPE'] = MessageType().XML
                        break
                    try:
                        json.loads(inputData)
                        self.msg['JSON'] = json.dumps(inputData)
                        self.msg['TYPE'] = MessageType().JSON
                        break
                    except Exception as identifier:
                        pass
                    try:
                        unknownData = base64.b64decode(inputData)
                        ftype = judgeFileType(unknownData)
                        self.msg['TYPE'] = self.msgType[ftype]
                        if self.msg['TYPE']:
                            self.msg[self.fileType[ftype]] = inputData
                        break
                    except Exception as identifier:
                        pass
                    self.msg['TYPE'] = MessageType().TEXT
                    self.msg['TEXT'] = inputData
                    break
        judgeData(self,inputData)

    def __isXML(self,data):
        matchData = re.search(self.is_xml_regex,data)
        if matchData:
            return True
        return False

    def __read(self,path,mode):
        with open(path, mode) as file:
            readData = file.read()
        return readData

    @property
    def TEXT_IMAGE(self):
        return self.msg['TEXT_IMAGE']

    @property
    def TYPE(self):
        return self.msg['TYPE']

    @property
    def JSON(self):
        return self.msg['JSON']

    @property
    def XML(self):
        return self.msg['XML']

    @property
    def IMAGE(self):
        return self.msg['IMAGE']

    @property
    def VOICE(self):
        return self.msg['VOICE']

    @property
    def TEXT(self,text:str):
        return self.msg['TEXT']
    
    @property
    def RAW(self):
        return self.msg['RAW']

    @property
    def BASE64(self):
        return self.msg['BASE64']


'''Messages
print(Messages('https://example.xxxx.com/python/xxx.json').TYPE)
'''