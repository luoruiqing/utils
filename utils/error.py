# coding:utf-8
from sys import exc_info
from traceback import extract_tb


def get_error_info():
    """ 获得错误信息 返回的信息依次为 错误类型，错误原因，错误文件路径，错误文件行号，错误方法名称，错误行的代码内容 """
    exc_type, exc_reason, exc_tb = exc_info()
    file_path, line, func_name, err_line_content = extract_tb(exc_tb)[-1]
    return exc_type, exc_reason, file_path, line, func_name, err_line_content


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
