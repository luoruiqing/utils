# coding:utf-8
"""
sqlacodegen:
    将已经有的sql生成对应的model
    pip install sqlacodegen
    cmd: [--outfile d:\\models.py]
        sqlacodegen --noviews --noconstraints --noindexes mysql://root:123456@127.0.0.1:3306/test

"""

from subprocess import Popen, PIPE
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

template = '//{user}:{password}@{host}:{port}/{database}'
config = dict(host="127.0.0.1", port=3306, database="test", user="root", password="123456", charset="utf8")
generate_head = "sqlacodegen --noviews --noconstraints --noindexes mysql:"
get_session = lambda **config: sessionmaker(bind=create_engine("mysql+mysqlconnector:" + template.format(**config)))


def model_generate(**config):
    """ 生成 SQLAlchemy的model对象"""
    command = generate_head + template.format(**config)
    print command
    process = Popen(command, stdout=PIPE)
    return process.stdout.read()


if __name__ == '__main__':
    print get_session(**config)
    print model_generate(**config)
