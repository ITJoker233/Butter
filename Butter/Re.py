import re

class Pattern(object):
    Date = '^\d{4}-\d{1,2}-\d{1,2}'
    Number = '^[0-9]+$'
    Chinese = '^[\u4e00-\u9fa5]+$'
    English = '^[a-zA-Z]+$'
    Email = '^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$'
    Telephone = '^(13[0-9]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\\d{8}$'
    IdCard = '^\d{8,18}|[0-9x]{8,18}|[0-9X]{8,18}?$'
    Url = '[a-zA-z]+://[^\s]*'
    Ipaddress = '((?:(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|[01]?\\d?\\d))'
    Username = '^[a-zA-Z][a-zA-Z0-9_]{4,15}$'
    Password = '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,10}$'

def get(pattern,text):
    return re.findall(pattern,text)

def match(pattern,text):
    return re.match(pattern,text)

def sub(pattern,text,newText):
    return re.sub(pattern,text,newText)

def split(pattern,text):
    return re.split(pattern,text)

def search(pattern,text):
    return re.search(pattern,text)

def isDate(text):
    return match(Pattern().Date,text)

def isNumber(text):
    return match(Pattern().Number,text)

def isChinese(text):
    return match(Pattern().Chinese,text)

def isEnglish(text):
    return match(Pattern().English,text)

def isEmail(text):
    return match(Pattern().Email,text)

def isTelephone(text):
    return match(Pattern().Telephone,text)

def isIdCard(text):
    return match(Pattern().IdCard,text)

def isUrl(text):
    return match(Pattern().Url,text)

def isIpAddress()
    return match(Pattern().IpAddress,text)

def checkUsername(text)
    return match(Pattern().Username,text)

def checkPassword(text):
    return match(Pattern().Username,text)
