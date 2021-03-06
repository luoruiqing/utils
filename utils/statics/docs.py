# coding:utf-8
mysql_doc = """
cur.execute() # 执行mysql
cur.fetchall() # 获得所有结果
cur.fetchmany() # 获得条数结果  [cur.arraysize 是默认值]
cur.fetchone() # 获得第一条
cur.lastrowid # 插入的上条记录的ID
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

deque = """
from collections import deque
deque(maxlen=10) 定长列表 maxlen 决定长度 自动挤出去之前下标为0的数据
"""
