# coding:utf-8
from sys import platform
from os import popen as sys_popen
from logging import getLogger, DEBUG
from subprocess import PIPE, Popen as subprocess_popen
from paramiko import AutoAddPolicy, SSHClient as _SSHClient

logger = getLogger()
logger.setLevel(DEBUG)


def subprocess_cmd(command, *args, **kwargs):
    """ 这个方法会返回迭代器，一边读一边返回
    for row in subprocess_cmd_noblock("ping 8.8.8.8"):
        print row,
    """
    logger.debug('process cmd: %s' % command)
    stdin, stdout, stderr = [kwargs.pop(field, PIPE) for field in ("stdin", "stdout", "stderr")]
    process = subprocess_popen(command, stdin=stdin, stdout=stdout, stderr=stderr, *args, **kwargs)
    while process.poll() is None:  # 下面只是展示用法，不好封装这个方法
        try:
            r = process.stdout.readline()
            if r:
                yield r
        except KeyboardInterrupt:
            pass  # 中断信号忽略,如果还有内容继续读取
    error = process.stderr.read()
    if error:
        yield error


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


if "win" not in platform:
    from sh import ifconfig  # 好用到哭的库 回头研究

    print ifconfig("ech0")
