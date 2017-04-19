# coding:utf-8
"""
sqlacodegen:
    将已经有的sql生成对应的model
    pip install sqlacodegen
    cmd: [--outfile d:\\models.py]
        sqlacodegen --noviews --noconstraints --noindexes mysql://root:123456@127.0.0.1:3306/test




"""

from subprocess import Popen, PIPE
from logging import getLogger, DEBUG
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

logger = getLogger()
logger.setLevel(DEBUG)

template = '//{user}:{password}@{host}:{port}/{database}'
config = dict(host="127.0.0.1", port=3306, database="test", user="root", password="123456", charset="utf8")
generate_head = "sqlacodegen --noviews --noconstraints --noindexes "
get_session = lambda **config: sessionmaker(bind=create_engine("mysql+mysqlconnector:" + template.format(**config)))


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

    basicConfig()
    print model_generate(**config)
