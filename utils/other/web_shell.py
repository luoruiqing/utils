# coding:utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from Queue import Queue
from functools import wraps
from platform import system
from time import time as now
from threading import Thread
from StringIO import StringIO
from flask import Flask, request
from logging import getLogger, DEBUG
from types import DictType, StringTypes
from subprocess import PIPE, Popen as subprocess_popen
from io import BytesIO

logger = getLogger()
logger.setLevel(DEBUG)

queue = Queue(10)  # 同时最多处理100个任务
console = {}
flask_app = Flask(__name__)
TestError = type('TestError', (Exception,), {})


# if "WIN" in system().upper():
#     command += " -t"

def cmd(command):
    process = subprocess_popen(command, shell=True, stdout=PIPE, stderr=PIPE)  # , close_fds=True)
    while process.poll() is None:
        yield process.stdout.readline()
    err = process.stderr.readline()
    if err:
        yield err


def consumer():
    while 1:
        msg = queue.get()
        logger.info("start url %s" % msg)
        info = console.setdefault(msg, {})
        info["start_time"] = now()
        for row in cmd(msg):
            info.setdefault("out", []).append(row)


def api_result(function):  # 接口返回值
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            result = function(*args, **kwargs)
        except Exception, error:
            return {"status": False, "msg": error.message}
        if isinstance(result, (DictType, StringTypes)):
            return {"status": True, "msg": "OKey."}
        return result

    return wrapper


#
def cmd_task():
    while True:
        msg = queue.get()
        result = cs_type = err = None
        logger.debug('process cmd: %s' % msg)
        info = console.get(msg, {})
        if now() - info.get("last_time", 0) > 3600:  # 超出一小时，删除掉这个任务
            del info  # TODO 这里应该退出命令行，回头查一下
        # cmd = info["cmd"] = "" % (work_dir, quotes, url, quotes)
        stdout = stderr = StringIO()  # 合并输出错误流
        info["popen"] = subprocess_popen(cmd, shell=True, stdout=stdout, stderr=stderr)


HTML = """

"""
app.route('/check_cs')(lambda: HTML)


@app.route('/check_cs/test', methods=["POST"])
@api_result
def cs_test():
    url = request.args["url"]
    if len(console) > 100:
        raise TestError("任务已满，请稍后重试。")

    info = console.setdefault(url, {"last_time": now()})
    queue.put(url, block=False, timeout=5)
    return "OKey."


@app.route('/check_cs/test/read', methods=["POST"])
def cs_test1():
    url = request.args["url"]
    task = console.get(url, {})
    read_lines = task["stdout"].read()
    return read_lines


if __name__ == '__main__':
    tasks = [Thread(target=cmd_task) for x in range(5)]
    for x in tasks:
        x.start()
    app.run()
