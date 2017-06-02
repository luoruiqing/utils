# coding:utf-8
from functools import wraps
from flask import Flask, request
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)


def unpackargs(func):
    """ 解包参数
        不管任意方式 都将提交的内容解包
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs = (getattr(request, "form") or getattr(request, "args", ImmutableMultiDict())).to_dict()
        return func(*args, **dict(kwargs, **kwargs))

    return wrapper


@app.route("/")
@unpackargs
def index(name="World"):  # http://127.0.0.1:8888/?name=luoruiqing
    return "Hello %s!" % name


if __name__ == '__main__':
    from logging import basicConfig

    basicConfig(format="[%(levelname)s - %(asctime)s]: %(message)s")
    app.run(host='0.0.0.0', port=8888, debug=True)
