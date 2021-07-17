import sqlite3
import json
import os

class Sqlite3:
    conn = None
    cursor = None
    keyword = None
    STORAGE_TYPE=('TEXT','INT','REAL','BLOB','NOT NULL')
    def __init__(self, path):
        self.path = path
        if os.path.exists(self.path) and os.path.isfile(self.path):
            try:
                self.conn = sqlite3.connect(self.path)
                # conn.text_factory = lambda x: unicode(x, 'utf-8', 'ignore')
                self.conn.text_factory = str
            except sqlite3.OperationalError as e:
                print("Error:%s" % e)
        self.conn = sqlite3.connect(self.path,check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.conn.row_factory = self._dict_factory_
    
    def __del__(self):
        self.conn.close()
        
    def _dict_factory_(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def getCursor(self):
        self.cursor = self.conn.cursor()
        return self.cursor
    
    def close(self):
        self.cursor.close()
    
    def closes(self):
        self.cursor.close()
        self.conn.close()
    
    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()
    
    def execute(self,sql,isrollback=False):
        self.keyword = str(sql).split()[0]
        self.cursor.execute(sql)
        if self.keyword != 'SELECT' and not isrollback:
            self.commit()
        elif isrollback:
            self.rollback()
        return self.cursor.fetchall()

class Database:
    #STORAGE_TYPE=('TEXT','INT','REAL','BLOB','NOT NULL')
    def __init__(self,database,path='.'):
        self.database = database
        self.path = f'{path}/{database}.db'
        self.db = Sqlite3(self.path)
        self.STORAGE_TYPE = self.db.STORAGE_TYPE
        self.sql = ''
        self.val = ''
        self.keyword = ''
        self.fields = {}
        self.table = ''
        self.where = ''
        self.rollback = False
        
    def __del__(self):
        self.db.close()
    
    def __str__(self):
        return self.sql
    
    def __dict2sql_val__(self,add_k=False):
        flag = True
        temp = ''
        for k in self.fields:    
            if not add_k:
                if isinstance(self.fields[k],str):
                    self.val += temp+f'"{self.fields[k]}"'
                elif isinstance(self.fields[k],dict) or isinstance(self.fields[k],tuple):
                    self.val += temp+f'"{json.dumps(self.fields[k])}"'
                else:
                    self.val += temp+f'{self.fields[k]}'
            else:
                if isinstance(self.fields[k],str):
                    self.val += temp+f'{k} = "{self.fields[k]}"'
                elif isinstance(self.fields[k],dict) or isinstance(self.fields[k],tuple):
                    self.val += temp+f'{k} = "{json.dumps(self.fields[k])}"'
                else:
                    self.val += temp+f'{k} = {self.fields[k]}'
            if flag:
                flag=False
                temp = ', '
                
    def __dict2sql_val_v2__(self):
        self.val = ', '.join(f'{k}' for k in self.fields.keys())
                
    def __dict2sql_key_val__(self):
        flag = True
        temp = '\n '
        for k in self.fields:    
            self.val += temp+f'{k} {self.STORAGE_TYPE[self._cheak_key_type_(self.fields[k])]}'
            if flag:
                flag=False
                temp = ',\n '
    
    def _cheak_key_type_(self,k):
        t_dict = {
            'str':0,
            'int':1,
            'float':2,
        }
        if k == None:
            t = len(self.STORAGE_TYPE)-1
        elif type(k).__name__=='type':
            t = t_dict.get(k.__name__,3)
        else:
            t = t_dict.get(type(k).__name__,3)
        return t

    def _check_self_is_true_(self):
        if not isinstance(self.table,str) or self.table == '':
            raise('Check Table Name!')
        elif not isinstance(self.where,str) or self.where == None or (
            (self.where == '' or self.where.isspace()) and (
                self.keyword == 'UPDATE' or self.keyword == 'DELETE')
        ):
            raise('Check Where Value!')
        elif (not isinstance(self.colname,str) or self.colname == '') and (
            self.keyword == 'SELECT' and 
            len(self.where)>3):
            raise('Check Column Name Value!')
        
    def _dict2sql_(self):
        self.val=''
        if self.keyword =='UPDATE':
            self.__dict2sql_val__(True)
            self.sql = (self.template % (self.val))
        elif self.keyword =='INSERT':
            key = ', '.join(f'{k}' for k in self.fields.keys())
            self.__dict2sql_val__()
            self.sql = (self.template % (key,self.val))
        elif self.keyword == 'CREATE':
            self.__dict2sql_key_val__()
            self.sql = (self.template % (self.val))
            
    def Rollback(self,isrollback):
        self.rollback = isrollback
        return self.rollback
    
    def Table(self,table):
        self.table = table
        return self
    
    def Where(self,where):
        self.where = where
        return self
    
    def Colname(self,colname):
        self.colname = colname
        return self
    
    def execute(self,sql=None):
        if sql is not None:
            self.sql = sql
        #print(self.sql)
        data = self.db.execute(self.sql,isrollback=self.rollback)
        self.rollback = False
        self.where = ''
        self.colname = ''
        return data    

    def Create(self,**fields):
        self.fields = fields
        self.keyword = 'CREATE'
        self.template = f'{self.keyword} TABLE IF NOT EXISTS {self.table}(ID INTEGER PRIMARY KEY,%s)'
        self._dict2sql_()
        return self.execute()
    
    def Insert(self,**fields):
        self.fields = fields
        self.keyword = 'INSERT'
        self.template = f'{self.keyword} INTO {self.table}(%s) VALUES(%s)'
        self._dict2sql_()
        return self.execute()
    
    def Drop(self):
        self.fields = {}
        self.keyword = 'DROP'
        self.template = f'{self.keyword} TABLE {self.database}.{self.table}'
        return self.execute()
    
    def Delete(self):
        self.fields = {}
        self.keyword = 'DELETE'
        self._check_self_is_true_()
        self.template = f'{self.keyword} FROM {self.table} {self.where}'
        self.sql = self.template
        return self.execute()

    def Update(self,**fields):
        self.fields = fields
        self.keyword = 'UPDATE'
        self._check_self_is_true_()
        self.template = f'{self.keyword} {self.table} SET %s WHERE {self.where}'
        self._dict2sql_()
        return self.execute()

    def Get(self):
        self.fields = {}
        self.keyword = 'SELECT'
        self._check_self_is_true_()
        if len(self.where) > 3 and (('=' or '>' or '<') in self.where):
            self.template = f'{self.keyword} {self.colname} FROM {self.table} WHERE {self.where}'
        else:
            self.template = f'{self.keyword} {self.colname} FROM {self.table}'
        self.sql=self.template
        return self.execute()
    
    def Gets(self):
        self.fields = {}
        self.keyword = 'SELECT'
        self.template = f'{self.keyword} * FROM {self.table}'
        self.sql=self.template
        return self.execute()
    
    def Match(self):
        self.fields = {}
        self.keyword = 'SELECT'
        self.colname = '*'
        self._check_self_is_true_()
        self.template = f'{self.keyword} {self.where} FROM {self.table}'
        self.sql=self.template
        return self.execute()
        
    
    
'''

db = Database('test').Table('user')

#db.create(name=str,key=str)
#print(db.insert(name='jack',key='123123'))
#print(db.insert(name='tom',key='123123'))
db.Where('id=2').update()
print(db.sql)
print(db.selects())
'''