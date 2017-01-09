# coding:utf-8

from os import popen as sys_popen
from logging import getLogger, DEBUG
from subprocess import PIPE, Popen as subprocess_popen
from paramiko import AutoAddPolicy, SSHClient as _SSHClient

logger = getLogger()
logger.setLevel(DEBUG)


def subprocess_cmd(command):
    """ subprocess_cmd("ping www.baidu.com") """
    logger.debug('process cmd: %s' % command)
    process = subprocess_popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    return process.stdout.read() or process.stderr.read()


def sys_cmd(command):
    """ sys_cmd("ping www.baidu.com") """
    logger.debug('process cmd: %s' % command)
    pipe = sys_popen('{ ' + command + '; } 2>&1', 'r')
    sts = pipe.close()
    if sts is None:
        sts = 0
    return sts


def ssh_cmd(command, hostname, port=22, username=None, password=None):
    with SSHClient(hostname=hostname, port=port, username=username, password=password) as ssh_c:
        e = ssh_c.exe(command)
    return e


CommandError = type('CommandError', (Exception,), {})


class SSHClient(_SSHClient):
    def __init__(self, *args, **kwargs):
        self.hostname = kwargs.get("hostname") or (args or [None, ])[0]
        super(SSHClient, self).__init__()
        self.set_missing_host_key_policy(AutoAddPolicy())
        self.connect(*args, **kwargs)
        # self.set_log_channel("test.log")

    def exe(self, command, safe=False):
        stdin, stdout, stderr = self.exec_command(command)
        e = stderr.read()
        if e:
            error = "[%s] " % self.hostname + e
            if safe:
                raise CommandError(error)
            logger.warning(error)
        return stdout.read() or e



