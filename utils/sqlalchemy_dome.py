# coding:utf-8
"""
sqlacodegen:
    将已经有的sql生成对应的model
    pip install sqlacodegen
    cmd: [--outfile d:\\models.py]
        sqlacodegen --noviews --noconstraints --noindexes mysql://root:123456@127.0.0.1:3306/test



"""
from copy import copy
from subprocess import Popen, PIPE
from logging import getLogger, DEBUG
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta

try:
    from model import Base
except ImportError:
    Base = type("", (object,), {})()

logger = getLogger()
logger.setLevel(DEBUG)

template = '//{user}:{password}@{host}:{port}/{database}?charset={charset}'
generate_head = "sqlacodegen --noviews --noconstraints --noindexes "
get_session = lambda **config: sessionmaker(bind=create_engine("mysql+mysqlconnector:" + template.format(**config)))


def default__str__(self):
    """
    :param self: 
    :return:
    
    sqlalchemy 的所有__str__方法修改成易读的样子 ;)
    model.py
        class Tag(Base):
            __tablename__ = 'tags'
            name = Column(String(255), nullable=False)
        print Tag(name="luoruiqing") ->  <invest.tools.database.model.Tag object at 0x03BAFD10>
    test.py
        setdefault__str__()
        from model import Tag
        print Tag(name="luoruiqing") ->   {"name": "luoruiqing"}

    """
    attr = copy(self.__dict__)
    del attr["_sa_instance_state"]
    return dumps(attr)


# 改变原有的字符输出方法
Base.__str__ = default__str__
# 返回所有的内容为字典类型
Base.dict = property(lambda self: {c.name: getattr(self, c.name) for c in self.__table__.columns})


def dumps(object):
    if isinstance(object.__class__, DeclarativeMeta):
        return object.dict


def model_generate(**config):
    """ 生成 SQLAlchemy的model对象"""
    outfile = config.pop("outfile", None)
    outfile = ("--outfile %s" % outfile) if outfile else ''
    command = generate_head + outfile + " mysql:" + template.format(**config)
    logger.debug(command)
    print command
    return Popen(command, stdout=PIPE).stdout.read()


if __name__ == '__main__':
    from logging import basicConfig

    config = dict(host="127.0.0.1", port=3306, database="dictionary", user="root", password="123456",
                  charset="utf8")
    basicConfig()
    print model_generate(**config)
