# coding:utf-8
from sys import stdout
from collections import Iterable
from logging import INFO, DEBUG, NOTSET, basicConfig, getLogger, Logger


def log_wrapper(func):
    """ 修改打印方法，可以传入其他数据类型，使用str强制转换 """

    def wrapper(*args, **kwargs):
        args = list(args)
        if not isinstance(args[2], basestring) and isinstance(args[2], Iterable):
            args[2] = str(args[2])
        return func(*args, **kwargs)

    return wrapper


Logger._log = log_wrapper(Logger._log)

FORMAT = '%(asctime)s [%(levelname)s] %(threadName)s %(message)s'
basicConfig(  # 全局默认日志
    level=INFO,
    format=FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=stdout
)


def get_mongodb_logger(collection, db="log", host='localhost', port=None,
                       username=None, password=None, level=NOTSET):
    # 将日志写入到mongodb中
    from mongolog.handlers import MongoHandler
    logger = getLogger()
    logger.setLevel(DEBUG)
    logger.addHandler(MongoHandler(collection, db))
    return logger


if __name__ == '__main__':
    # logger = get_mongodb_logger('appinfo')
    # logger.info("debug message111111111111111111111111111111111111")
    logger = getLogger()
    logger.setLevel(DEBUG)
    logger.info("111111111111111111")
    logger.info(range(5))
