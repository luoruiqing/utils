# coding:utf-8
from json import dumps
from web.db import MySQLDB
from functools import partial
from web.utils import Storage, IterBetter

""" 只取出一条数据 """
MySQLDB.query_one = lambda self, *args, **kwargs: next(iter(self.query(*args, **kwargs)), Storage())


def webpy_dumps(object):
    if isinstance(object, IterBetter):
        return list(IterBetter)
    return str(object)


dumps = partial(dumps, default=webpy_dumps)
