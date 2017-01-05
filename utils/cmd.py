from os import popen as sys_popen
from logging import getLogger, DEBUG
from subprocess import PIPE, Popen as subprocess_popen

logger = getLogger()
logger.setLevel(DEBUG)


def subprocess_cmd(cmd):
    """ subprocess_cmd("ping www.baidu.com") """
    process = subprocess_popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    return (process.stdout.read(), process.stderr.read())


def sys_cmd(cmd):
    """ sys_cmd("ping www.baidu.com") """
    logger.debug('process cmd: %s' % cmd)
    pipe = sys_popen('{ ' + cmd + '; } 2>&1', 'r')
    sts = pipe.close()
    if sts is None:
        sts = 0
    return sts
