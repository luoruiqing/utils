# coding:utf-8
from __future__ import print_function
from functools import partial
from tornado.gen import coroutine, Return
from tornado.ioloop import IOLoop, PeriodicCallback


def check_tornado_async(func):
    """检查是不是tornado异步方法"""
    return "TracebackFuture" in func.func_code.co_names


def tornado_run(function, *args, **kwargs):
    """ 异步执行一个方法 """
    tornado_timeout = kwargs.pop("tornado_timeout", None)
    _print = kwargs.pop("_print", True)
    function = partial(function, *args, **kwargs)  # 填写默认参数
    if _print:  # 打印返回结果
        @coroutine
        def async_print_result(func):
            print((yield func()))

        function = partial(async_print_result, func=function)
    IOLoop.current().run_sync(function, timeout=tornado_timeout)


def tornado_periodic(function, interval, start=True, *args, **kwargs):
    """ 周期执行一个函数 interval基本单位是毫秒 不阻塞时,应该手动启动tornado ioloop的单例"""
    PeriodicCallback(partial(function, *args, **kwargs), interval).start()
    if start:
        IOLoop.instance().start()


def clear_locals(vars, pops=("self", "conn", "cur")):
    """ tornado中使用locals() 不用一个个传变量了
    def get(self):
        return self.render('index.html', **clear_locals(locals()))
    """
    for v in pops:
        if v in vars:
            del vars[v]
    return vars


def tornado_wrapper(func):
    """ 注意顺序 这里可以分辨方法是否被异步 <使用装饰器可以在tornado里面干净的写API>
    @tornado_wrapper
    @coroutine
    def test(*args, **kwargs):
        yield None
    """

    @coroutine
    def async_wrapper(*args, **kwargs):
        raise Return((yield func()))

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    if "TracebackFuture" in func.func_code.co_names:  # 被异步的方法<coroutine>
        wrapper = async_wrapper
    return wrapper


def tornado_api_dome():
    """使用tornado_wrapper可以在tornado里面干净的写API 这里只拿tornado举例"""

    def api(func):
        @coroutine
        def async_wrapper(self, *args, **kwargs):
            r, e = None, None
            try:
                r = yield func(self, *args, **kwargs)
            except ValueError, e:  # 这里自定义错误类 更加方便
                self.write({"status": False, "message": e.message, "data": None})
            except Exception:
                raise
            if r and not e:
                self.write({"status": True, "message": "OK.", "data": r})
                raise Return(r)

        return async_wrapper

    @api
    @coroutine
    def post(self, *args, **kwargs):  # 源码这么少 还能对数据库连接管理
        if True:
            raise ValueError("No data.")

    tornado_run(post, self=type('', tuple(), {"write": print}), _print=False)


def tornado_static_dome():
    STATICS = []

    @coroutine
    def tornado_async(func, *args, **kwargs):
        """ 同步的方式执行tornado方法 结果写入静态变量中，外面无需 yield
        tornado_run(partial(tornado_async, async_func, *args, **kwargs))
        """
        # global STATICS
        result = yield func(*args, **kwargs)
        STATICS.append(result)

    tornado_run(tornado_async)


cl = clear_locals
# 无意义的代码和例子只是想要学习交流 故删除
del tornado_wrapper
del tornado_api_dome
del tornado_static_dome
if __name__ == '__main__':
    tornado_api_dome()
