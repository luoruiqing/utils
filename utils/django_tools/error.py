class ErrorBase(Exception):
    """ 全局基础对象 """


class ErrorCodeBase(ErrorBase):
    """ 代码错误基类 """
    CODES = {}  # 所有的CODE

    DATA = {}  # 引用对象
    _data = None  # 非引用对象

    @property
    def data(self):
        return self._data or self.DATA

    def __init__(self, code=200, message='', description='', status=400, strformat=True):
        assert code not in self.CODES, f"Error code duplication({code}) - {message}."
        self.code = code
        self.status = status
        self.message = message
        self.description = description
        self.CODES[code] = self
        self.strformat = strformat  # 是否需要格式化message

    def __call__(self, *args, **kwargs):
        self._data = kwargs.pop("data", None)  # data 是占用字段
        if args:
            self.verbose_name = self.verbose_name.format(*args)
            self.description = self.description.format(*args)
        elif kwargs:
            self.verbose_name = self.verbose_name.format(**kwargs)
            self.description = self.description.format(**kwargs)
        return self

    def __str__(self):
        return f'[{self.code}]: {self.message}' + (f'\n[DATA]: {self.data}' if self.data else '') if self.strformat else self.message
        # def __format__(self, format_spec):
        #     pass


class ErrorCode(ErrorCodeBase):
    """ 全局错误 """


# DoesNotExist
SERVER_ERROR = ErrorCode(400001, '服务器内部错误!', description='Server internal error!')
CONNECT_NOT_EXISTENT_OR_DISABLE = ErrorCode(400005, '连接被禁用或不存在 - {}!', description='The connection - {} is disabled or nonexistent!')
NO_DATA = ErrorCode(400006, '无数据!', description='No data!', status=200)
DATA_IS_NULL = ErrorCode(400007, '当前筛选条件下没有数据', description='Data Is Null', status=200, strformat=False)

if __name__ == '__main__':
    from traceback import print_exc
    from time import sleep

    print("错误实例:", isinstance(DASHBOARD_ID, ErrorCode))
    p = lambda: (sleep(0.3), print("*" * 50))
    p()
    print(SERVER_ERROR)
    p()
    print("*" * 20)
    try:
        ErrorCode(100)
        ErrorCode(100)
    except:
        print_exc()
    p()
    try:
        raise SERVER_ERROR
    except:
        print_exc()
    p()
    try:
        raise SERVER_ERROR(data={"name", "luoruiqing"})
    except Exception as error:
        raise Exception() from error
