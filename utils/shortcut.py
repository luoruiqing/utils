# coding:utf-8
"""
扩展方法 使用前考虑性能---------------------------------------------------------------------
"""
from time import sleep
from copy import deepcopy
from sys import version_info
from collections import Iterable
from functools import partial, wraps
from inspect import getargspec, getclasstree  # https://www.zhihu.com/question/19794855
from types import IntType, LongType, FloatType, StringTypes, MethodType, UnboundMethodType, \
    BuiltinMethodType, TypeType, InstanceType, ClassType

# Ellipsis 全局单例 不可回调 不可实例化 用 “is” 检测是不是本身
DefaultFunc = lambda item: item
NumberTypes = (IntType, LongType, FloatType)
MethodType = (MethodType, UnboundMethodType, BuiltinMethodType)

py2 = version_info[0] == 2
py3 = not py2


def isnum(object):
    try:
        float(object)
        return True
    except:
        return False


def defaultfloat(object):
    try:
        return float(object)
    except:
        return object


def defaultnumber(object):
    try:
        return int(object)
    except ValueError:
        try:
            return float(object)
        except ValueError:
            pass
    return object


def nexter(func):
    """ 全局单次迭代器
    @nexter
    def iter_item():
        for item in range(5):yield item
    for item in iter_item:print item
    """
    return func()


# ====================================== 方法 Methods ============================================
def closed_eval(eval_py="", must_vars=None):
    """ eval_py执行的语句 must_vars 需要使用的变量 """
    must_vars = must_vars if must_vars else {}
    for var, value in must_vars.items():
        locals()[var] = value
    return eval(eval_py)


def call_rself(method, *args, **kwargs):
    """调用方法，然后返回自身 dome: call_rself(range(55).remove, 1) """
    assert isinstance(method, MethodType)
    method(*args, **kwargs)
    return getattr(method, '__self__') or getattr(method, 'im_self')


def isiter(object):
    # 是否可以迭代，字符型除外
    if isinstance(object, Iterable) and not isinstance(object, StringTypes):
        return True
    return False


def iter(object):
    # 是否可以迭代，字符型除外
    if isinstance(object, Iterable) and not isinstance(object, StringTypes):
        return object
    return ()


def default_property(func):
    """ 只执行一次的默认值方法，如果制造一个对象有很多个属性，都是执行一次的，那就写的太多了
    class A():
        @property
        def name(self):
            if not hasattr(self, "__name"):
                setattr(self, "__name", "luoruiqing")
            return getattr(self, "__name")


    class B():
        @default_property
        def name(self):
            return "luoruiqing"


    if __name__ == '__main__':
        a = A()
        print "my name is %s." % a.name
        print "my name is %s." % a.name
        print "=============================="
        b = B()
        print "my name is %s." % b.name
        print "my name is %s." % b.name
    """
    attr_name = "__" + func.__name__  # 私有变量名称

    @property
    @wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)

    return wrapper


def retry(error=Exception, default=Ellipsis, number=3, interval=0):
    """ 重试装饰器, 错误类,默认值(无则报错), 重试次数, 重试间隔时间
            err1 = retry(default=None)(lambda: 1 + 2)
            err2 = retry(lambda: 1 + 2)
    """

    def _wrapper(*args, **kwargs):
        for attempt in range(number):
            try:
                return func(*args, **kwargs)
            except error, e:
                sleep(interval)
                if attempt == number - 1:
                    if default is Ellipsis:
                        raise e
                    return default

    def wrapper(func):
        return wraps(func)(_wrapper)

    if not (isinstance(error, TypeType) and issubclass(error, BaseException)):  # 不是参数装饰器
        func, error = error, Exception
        return wrapper(func)
    return wrapper


flat = lambda l: sum(map(flat, l), []) if isinstance(l, list) else [l]  # 压平多嵌套列表


# ======================================== 字符类型 StringType ==============================================

def to_items(item, type=tuple):
    """ 格式化为元祖，迭代类型中不包含字符 1 > (1,)  ["a"] > ["a"] """
    if isinstance(item, Iterable) and not isinstance(item, StringTypes):
        return item
    return type([item, ])


def strips(rows, chars=None):
    """ 对列表内的每一项执行strips """
    return [item.strip(chars) for item in rows]


def replaces(str, **kwargs):
    """ 多次替换 replaces("abc", a="1", b="2") """
    for k, v in kwargs.iteritems():
        str = str.replace(k, v)
    return str


def docking(rows, string=""):
    """ join时 前后也加上字符"""
    return string + string.join(rows) + string


