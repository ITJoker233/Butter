import re

input_data = '#reload.ls 233abc'
print(re.split('[#]?([a-zA-Z]+)[\. ]([a-zA-Z0-9]+)',input_data))
input_data = '#reload.ls'
print(re.split('#([a-zA-Z]+)[\. ]([a-zA-Z0-9]+)',input_data))
input_data = '#reload.'
print(re.split('#([a-zA-Z]+)[\. ]([a-zA-Z0-9]+)',input_data))
input_data = '#reload'
print(re.split('#([a-zA-Z]+)[\. ]([a-zA-Z0-9]+)',input_data))
input_data = '#reload.233'
print(re.split('#([a-zA-Z]+)[\. ]([a-zA-Z0-9]+)',input_data))
input_data = '#reload 233'
print(re.split('#([a-zA-Z]+)[\. ]([a-zA-Z0-9]+)',input_data))