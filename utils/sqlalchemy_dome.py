# coding:utf-8
"""
sqlacodegen:
    将已经有的sql生成对应的model
    pip install sqlacodegen
    cmd: [--outfile d:\\models.py]
        sqlacodegen --noviews --noconstraints --noindexes mysql://root:123456@127.0.0.1:3306/test




"""
from __future__ import unicode_literals
from subprocess import Popen, PIPE
from logging import getLogger, DEBUG
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

logger = getLogger()
logger.setLevel(DEBUG)

template = '//{user}:{password}@{host}:{port}/{database}'
generate_head = "sqlacodegen --noviews --noconstraints --noindexes "
get_session = lambda **config: sessionmaker(bind=create_engine("mysql+mysqlconnector:" + template.format(**config)))


def setdefault__str__():
    """
    sqlalchemy 的所有__str__方法修改成易读的样子 ;)
    a.py
        class Tag(Base):
            __tablename__ = 'tags'

            name = Column(String(255), nullable=False)
        print Tag(name="luoruiqing") ->  <invest.tools.database.model.Tag object at 0x03BAFD10>
    b.py
        from a import Tag
        setdefault__str__()
        print Tag(name="luoruiqing") ->   {"name": "luoruiqing"}
    """
    try:
        from model import Base
    except:
        return False
    from copy import copy
    from json import dumps
    def default__str__(self):
        attr = copy(self.__dict__)
        del attr["_sa_instance_state"]
        return dumps(attr)

    Base.__str__ = default__str__  # 改变原有的字符输出方法
    return True


def model_generate(**config):
    """ 生成 SQLAlchemy的model对象"""
    outfile = config.pop("outfile", '')
    outfile = ("--outfile %s" % outfile) if outfile else ''
    command = generate_head + outfile + " mysql:" + template.format(**config)
    logger.debug(command)
    print command
    return Popen(command, stdout=PIPE).stdout.read()


if __name__ == '__main__':
    from logging import basicConfig

    config = dict(host="127.0.0.1", port=3306, database="invest", user="root", password="123456", charset="utf8")
    basicConfig()
    print model_generate(**config)
