# coding:utf-8
from decimal import Decimal
from functools import partial
from collections import Iterable
from types import IntType, NoneType
from json import dumps as json_dumps
from pymysql.cursors import DictCursor
from tornado.gen import coroutine, Return
from tornado_mysql import connect, cursors
from pymysql.connections import Connection

TDB = partial(connect, host="127.0.0.1", port=3306, user='root', passwd='123456',
              db='test', cursorclass=cursors.DictCursor)
DB = partial(Connection, host="127.0.0.1", port=3306, user='root', passwd='123456',
             db='test', cursorclass=DictCursor)


def items(items):
    """ pysql中拼接括号参数方法  items(3) ->> (%s, %s, %s)"""
    count = items if isinstance(items, IntType) else len(items)
    return "(" + ", ".join(["%s"] * count) + ")"


def get_one_field(result, field, default=None):
    """ 取第一条记录中的一个字段 id = get_one_field(cur.fetchall()/cur.fetchone(), 'id') """
    if isinstance(result, NoneType):
        result = {}
    elif isinstance(result, Iterable):
        result = result[0] if hasattr(result, "__getitem__") else list(result)[0]
    return result.get(field, default)


class ConnectManager:
    """ 用于简单管理tornado_mysql的连接关闭
    # tornado =============================================
    with ConnectManager((yield db_conn())) as (conn, cur):
        yield cur.execute("show tables;")
    # ordinary ============================================
    with ConnectManager(db_conn()) as (conn, cur):
        yield cur.execute("show tables;")
    """

    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        self.cur = self.conn.cursor()
        return self.conn, self.cur

    def __exit__(self, *args, **kwargs):
        self.cur.close()
        self.conn.close()


@coroutine
def tornado_query(sql, args=None):
    """ yield tornado_query()"""
    with ConnectManager((yield TDB())) as (conn, cur):
        yield cur.execute(sql, args)
    raise Return(list(cur))


def query(sql, args=None):
    with ConnectManager(DB()) as (conn, cur):
        cur.execute(sql, args)
        result = cur.fetchall()
    return result


@coroutine
def tornado_query_one(sql, args=None):
    with ConnectManager((yield TDB())) as (conn, cur):
        yield cur.execute(sql, args)
        result = cur.fetchone()
    raise Return(result)


def query_one(sql, args=None):
    with ConnectManager(DB()) as (conn, cur):
        cur.execute(sql, args)
        result = cur.fetchone()
    return result


sql_dumps = partial(json_dumps, default=lambda obj: float(obj) if isinstance(obj, Decimal) else obj)

if __name__ == '__main__':
    pass
