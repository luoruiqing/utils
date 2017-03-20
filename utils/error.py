# coding:utf-8
from abc import ABCMeta
from sys import exc_info
from traceback import extract_tb


def get_error_info():
    """ 获得错误信息 返回的信息依次为 错误类型，错误原因，错误文件路径，错误文件行号，错误方法名称，错误行的代码内容 """
    exc_type, exc_reason, exc_tb = exc_info()
    file_path, line, func_name, err_line_content = extract_tb(exc_tb)[-1]
    return exc_type, exc_reason, file_path, line, func_name, err_line_content


class ErrorManager:
    """ 发生错误的另一种简洁的写法

    class ErrorManagerDome(ErrorManager):
        def _except(self):
            print "error!"

    ErrorManagerDome = ErrorManagerDome()
    with ErrorManagerDome:
        1 + "s"

    """
    __metaclass__ = ABCMeta
    __enter__ = lambda self: self

    def __init__(self, exc_types=Exception):
        if issubclass(exc_types, BaseException):
            exc_types = [exc_types]
        self.exc_types = exc_types

    def _except(self, *args, **kwargs):
        """ 发生错误时候执行的方法 """

    def _finally(self, *args, **kwargs):
        """ 一定执行的方法 """

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exc_val 是错误类 直接抛出 会把错误栈信息重新抛出
        if exc_type:
            if filter(lambda t: issubclass(exc_type, t), self.exc_types):
                self._except()
                return True  # 这个返回值会决定这个错误信息是否被输入到错误流
            else:
                try:
                    raise exc_val
                finally:
                    self._finally()


class Error(Exception):
    def __init__(self, code, default_message, data=None):
        self.code = code
        self.data = data
        self.default_message = default_message
        self.message = "%d - %s" % (code, default_message)
        if data:
            self.message += "\n[DATA]: %s" % str(data)
        super(Error, self).__init__(self.message)

    def __call__(self, msg=None, data=None, **kwargs):
        return Error(self.code, msg or self.default_message, data or self.data)


NORMAL = Error(0, "正常")

if __name__ == '__main__':
    def test():
        try:
            raise NORMAL
        except Error, e:
            try:
                raise NORMAL()
            except Exception:
                from traceback import print_exc
                print_exc()


    test()
