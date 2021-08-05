from inspect import isclass
import re
from pyparsing import Word, nums, Combine, alphas, Literal, ZeroOrMore, Group,Suppress,ParseException

''''字典转Object'''
class DictToObject(dict):
    def __init__(self, *args, **kwargs):
        super(DictToObject, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        value = self[key]
        if isinstance(value, dict):
            value = DictToObject(value)
        return value

'''Object转字典'''
class ObjectToDict():
    _functions_ = {}

    def __init__(self, newClassFunc):
        ([self._functions_.update({str(key): newClassFunc().__class__.__dict__[str(
            key)]}) for key in newClassFunc().__class__.__dict__ if not key.startswith('_')])

    def dict(self):
        return self._functions_

class func:
    def run(**kw):
        return('hello world!')
        
    def set(**kw):
        print('set func')
        return(kw)
        
class Commander:
    cmds = ['admin','user']
    token_list = []
    cmd_keyword = ''
    cmd_auth = ''
    cmd_sub = ''
    cmd_obj = []
    #cmd_op = []
    cmd_value = []
    
    SUCCESS = 1
    ERROR = -1
    
    endFlag = Literal(';')
    dot_flag = Literal('.')
    equal_flag = Literal('=')
    space_flag = Literal(' ')
    value_field = Word(alphas+nums)
    string_field = Word(alphas,max=8)
    
    def __init__(self,func_class,cmd_keyword='>'):
        self.cmd_keyword = cmd_keyword
        self.start_flag = Literal(cmd_keyword)
        self.regex_equal = Group(
                ZeroOrMore(
                    ZeroOrMore(Suppress(self.space_flag))
                    +self.string_field+self.equal_flag\
                    +ZeroOrMore(Suppress(self.space_flag))+self.value_field)
                )
        self.regex_main = self.start_flag\
            +Group(self.string_field+Combine(self.dot_flag+self.string_field))\
            +self.regex_equal\
            +self.endFlag
        if isclass(func_class):
            self.func = ObjectToDict(func).dict()
        else:
            self.func = None
    
    def Regex(self,regex):
        self.regex_main = regex
        return self
    
    def Func(self,func):
        if isclass(func):
            self.func = ObjectToDict(func).dict()
            return self
        return  None
        
    def Parse(self,string):
        try:
            self.token_list =  self.regex_main.parseString(string).asList()
            if self.cmd_keyword != self.token_list[0]:
                return self.ERROR,ParseException
            self.cmd_auth= self.token_list[1][0]
            self.cmd_sub = self.token_list[1][1][1::]
            if self.token_list[2] != []:
                num = 3
                equal_count = int(len(self.token_list[2])/num)
                for i in range(equal_count):
                    self.cmd_obj.append(self.token_list[2][0+num*i])
                    #self.cmd_op.append(self.token_list[2][1+num*i])
                    self.cmd_value.append(self.token_list[2][2+num*i])
            return self.SUCCESS,self.token_list
        except ParseException as exception:
            return self.ERROR,exception
        
    def Do(self):
        if self.token_list == []:
            return self.ERROR,'cmd list is []'
        if self.cmd_auth in self.cmds:
            if self.cmd_sub in self.func:
                if self.func != None:
                    kw = {
                        'cmdauth':self.cmd_auth,
                        'func':self.cmd_sub,
                        'kw':{}
                    }
                    if self.cmd_obj != [] and self.cmd_value != []:  #改成用字典形式的存储
                        kw['kw'] = dict(zip(self.cmd_obj,self.cmd_value))
                    result = self.SUCCESS,self.func[self.cmd_sub](**kw)
                    self.token_list = []
                    self.cmd_auth = ''
                    self.cmd_sub = ''
                    self.cmd_obj = []
                    self.cmd_value = []
                    return result
        return self.ERROR,None



if __name__ == '__main__':
    commander = Commander(func_class=func)
    cmd = '>admin.set;'
    status,token_list=commander.Parse(cmd)
    print(commander.Do())
