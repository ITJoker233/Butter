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
