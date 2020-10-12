import os
import re
import io
import json
from typing import (
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    Mapping,
    Optional,
    Union,
    cast,
    Any,
    TypeVar, 
    Generic,
    Tuple
)
from abc import ABC, abstractmethod
from collections import OrderedDict, abc

'''
tinydb 魔改版 或 阉割版
去除了用不到的功能，如中间件，更改了一些方法名

Tinydb() = Database()

Database:{
    drops()  = drop_tables()
    drop() = drop_table()
}

Table:{ 
    #内置函数名对应
    clearCache() = clear_cache()
    inserts() = insert_multiple()
}

drop = 
'''

'''Query'''

class Operations:
    def delete(field):
        """
        Delete a given field from the document.
        """
        def transform(doc):
            del doc[field]

        return transform


    def add(field, n):
        """
        Add ``n`` to a given field in the document.
        """
        def transform(doc):
            doc[field] += n

        return transform


    def subtract(field, n):
        """
        Substract ``n`` to a given field in the document.
        """
        def transform(doc):
            doc[field] -= n

        return transform


    def set(field, val):
        """
        Set a given field to ``val``.
        """
        def transform(doc):
            doc[field] = val
        return transform


    def increment(field):
        """
        Increment a given field in the document by 1.
        """
        def transform(doc):
            doc[field] += 1
        return transform


    def decrement(field):
        """
        Decrement a given field in the document by 1.
        """
        def transform(doc):
            doc[field] -= 1
        return transform


def is_sequence(obj):
    return hasattr(obj, '__iter__')


class QueryInstance:
    def __init__(self, test: Callable[[Mapping], bool], hashval: Tuple):
        self._test = test
        self._hash = hashval

    def __call__(self, value: Mapping):
        return self._test(value)

    def __hash__(self):
        return hash(self._hash)

    def __repr__(self):
        return 'QueryImpl{}'.format(self._hash)

    def __eq__(self, other: object):
        if isinstance(other, QueryInstance):
            return self._hash == other._hash

        return False

    # --- Query modifiers -----------------------------------------------------

    def __and__(self, other: 'QueryInstance'):
        return QueryInstance(lambda value: self(value) and other(value),
                             ('and', frozenset([self._hash, other._hash])))

    def __or__(self, other: 'QueryInstance'):
        return QueryInstance(lambda value: self(value) or other(value),
                             ('or', frozenset([self._hash, other._hash])))

    def __invert__(self):
        return QueryInstance(lambda value: not self(value),
                             ('not', self._hash))


class Query(QueryInstance):

    def __init__(self):
        self._path = ()
        def notest(_):
            raise RuntimeError('Empty query was evaluated')

        super().__init__(
            test=notest,
            hashval=(None,)
        )

    def __repr__(self):
        return '{}()'.format(type(self).__name__)

    def __hash__(self):
        return super().__hash__()

    def __getattr__(self, item: str):
        query = type(self)()
        query._path = self._path + (item,)
        query._hash = ('path', query._path)

        return query

    def __getitem__(self, item: str):
        return getattr(self, item)

    def _generate_test(
            self,
            test: Callable[[Any], bool],
            hashval: Tuple,
    ):
        if not self._path:
            raise ValueError('Query has no path')

        def runner(value):
            try:
                for part in self._path:
                    value = value[part]
            except (KeyError, TypeError):
                return False
            else:
                # Perform the specified test
                return test(value)

        return QueryInstance(
            lambda value: runner(value),
            hashval
        )

    def __eq__(self, rhs: Any):
        return self._generate_test(
            lambda value: value == rhs,
            ('==', self._path, freeze(rhs))
        )

    def __ne__(self, rhs: Any):
        return self._generate_test(
            lambda value: value != rhs,
            ('!=', self._path, freeze(rhs))
        )

    def __lt__(self, rhs: Any):
        return self._generate_test(
            lambda value: value < rhs,
            ('<', self._path, rhs)
        )

    def __le__(self, rhs: Any):
        return self._generate_test(
            lambda value: value <= rhs,
            ('<=', self._path, rhs)
        )

    def __gt__(self, rhs: Any):
        return self._generate_test(
            lambda value: value > rhs,
            ('>', self._path, rhs)
        )

    def __ge__(self, rhs: Any):
        return self._generate_test(
            lambda value: value >= rhs,
            ('>=', self._path, rhs)
        )

    def exists(self):
        return self._generate_test(
            lambda _: True,
            ('exists', self._path)
        )

    def matches(self, regex: str, flags: int = 0):
        def test(value):
            if not isinstance(value, str):
                return False

            return re.match(regex, value, flags) is not None

        return self._generate_test(test, ('matches', self._path, regex))

    def search(self, regex: str, flags: int = 0):
        def test(value):
            if not isinstance(value, str):
                return False

            return re.search(regex, value, flags) is not None

        return self._generate_test(test, ('search', self._path, regex))

    def test(self, func: Callable[[Mapping], bool], *args):
        return self._generate_test(
            lambda value: func(value, *args),
            ('test', self._path, func, args)
        )

    def any(self, cond: Union[QueryInstance, List[Any]]):
        if callable(cond):
            def test(value):
                return is_sequence(value) and any(cond(e) for e in value)

        else:
            def test(value):
                return is_sequence(value) and any(e in cond for e in value)

        return self._generate_test(
            lambda value: test(value),
            ('any', self._path, freeze(cond))
        )

    def all(self, cond: Union['QueryInstance', List[Any]]):
        if callable(cond):
            def test(value):
                return is_sequence(value) and all(cond(e) for e in value)

        else:
            def test(value):
                return is_sequence(value) and all(e in value for e in cond)

        return self._generate_test(
            lambda value: test(value),
            ('all', self._path, freeze(cond))
        )

    def one_of(self, items: List[Any]):
        return self._generate_test(
            lambda value: value in items,
            ('one_of', self._path, freeze(items))
        )

    def noop(self):

        return QueryInstance(
            lambda value: True,
            ()
        )

