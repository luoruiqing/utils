# coding:utf-8
"""
    Flask标准化接口抽象类以及错误类
"""
from __future__ import unicode_literals
from traceback import print_exc
from logging import root as logger
from flask.views import MethodView
from types import DictType, ListType
from flask import jsonify, request, abort
from class_tools import import_mapping_classes


# class ABCAPI(object):
#     __metaclass__ = type(b"APIMetaClasses", (ABCMeta, APIMetaClass), {})

class MethodViewBase(MethodView):
    def dispatch_request(self, *args, **kwargs):
        try:
            result = super(MethodViewBase, self).dispatch_request(*args, **kwargs)
            if isinstance(result, (DictType, ListType)):
                return jsonify({"message": "ok", "status": True, "data": result})
            return result
        except Exception, e:
            print_exc()
            logger.error(abort(500))
            return jsonify({"message": e.message, "status": False, "data": {}})

    @property
    def json(self):
        try:
            self._json = getattr(self, "_json", None) or request.get_json(force=True)
        except:
            self._json = {}
            print_exc()
        return self._json

    @property
    def params(self):
        self._params = getattr(self, "_params", None) or (request.form or request.args).to_dict()
        return self._params


def install_rules(self, dir):
    """
    自动安装映射路径，路由是 /<第一层文件名称/第一层文件夹>/<第二层文件名称/第二层文件夹>/..../类名
    :param self: 
    :param dir: 
    :return: 
    >>> from flask import Flask
    >>> Flask.install_rules = install_rules
    >>> if __name__ == '__main__':
    >>>     app = Flask(__name__).install_rules("../control")
    >>>     app.run(debug=True)
    """
    for path, _class in import_mapping_classes(dir):
        assert issubclass(_class, MethodView), "{}.{} not is flask MethodView class.".format(path, _class.__name__)
        rule = "/" + "/".join(path.split(".")[1:])
        self.add_url_rule(rule, view_func=_class.as_view(_class.__name__))
    return self


if __name__ == '__main__':
    pass
