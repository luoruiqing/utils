# coding:utf-8
from web.db import MySQLDB
from web.utils import Storage

""" 只取出一条数据 """
MySQLDB.query_one = lambda self, *args, **kwargs: next(iter(self.query(*args, **kwargs)), Storage())
