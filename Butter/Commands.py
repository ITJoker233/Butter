import re
import os
import json
try:
    from .version import version
except Exception as identifier:
    from version import version

COMMAND_DEFAULT_LEVEL = 1
COMMAND_DEFAULT_DESCRIPTION = f'当前没有描述'

class Command():
    _version_ = f'{version}'

    def __init__(self,
                _name_ = str, 
                _args_ = [],
                _keyword_ = str,
                _content_ = '',
                _level_ = COMMAND_DEFAULT_LEVEL,
                _description_ = COMMAND_DEFAULT_DESCRIPTION):
        self._name_ = _name_
        self._description_ = _description_
        self._args_ = _args_
        self._level_ = _level_
        self._keyword_ = _keyword_
        self._content_ = _content_
        self._help_ = f'描述:{self.description} 权限等级:{self.level}\nargs:{self.args}\n取args中的子命令，例:{self.keyword}{self.name}.arg xxxx\n若args为空则\n{self.keyword}{self.name}'

    @property
    def help(self):
        return self._help_

    @property
    def level(self):
        return self._level_

    @property
    def args(self):
        return self._args_

    @property
    def description(self):
        return self._description_

    @property
    def name(self):
        return self._name_

    @property
    def keyword(self):
        return self._keyword_
    
    @property
    def content(self):
        return self._content_


class Parser(Command):
    _keyword_ = '#'
    _name_ = ''
    _args_ = ''
    _content_ = ''
    _inputData_ = ''

    def __init__(self, _inputData_:str):
        self._inputData_ = _inputData_

    def set(self,_inputData_:str):
        self._inputData_ = _inputData_
        self._name_ = ''
        self._arg_ = ''
        self._content_ = ''

    def parse(self):
        self._keyword_ = self._inputData_[0:1]
        content = re.search(re.compile(r'[ ]([^ ]+)'),self._inputData_)
        args = re.search(re.compile(r'[\.]([^(\. )]+)'),self._inputData_)
        name = re.search(re.compile(r'([a-zA-Z]+)'),self._inputData_)
        if content:
            self._content_ = content.groups()[0]
        if args:
            self._args_ = args.groups()[0]
        if name:
            self._name_ = name.groups()[0]
        return Command(_name_ = self._name_,_args_ =  self._args_,_keyword_= self._keyword_,_content_ = self._content_)


class Manager():
    __config = {}

    @property
    def config(self):
        return self.__config

    def add(self, cmd):
        if hasattr(cmd, 'name') and hasattr(cmd, 'level') and hasattr(cmd, 'args') and hasattr(cmd, 'description') and hasattr(cmd, 'help'):
            self.__config[str(cmd.name)] = {
                'level': cmd.level,
                'args': cmd.args,
                'description': cmd.description,
                'help':cmd.help
            }
        else:
            print('add ERROR!')
            raise Exception

    def delete(self, cmd):
        if hasattr(cmd, 'name'):
            del self.__config[str(cmd.name)]
        else:
            print('remove ERROR!')
            raise Exception


''' Parser的使用方法
input_data = '#reload.ls 233'
cp = Parser(input_data)
cmd  = cp.parse()
print(cmd.args)
'''
'''
cp.set('.baidu 123')
cmd = cp.parse()
print(cmd.__dict__)
'''
'''Manager 的使用方法
cmdManager = Manager('commands.json')
myKeyword = '#'
cmd_list = [
    Command('stop', ['now', 'settime'], myKeyword,'', 5, '停止命令'),
    Command('reload', ['now', 'settime'], myKeyword,'', 5, '重载命令'),
    Command('cmd', ['ls', 'cat','curl'], myKeyword,'', 5, '系统命令'),
    Command('user', ['up', 'down','me'], myKeyword,'', 5, '用户命令'),
    Command('group', ['enable', 'disenable'], myKeyword,'', 5, '群组命令')
]
for cmd in cmd_list:
    cmdManager.add(cmd)
    print(cmd.args)
print(cmdManager.config)
'''