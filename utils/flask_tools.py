# coding:utf-8
"""
    Flask标准化接口抽象类以及错误类
"""
from __future__ import unicode_literals
from functools import wraps
from flask import jsonify, request
from abc import ABCMeta, abstractproperty
from types import StringType, DictType, ListType, ObjectType


# ============================================================================
# 错误
class APIBaseException(BaseException):
    """ API 错误基类 """


class APIException(Exception):
    """ 错误类 """
    status = False  # 错误状态都为false
    code = 0  # 错误代码
    msg = "API Error."  # 错误消息

    def __init__(self, msg=None, *args, **kwargs):
        super(Exception, self).__init__(msg or self.msg, *args, **kwargs)


# ============================================================================
# 接口装饰类，包含结果处理，标准化错误提示
def standard(func):
    """ API结果处理方法 """

    func_params = set(func.func_code.co_varnames)

    @wraps(func)
    def _wrapper(*args, **kwargs):
        requests_params = dict(request.args.to_dict(), **request.form.to_dict())
        for k, v in requests_params.iteritems() if len(func_params) > 1 else ():
            if k in func_params:
                kwargs[k] = None if isinstance(v, StringType) and not v.strip() else v  # 对空字符处理
        try:
            result = func(*args, **kwargs)
        except APIException, e:
            return jsonify({"status": e.status, "code": e.code, "message": e.message})
        except TypeError, e:
            if " argument " in e.message:  # 参数错误
                return '''<h1>Bad Request</h1>
                <br>The browser (or proxy) sent a request that this server could not understand.''', 400
            raise  # 其他错误抛出
        if isinstance(result, (DictType, ListType)):
            return jsonify({"status": True, "message": "ok.", "code": -1, "data": result})
        return result

    return _wrapper


# ============================================================================


class APIMetaClass(type):
    """ 基础元类 负责错误捕获和JSON格式化以及错误提示JSON """

    def __new__(cls, name, bases, attr):
        if bases and not ObjectType in bases:  # 非父类
            funcs = filter(lambda (k, v): not k.startswith("__"), attr.iteritems())
            for k, v in funcs:
                if hasattr(v, "__call__"):
                    attr[k] = standard(v)
        return type.__new__(cls, name, bases, attr)


if __name__ == '__main__':
    from flask import Flask

    app = Flask(__name__)


    # ========================================================================
    # 接口实现

    # 抽象
    class ABCAPI(object):
        __metaclass__ = type(b"APIMetaClasses", (ABCMeta, APIMetaClass), {})

        @abstractproperty
        def index(self, *args, **kwargs):
            """ 主页 """

        def search(self, *args, **kwargs):
            raise NotImplementedError("未实现")


    class API(ABCAPI):
        def index(self, name="World!"):
            # 俩个测试地址
            # http://127.0.0.1:5000/index?name=luoruiqing
            # http://127.0.0.1:5000/index
            return "Hello {}".format(name)


    # 普通
    @standard
    def test(name='test', age=0):
        """
        测试地址
        http://127.0.0.1:5000/test?name=luoruiqing&age=22
        http://127.0.0.1:5000/test?age=22
        :return:
        """
        if name != "test":
            raise APIException("接口功能未完成.")
        return {"name": name, "age": age}


    app.add_url_rule("/index", view_func=API().index, methods=["GET", "POST"])
    app.add_url_rule("/test", view_func=test, methods=["GET", "POST"])
    app.run(debug=True)
