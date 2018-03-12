# coding:utf-8
"""
sqlacodegen:
    将已经有的sql生成对应的model
    pip install sqlacodegen
    cmd: [--outfile d:\\models.py]
        sqlacodegen --noviews --noconstraints --noindexes mysql://root:123456@127.0.0.1:3306/test
        
        
        
        



https://www.keakon.net/2012/12/03/SQLAlchemy 使用经验
from sqlalchemy import func, or_, not_


user = User(name='a')
session.add(user)
user = User(name='b')
session.add(user)
user = User(name='a')
session.add(user)
user = User()
session.add(user)
session.commit()

query = session.query(User)
print query # 显示SQL 语句
print query.statement # 同上
for user in query: # 遍历时查询
    print user.name
print query.all() # 返回的是一个类似列表的对象
print query.first().name # 记录不存在时，first() 会返回 None
# print query.one().name # 不存在，或有多行记录时会抛出异常
print query.filter(User.id == 2).first().name
print query.get(2).name # 以主键获取，等效于上句
print query.filter('id = 2').first().name # 支持字符串

query2 = session.query(User.name)
print query2.all() # 每行是个元组
print query2.limit(1).all() # 最多返回 1 条记录
print query2.offset(1).all() # 从第 2 条记录开始返回
print query2.order_by(User.name).all()
print query2.order_by('name').all()
print query2.order_by(User.name.desc()).all()
print query2.order_by('name desc').all()
print session.query(User.id).order_by(User.name.desc(), User.id).all()

print query2.filter(User.id == 1).scalar() # 如果有记录，返回第一条记录的第一个元素
print session.query('id').select_from(User).filter('id = 1').scalar()
print query2.filter(User.id > 1, User.name != 'a').scalar() # and
query3 = query2.filter(User.id > 1) # 多次拼接的 filter 也是 and
query3 = query3.filter(User.name != 'a')
print query3.scalar()
print query2.filter(or_(User.id == 1, User.id == 2)).all() # or
print query2.filter(User.id.in_((1, 2))).all() # in

query4 = session.query(User.id)
print query4.filter(User.name == None).scalar()
print query4.filter('name is null').scalar()
print query4.filter(not_(User.name == None)).all() # not
print query4.filter(User.name != None).all()

print query4.count()
print session.query(func.count('*')).select_from(User).scalar()
print session.query(func.count('1')).select_from(User).scalar()
print session.query(func.count(User.id)).scalar() 
print session.query(func.count('*')).filter(User.id > 0).scalar() # filter() 中包含 User，因此不需要指定表
print session.query(func.count('*')).filter(User.name == 'a').limit(1).scalar() == 1 # 可以用 limit() 限制 count() 的返回数
print session.query(func.sum(User.id)).scalar()
print session.query(func.now()).scalar() # func 后可以跟任意函数名，只要该数据库支持
print session.query(func.current_timestamp()).scalar()
print session.query(func.md5(User.name)).filter(User.id == 1).scalar()

query.filter(User.id == 1).update({User.name: 'c'})
user = query.get(1)
print user.name

user.name = 'd'
session.flush() # 写数据库，但并不提交
print query.get(1).name

session.delete(user)
session.flush()
print query.get(1)

session.rollback()
print query.get(1).name
query.filter(User.id == 1).delete()
session.commit()
print query.get(1)

# 根据主键查询并 替换
user = User(id=1, name='ooxx')
session.merge(user)



from sqlalchemy import distinct
from sqlalchemy.orm import aliased


Friend = aliased(User, name='Friend')
Base.metadata.tables # 所有表
print session.query(User.id).join(Friendship, User.id == Friendship.user_id1).all() # 所有有朋友的用户
print session.query(distinct(User.id)).join(Friendship, User.id == Friendship.user_id1).all() # 所有有朋友的用户（去掉重复的）
print session.query(User.id).join(Friendship, User.id == Friendship.user_id1).distinct().all() # 同上
print session.query(Friendship.user_id2).join(User, User.id == Friendship.user_id1).order_by(Friendship.user_id2).distinct().all() # 所有被别人当成朋友的用户
print session.query(Friendship.user_id2).select_from(User).join(Friendship, User.id == Friendship.user_id1).order_by(Friendship.user_id2).distinct().all() # 同上，join 的方向相反，但因为不是 STRAIGHT_JOIN，所以 MySQL 可以自己选择顺序
print session.query(User.id, Friendship.user_id2).join(Friendship, User.id == Friendship.user_id1).all() # 用户及其朋友
print session.query(User.id, Friendship.user_id2).join(Friendship, User.id == Friendship.user_id1).filter(User.id < 10).all() # id 小于 10 的用户及其朋友
print session.query(User.id, Friend.id).join(Friendship, User.id == Friendship.user_id1).join(Friend, Friend.id == Friendship.user_id2).all() # 两次 join，由于使用到相同的表，因此需要别名
print session.query(User.id, Friendship.user_id2).outerjoin(Friendship, User.id == Friendship.user_id1).all() # 用户及其朋友（无朋友则为 None，使用左连接）



sqlacodegen --noviews --noconstraints --noindexes ''


"""
from copy import copy
from subprocess import Popen, PIPE
from logging import getLogger, DEBUG
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from copy import copy
from json import dumps as json_dumps
from types import IntType, ListType

