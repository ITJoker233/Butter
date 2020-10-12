
class Authoritys():
    superAdmin = 1000
    groupOwner = 200
    admin = 100
    user = 10
    guest = 1
    blackUser = -1
    enable = 1
    disenable = -1

def verifyAuthority(authorityNum):
    def verify(func):
        def inner(*args,**kwargs):
            if 'permit' in kwargs:
                if kwargs['permit'] >= authorityNum:
                    return func(*args,**kwargs)
                else:
                    return {'data':'','messageType':0,'base64':False,'message':f'没有权限','status':-1}
            raise Exception("Invalid Kwargs! There is no permit Parameter!")
        return inner
    return verify