# 过滤器 =========================================================================================




def filter_one(function=None, sequence=(), default=None):
    """ 只获得一个满足条件的数据 """
    if not hasattr(function, "__call__"):
        function = bool
    return next((item for item in sequence if function(item)), default)  # 这里很高级 (...for...) 居然是生成器


ReservedNumbersFunc = lambda item: isinstance(item, NumberTypes) or item  # 保留数字
filter_reserved_number = partial(filter, ReservedNumbersFunc)  # filter_reserved_number([0, True, 2, 3])

filter_one_reserved_number = partial(filter_one, ReservedNumbersFunc)  # 很多情况下的0也是要的  不是过滤掉

fn = filter_reserved_number
f1 = filter_one
f1n = filter_one_reserved_number


# 基础 ============================================================================================

def order_move_duplicate(listing, copy=True):
    """ 有序set 列表去重后保持有序 原地转换 不改变引用 """
    new_list = list(set(listing))
    result = sorted(new_list, key=listing.index)
    if not copy:
        listing[:] = result
        return listing
    return result


omdlist = order_move_duplicate


def check_is_admin(object=lambda name, age=22: None):
    """ 关于位置参数的问题  例如：username是一个位置参数 """
    class_func = False
    if isinstance(object, (InstanceType, ClassType, TypeType)):
        class_func = getattr(object, "__init__", None) or getattr(object, "__call__", None)
        assert class_func, "Class object has no entry method."
        object = class_func.__func__
    if isinstance(object, MethodType):
        class_func = True

    return "||||{}".format(object.func_code.co_varnames[1 if class_func else 0:])  # 确定是方法类型 isinstance(v, MethodType)


class A():
    def __init__(self, name=22):
        pass


class B(object):    pass


print type(B)
print type(B())
from types import InstanceType

print isinstance(B(), InstanceType)
print "=" * 100
# print isinstance(B, ModuleType)

# print "A(): ", check_is_admin(A())
# print "A: ", check_is_admin(A)
# print "A.__init__: ", check_is_admin(A.__init__)
# print "A().__init__): ", check_is_admin(A().__init__)
# print "[TEST]: ", isinstance(B(), ClassType)
# print "B(): ", check_is_admin(B())
# print "=" * 50
# print "B: "
# print check_is_admin(B)
# print "=" * 50
# print "B.__init__: ", check_is_admin(B.__init__)
# print "B().__init__: ", check_is_admin(B().__init__)
# print "None: ", check_is_admin()
# 将单个列表依次分段，上一个与下一个组成一个列表
'''
def subsection(listing):  # 正常版本
    """  sub(range(5)) -> [[0, 1], [1, 2], [2, 3], [3, 4]] 
         sub(range(0,15,3)) -> [[0, 3], [3, 6], [6, 9], [9, 12]]
    """
    result = []
    print reduce(lambda a, b: result.append([a, b]) or b, listing)
    return result
'''
sub = subsection = lambda listing: (reduce(lambda a, b, c=[]: c.append([a, b]) or b or c, listing + [None]))[:-1]


def check_field(field):
    key, default, func = field, Ellipsis, DefaultFunc
    if isinstance(field, Iterable) and not isinstance(field, basestring):
        if len(field) == 2:
            key, func = field
            if not hasattr(func, '__call__'):  # 2个参数 不是回调 就是默认值
                default, func = func, DefaultFunc
        elif len(field) == 3:
            key, default, func = field
            if not hasattr(func, '__call__'):  # 3个参数 可能会反了
                default, func = func, default
    else:
        key = field

    return key, default, func


def get_result(dictionary, key, default=Ellipsis, func=DefaultFunc):
    result = dictionary[key] if default is Ellipsis else dictionary.get(key, default)  # 直选 预知的错误
    return func(result) if result is not default or default is Ellipsis else result  # 得到值-转类型 没有值-设置默认值


def get(dictionary, field):
    """  主要作用是字典内获得一个值 如果值存在 获得然后转类型 如果不存在则返回默认值 如果默认值不存在 报错 KeyError
    get({},["a",None,int]) > None
    get({},["a",int]) > KeyError
    get({"a":"3"},["a",int]) > 3 type:int
    """
    key, default, func = check_field(field)
    return get_result(dictionary, key=key, default=default, func=func)


# 快捷提取 =========================================================================================

def conversion_dict(dictionary, *fields):
    """ 原地转换 直接在原有数据上修改
    dic = {"a": 1, "b": '2', "d": '{}', 1: "a"}
    conversion_dict(dic, "a", ["b", int], ["c", None, int], ["d", json_loads], 1)
    """
    for field in fields:
        key, default, func = check_field(field)
        dictionary[key] = get_result(dictionary, key, default, func)
    return dictionary