from attrdict import AttrDict
from sqlalchemy.orm import Session
from sqlalchemy.util._collections import _LW, KeyedTuple

try:
    from model import Base, metadata
except ImportError:
    Base = type("", (object,), {})()

# 给会话类添加上下文管理器
setattr(Session, "__enter__", lambda self: self)
setattr(Session, "__exit__", lambda self, *args, **kwargs: self.close())


#
# 工具
#

def _dict(self):
    """
    Test(id=5) # {"id": 5}   # self.__table__.columns
    :param self:
    :return:
    """
    attr = copy(self.__dict__)
    del attr["_sa_instance_state"]
    return attr


def __str__(self):
    ''' 打印对象时自动打印数据 '''
    return json_dumps(self._dict, default=str)  # 默认字符类型


def setdefault_by_pk(cls, session_class, **kwargs):
    where = []
    for pk in cls.__table__.primary_key:  # 输入主键的情况 判断自增键 如果不是自增就插入键
        option = kwargs.get
        if isinstance(kwargs.get(pk.key), IntType):  # 自增键一定为INT类型
            option = kwargs.pop
        where.append(getattr(cls, pk.key) == option(pk.key))
    with session_class() as session:
        model = session.query(cls).filter(*where).scalar()
        if not model:
            model = cls(**kwargs)
            session.add(model)
            session.commit()
        model = AttrDict(model._dict)  # XXX 返回的对象为字典
    return model


def asdict(object):
    ''' 将对象转换成字典类型 '''
    if isinstance(object, ListType):
        result = []
        for row in object:
            if hasattr(row, "_asdict"):
                result.append(AttrDict(row._asdict()))
            elif hasattr(row, "_dict"):
                result.append(AttrDict(row._dict))
            else:
                raise Exception("不支持的类型,请添加支持方法.")
        return result
    if not object:
        return AttrDict()
    if isinstance(object, AttrDict):
        return object
    if isinstance(object, Base):
        return AttrDict(object._dict)
    return AttrDict(object._asdict())


_LW._dict = KeyedTuple._dict = property(lambda self: AttrDict(self._asdict()))  # 可以使用.的形式访问字段
keyed_tuple = KeyedTuple([], [])
Base._dict = property(_dict)
Base.__str__ = __str__  # 改变原有的字符输出方法
Base.setdefault_by_pk = classmethod(setdefault_by_pk)

#
#   连接方式
#

logger = getLogger()
logger.setLevel(DEBUG)
config = dict(type="mysql", username="root", password="123456", host="127.0.0.1", port=3306, database="test", charset="utf-8")

TEMPLATE = '{type}://{username}:{password}@{host}:{port}/{database}?charset={charset}'

connect_params = TEMPLATE.format(**config)
engine = create_engine(connect_params)
# Base.metadata.create_all(engine)  # 自动创建表
default_session = lambda: sessionmaker(bind=engine)  # 获得会话

generate_head = "sqlacodegen --noviews --noconstraints --noindexes "


# 上下文管理器






#
#
def model_generate(**config):
    """ 生成 SQLAlchemy的model对象"""
    outfile = config.pop("outfile", None)
    outfile = ("--outfile %s" % outfile) if outfile else ''
    command = generate_head + outfile + TEMPLATE.format(**config)
    logger.debug(command)
    print command
    return Popen(command, stdout=PIPE).stdout.read()


#
#
if __name__ == '__main__':
    from logging import basicConfig

    basicConfig()
    config = model_generate(**config)
