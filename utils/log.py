# coding:utf-8
from sys import stdout
from collections import Iterable
from logging import INFO, DEBUG, NOTSET, basicConfig, getLogger, Logger

FORMAT = "[%(levelname)s - %(asctime)s]: %(message)s"


def log_wrapper(func):
    """ 修改打印方法，可以传入其他数据类型，使用str强制转换
    logger.debug(range(5)) --> [INFO - 2017-03-20 11:50:07]: [0, 1, 2, 3, 4]
    """

    def wrapper(self, *args, **kwargs):
        args = list(args)
        if not isinstance(args[1], basestring) and isinstance(args[1], Iterable):
            args[1] = str(args[1]) or repr(args[1])
        return func(self, *args, **kwargs)

    return wrapper


Logger._log = log_wrapper(Logger._log)  # 扩展内置方法


def logger_init():
    """ 闭包方法，当遇到错误时，如果有日志模块，将错误输出到日志，如果没有输出到控制台

from logging import basicConfig
# basicConfig() # 初始化后和未初始化日志模块有区别
try:
    1 + "s"
except:
    logging_err()
    """
    from sys import stderr
    from traceback import format_exc
    from logging import root, getLogger, DEBUG
    logger = getLogger()
    logger.setLevel(DEBUG)

    def outerr(e=None):
        e = e or format_exc()
        if root.handlers:
            logger.error(e)
        else:
            stderr.write(e)

    return outerr


logging_err = logger_init()
del logger_init


def get_mongodb_logger(collection, db="log", host='localhost', port=None,
                       username=None, password=None, level=NOTSET):
    # 将日志写入到mongodb中
    from mongolog.handlers import MongoHandler  # mongolog 这是一个log库
    logger = getLogger()
    logger.setLevel(DEBUG)
    logger.addHandler(MongoHandler(collection, db))
    return logger


del get_mongodb_logger  # 这个方式产生的日志比较详细，占用磁盘空间太高，只记录错误日志还可以
basicConfig(level=INFO, format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S', stream=stdout)  # 全局默认日志
getLogger('requests').setLevel(INFO)  # 屏蔽requests INFO 级别一下的日志

if __name__ == '__main__':
    logger = getLogger()
    logger.setLevel(DEBUG)
    logger.info("Hello word!")
    logger.info(range(5))
    logger.info(256)
    logger.info("sleep %ss...", 5)
