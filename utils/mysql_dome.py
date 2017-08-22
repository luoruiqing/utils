# coding:utf-8
""" MYSQL 的一些小工具和备注信息
cur.execute() # 执行mysql
cur.fetchall() # 获得所有结果
cur.fetchmany() # 获得条数结果  [cur.arraysize 是默认值]
cur.fetchone() # 获得第一条
cur.lastrowid # 插入的上条记录的ID
cur.description # 执行查询后 结果集内的keys就是这个
    # if cursor.description:
    #    names = [x[0] for x in cursor.description]
# ===========================================================
MysqlResult对象
    affected_rows = None
    insert_id = None
    server_status = None
    warning_count = 0
    message = None
    field_count = 0
    description = None
    rows = None
# ===========================================================
cur.rowcount # 执行查询后记录的条数
cur._last_executed # 插入时生成的SQL语句
conn.cursor() # 开启一个游标 可以传入一个游标类 例如:DictCursor
conn.commit() # 提交
conn.get_autocommit() # 获得是否开启了自动提交
conn.rollback() # 回滚提交
conn.client_flag # 客户端编号
conn.connect_timeout # 连接超时时间
conn.connected_time # 当前连接时间
conn.cursorclass # 游标类
conn.db # 当前数据库名称
conn.encoding # 编码类型
conn.host_info/get_host_info() # 获得主机地址 端口号 socket 127.0.0.1:3306
conn.insert_id() # 上一个提交的ID
conn.host # 主机地址
conn.port # 主机端口
conn.ping() # 测试连接
conn.user # 数据库用户名
conn.password # 数据库密码
conn.server_status #服务器状态 1 正常
conn.server_thread_id # 本次连接被分配的线程ID
conn.ssl # 是否是SLL连接
"""
from decimal import Decimal
from functools import partial
from collections import Iterable
from types import IntType, NoneType
from  collections import OrderedDict
from json import dumps as json_dumps
from pymysql.cursors import DictCursor
from tornado.gen import coroutine, Return
from tornado_mysql import connect, cursors
from pymysql.connections import Connection
from pymysql.cursors import DictCursorMixin, Cursor


class OrderedDictCursor(DictCursorMixin, Cursor):
    """ 有序字典游标类 PyMysql """
    dict_type = OrderedDict


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
