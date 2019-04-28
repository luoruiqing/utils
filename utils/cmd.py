from sys import platform
import io
from os import popen as sys_popen
from logging import getLogger, DEBUG
from subprocess import PIPE, Popen as subprocess_popen
from paramiko import AutoAddPolicy, SSHClient as _SSHClient

logger = getLogger()
logger.setLevel(DEBUG)

# client.load_system_host_keys()  # 加载系统的机器列表 直接通过机器访问


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


# CommandError = type('CommandError', (Exception,), {})


class SSHClient(_SSHClient):
    def __init__(self, *args, **kwargs):
        self.hostname = kwargs.get("hostname") or (args or [None, ])[0]  # 获取服务器名称
        super(SSHClient, self).__init__()
        self.init()  # 做一部分简单的初始化
        private_key_string = kwargs.pop("private_key", None)
        if private_key_string:
            file_object = self.get_private_key_file()  # 字符类型的私钥  生成Python IO对象
            kwargs['pkey'] = paramiko.RSAKey.from_private_key(file_object)  # 生成paramiko密钥对象
        self.connect(*args, **kwargs)

    @staticmethod
    def get_private_key_file(string):
    ''' 根据私钥内容生成文件接口, 方便paramiko模块使用 '''
        file_object = io.StringIO()
        file_object.write(string)
        file_object.seek(0, os.SEEK_SET)  # 文件指针到开始
        return file_object  # RSAKey.from_private_key(file_object)

    # def exe(self, command, safe=False):

    #     stdin, stdout, stderr = self.exec_command(command)
    #     e = stderr.read()
    #     if e:
    #         error = "[%s] " % self.hostname + e
    #         if safe:
    #             raise CommandError(error)
    #         logger.warning(error)
    #     return stdout.read() or e

    def init(self, *args, **kwargs):
        self.set_missing_host_key_policy(AutoAddPolicy())


if "win" not in platform:
    from sh import ifconfig  # 好用到哭的库 回头研究

    print ifconfig("ech0")