def where(key: str):
    """
    A shorthand for ``Query()[key]``
    """
    return Query()[key]

K = TypeVar('K')
V = TypeVar('V')
D = TypeVar('D')

class LRUCache(abc.MutableMapping, Generic[K, V]):
    def __init__(self, capacity=None):
        self.capacity = capacity
        self.cache = OrderedDict()  # type: OrderedDict[K, V]

    @property
    def lru(self):
        return list(self.cache.keys())

    @property
    def length(self):
        return len(self.cache)

    def clear(self):
        self.cache.clear()

    def __len__(self):
        return self.length

    def __contains__(self, key: object):
        return key in self.cache

    def __setitem__(self, key: K, value: V):
        self.set(key, value)

    def __delitem__(self, key: K):
        del self.cache[key]

    def __getitem__(self, key):
        value = self.get(key)
        if value is None:
            raise KeyError(key)

        return value

    def __iter__(self):
        return iter(self.cache)

    def get(self, key: K, default: D = None):
        value = self.cache.get(key)
        if value is not None:
            del self.cache[key]
            self.cache[key] = value

            return value

        return default

    def set(self, key: K, value: V):
        if self.cache.get(key):
            del self.cache[key]
            self.cache[key] = value
        else:
            self.cache[key] = value
            if self.capacity is not None and self.length > self.capacity:
                self.cache.popitem(last=False)

class FrozenDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def _immutable(self, *args, **kws):
        raise TypeError('object is immutable')
    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    setdefault = _immutable
    popitem = _immutable

    def update(self, e=None, **f):
        raise TypeError('object is immutable')

    def pop(self, k, d=None):
        raise TypeError('object is immutable')