def conversion_dicts(listing, *fields):
    fields_map = [check_field(field) for field in fields]
    for dictionary in listing:
        for key, default, func in fields_map:
            dictionary[key] = get_result(dictionary, key, default, func)
    return listing


def generate_dict(dictionary, *fields):
    """ 生成新的内容 不改变旧的列表 """
    return conversion_dict(deepcopy(dictionary), *fields)


def generate_dicts(listing, *fields):
    return conversion_dicts(deepcopy(listing), *fields)


def choose_dict(dictionary, *fields):
    """ 选择字典中的几个字段 返回包含选中字段的字典
    print choose_dict({}, "fid", "eid", "events", "start_time", "ht", "vt")
    """
    result_dict = {}
    for field in fields:
        key, default, func = check_field(field)
        result_dict[key] = get_result(dictionary, key, default, func)
    return result_dict


def choose_dicts(listing, *fields):
    """ 选择字典中的几个字段 返回包含选中字段的字典
    choose_dicts([{},{},{},], "fid", "eid", "events", "start_time", "ht", "vt")
    """
    result_listing = []
    fields_map = [check_field(field) for field in fields]
    for dictionary in listing:
        result_dict = {}
        for key, default, func in fields_map:
            result_dict[key] = get_result(dictionary, key, default, func)
        result_listing.append(result_dict)
    return result_listing


def list_to_dict(rows, key):
    """ List to Dict 将列表转为字典 指定一个key
    print ltd([{"a":1},....], "a")  > {1:{"a":1},.....}
    """
    return dict((row[key], row) for row in rows)


index_dict = list_to_dict


def unpack_dict(dictionary, *fields):
    """ 选择字典中的几个字段取值 返回结果为列表 """
    return [get_result(dictionary, *check_field(field)) for field in fields]


def unpack_dicts(listing, *fields):
    fields_map = [check_field(field) for field in fields]
    return [[get_result(dictionary, key, default, func)
             for key, default, func in fields_map]
            for dictionary in listing]


def replace_key(var_dict, replace_map):
    """ [原地转换] 替换字段名称 replace_keys(rows, [("count(1)", "value"), ("host_name", "name")]) """
    for old, new in replace_map:
        var_dict[new] = var_dict.pop(old)
    return var_dict


def replace_keys(var_list, replace_map):
    return [replace_key(var, replace_map=replace_map) for var in var_list]


# 其他 ==========================================================================================
# 获得类的继承树
getclasstreestr = lambda _class: dumps(getclasstree([_class]), indent=2, default=lambda o: str(o).split(".")[-1][:-2])


# 容错类  --------------------------------------------------------------------------------------
class FaultTolerant(object):
    """ TODO 容错类 很多场景不能用还 """
    __repr__ = __str__ = lambda *args, **kwargs: 'NULL'
    __getattribute__ = __call__ = __getitem__ = __contains__ = lambda self, *args, **kwargs: self
    __getslice__ = lambda *args, **kwargs: []

    def __instancecheck__(self):
        return False

    def __subclasscheck__(self):
        return False

    # def __cmp__(self, other):
    #     print 0

    def __eq__(self, other):  # 双等号
        if other is None:
            return True
        return False

    def __ne__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __ge__(self, other):
        return False

    def __le__(self, other):
        return False

    def __isub__(self, other):
        return None

    def __len__(self):
        return 0

    def __invert__(self):
        return False


if __name__ == '__main__':
    # print check_field("c")
    # print check_field(["c", int])
    # print check_field(["c", None])
    # print check_field(["c", None, int])
    # r = conversion_dict({"a": 1, "b": '2', "d": '{}', 1: "a"},
    #                     "a", ["b", int], ["c", None, int], ["d", loads], 1)
    b = [{"a": 1, "b": '2', "d": '{}', 1: "a"}, {"a": 0, "b": '2', "c": "7", "d": '{}', 1: "a"}]
    print unpack_dicts(b, ["c", int, None])
    # print choose_dicts(b, "a", "b", "c")
    # r = get_result({"a": 1, 1: "a"}, key="d", func=loads)
    # print type(r)
    from json import dumps

    # print dumps({"test": FaultTolerant()})
    # print 0 > None > 0, FaultTolerant().a.a.a.a.b[0], '<'
    print len(FaultTolerant().a.a.a.a.a.a.a.a.a.a.a.a.a.a.a()), '<<<<<<<<'