def freeze(obj):
    if isinstance(obj, dict):
        return FrozenDict((k, freeze(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        return tuple(freeze(el) for el in obj)
    elif isinstance(obj, set):
        return frozenset(obj)
    else:
        return obj


def touch(path: str, create_dirs: bool):
    if create_dirs:
        base_dir = os.path.dirname(path)
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
    with open(path, 'a'):
        pass

class Storage(ABC):
    @abstractmethod
    def read(self):

        raise NotImplementedError('To be overridden!')

    @abstractmethod
    def write(self, data: Dict[str, Dict[str, Any]]):
        raise NotImplementedError('To be overridden!')

    def close(self):
        pass

class JSONStorage(Storage):
    def __init__(self, path: str, create_dirs=False, encoding=None, access_mode='r+', **kwargs):
        super().__init__()
        self._mode = access_mode
        self.kwargs = kwargs
        if any([character in self._mode for character in ('+', 'w', 'a')]):  # any of the writing modes
            touch(path, create_dirs=create_dirs)
        self._handle = open(path, mode=self._mode, encoding=encoding)

    def close(self):
        self._handle.close()

    def read(self):
        self._handle.seek(0, os.SEEK_END)
        size = self._handle.tell()
        if not size:
            return None
        else:
            self._handle.seek(0)
            return json.load(self._handle)

    def write(self, data: Dict[str, Dict[str, Any]]):
        self._handle.seek(0)
        serialized = json.dumps(data, **self.kwargs)
        try:
            self._handle.write(serialized)
        except io.UnsupportedOperation:
            raise IOError('Cannot write to the database. Access mode is "{0}"'.format(self._mode))
        self._handle.flush()
        os.fsync(self._handle.fileno())
        self._handle.truncate()

class Document(dict):
    def __init__(self, value: Mapping, doc_id: int):
        super().__init__(value)
        self.doc_id = doc_id

class Table:
    document_class = Document
    document_id_class = int
    query_cache_class = LRUCache
    default_query_cache_capacity = 10

    def __init__(
        self,
        storage: Storage,
        name: str,
        cache_size: int = default_query_cache_capacity
    ):
        self._storage = storage
        self._name = name
        self._query_cache = self.query_cache_class(capacity=cache_size)
        self._next_id = None

    def __repr__(self):
        args = [
            'name={!r}'.format(self.name),
            'total={}'.format(len(self)),
            'storage={}'.format(self.storage),
        ]
        return '<{} {}>'.format(type(self).__name__, ', '.join(args))

    def __len__(self):
        tables = self.storage.read()
        if tables is None:
            return 0

        try:
            return len(tables[self.name])
        except KeyError:
            return 0

    def __iter__(self):
        for doc_id, doc in self._read_table().items():
            yield self.document_class(doc, doc_id)

    @property
    def storage(self):
        return self._storage

    @property
    def name(self):
        return self._name

    def insert(self, document: Mapping):
        if not isinstance(document, Mapping):
            raise ValueError('Document is not a Mapping')
        if isinstance(document, Document):
            doc_id = document.doc_id
            self._next_id = None
        else:
            doc_id = self._get_next_id()
        def updater(table: dict):
            assert doc_id not in table, 'doc_id '+str(doc_id)+' already exists'
            table[doc_id] = dict(document)
        self._update_table(updater)
        return doc_id

    def inserts(self, documents: Iterable[Mapping]):
        doc_ids = []
        def updater(table: dict):
            for document in documents:
                if not isinstance(document, Mapping):
                    raise ValueError('Document is not a Mapping')
                doc_id = self._get_next_id()
                doc_ids.append(doc_id)
                table[doc_id] = dict(document)
        self._update_table(updater)
        return doc_ids

    def delete(
        self,
        cond = None,
        doc_ids= None,
    ):
        if cond is None and doc_ids is None:
            raise RuntimeError('Use truncate() to remove all documents')

        if cond is not None:
            removed_ids = []
            def updater(table: dict):
                _cond = cast('Query', cond)
                for doc_id in list(table.keys()):
                    if _cond(table[doc_id]):
                        removed_ids.append(doc_id)
                        table.pop(doc_id)
            self._update_table(updater)
            return removed_ids
        if doc_ids is not None:
            removed_ids = list(doc_ids)
            def updater(table: dict):
                for doc_id in removed_ids:
                    table.pop(doc_id)
            self._update_table(updater)
            return removed_ids

        raise RuntimeError('This should never happen')


    def truncate(self):
        self._update_table(lambda table: table.clear())
        self._next_id = None

    def update(
        self,
        fields,
        cond= None,
        doc_ids = None,
    ):
        if callable(fields):
            def perform_update(table, doc_id):
                fields(table[doc_id])
        else:
            def perform_update(table, doc_id):
                table[doc_id].update(fields)
        if doc_ids is not None:
            updated_ids = list(doc_ids)
            def updater(table: dict):
                for doc_id in updated_ids:
                    perform_update(table, doc_id)
            self._update_table(updater)

            return updated_ids

        elif cond is not None:
            updated_ids = []
            def updater(table: dict):
                _cond = cast('Query', cond)
                for doc_id in list(table.keys()):
                    if _cond(table[doc_id]):
                        updated_ids.append(doc_id)
                        perform_update(table, doc_id)
            self._update_table(updater)
            return updated_ids
        else:
            updated_ids = []
            def updater(table: dict):
                for doc_id in list(table.keys()):
                    updated_ids.append(doc_id)
                    perform_update(table, doc_id)
            self._update_table(updater)
            return updated_ids

    def search(self, cond):
        if cond in self._query_cache:
            docs = self._query_cache.get(cond)
            if docs is not None:
                return docs[:]
        docs = [doc for doc in self if cond(doc)]
        self._query_cache[cond] = docs[:]
        return docs

    def get(
        self,
        cond = None,
        doc_id = None,
    ):
        if doc_id is not None:
            table = self._read_table()
            raw_doc = table.get(doc_id, None)
            if raw_doc is None:
                return None
            return self.document_class(raw_doc, doc_id)

        elif cond is not None:
            for doc in self:
                if cond(doc):
                    return doc
            return None
        raise RuntimeError('You have to pass either cond or doc_id')

    def contains(
        self,
        cond = None,
        doc_id = None
    ):
        if doc_id is not None:
            return self.get(doc_id=doc_id) is not None

        elif cond is not None:
            return self.get(cond) is not None

        raise RuntimeError('You have to pass either cond or doc_id')

    def upsert(self, document: Mapping, cond):
        updated_docs = self.update(document, cond)
        if updated_docs:
            return updated_docs
        return [self.insert(document)]

    def count(self, cond):
        return len(self.search(cond))

    def all(self):
        return list(iter(self))

    def clearCache(self):
        self._query_cache.clear()

    def _get_next_id(self):
        if self._next_id is not None:
            next_id = self._next_id
            self._next_id = next_id + 1

            return next_id
        table = self._read_table()
        if not table:
            next_id = 1
            self._next_id = next_id + 1

            return next_id
        max_id = max(self.document_id_class(i) for i in table.keys())
        next_id = max_id + 1
        self._next_id = next_id + 1
        return next_id

    def _read_table(self):
        tables = self.storage.read()
        if tables is None:
            return {}
        try:
            table = tables[self.name]
        except KeyError:
            return {}
        return {
            self.document_id_class(doc_id): doc
            for doc_id, doc in table.items()
        }

    def _update_table(self, updater: Callable[[Dict[int, Mapping]], None]):
        tables = self.storage.read()
        if tables is None:
            tables = {}

        try:
            raw_table = tables[self.name]
        except KeyError:
            raw_table = {}
        table = {
            self.document_id_class(doc_id): doc
            for doc_id, doc in raw_table.items()
        }
        updater(table)
        tables[self.name] = {
            str(doc_id): doc
            for doc_id, doc in table.items()
        }
        self.storage.write(tables)
        self.clearCache()

    def object(self):
        return dict2obj(self.dict)

class Database:
    table_class = Table
    default_table_name = '_default'
    defaultstorage_class = JSONStorage

    def __init__(self, *args, **kwargs):
        storage = kwargs.pop('storage', self.defaultstorage_class)
        self._storage = storage(*args, **kwargs)
        self._opened = True
        self._tables = {}

    def __repr__(self):
        args = [
            'tables={}'.format(list(self.tables())),
            'tables_count={}'.format(len(self.tables())),
            'default_table_documents_count={}'.format(self.__len__()),
            'all_tables_documents_count={}'.format(
                ['{}={}'.format(table, len(self.table(table)))
                 for table in self.tables()]),
        ]

        return '<{} {}>'.format(type(self).__name__, ', '.join(args))

    def table(self, name: str, **kwargs):
        if name in self._tables:
            return self._tables[name]
        table = self.table_class(self.storage, name, **kwargs)
        self._tables[name] = table
        return table

    def tables(self):
        return set(self.storage.read() or {})

    def drops(self):
        self.storage.write({})
        self._tables.clear()

    def drop(self, name: str):
        if name in self._tables:
            del self._tables[name]
        data = self.storage.read()
        if data is None:
            return
        if name not in data:
            return
        del data[name]
        self.storage.write(data)

    @property
    def storage(self):
        return self._storage

    def close(self):
        self._opened = False
        self.storage.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self._opened:
            self.close()

    def __getattr__(self, name):
        return getattr(self.table(self.default_table_name), name)

    def __len__(self):
        return len(self.table(self.default_table_name))

    def __iter__(self):
        return iter(self.table(self.default_table_name))