# coding:utf-8
"""
扩展方法 使用前考虑性能---------------------------------------------------------------------
"""
from copy import deepcopy
from inspect import getcallargs  # https://www.zhihu.com/question/19794855
from collections import Iterable
from functools import partial, wraps
from types import IntType, LongType, FloatType, StringTypes

DEFAULT_FUNC = lambda item: item
UNIQUE = type("Unique", tuple([]), {"__new__": lambda *args, **kwargs: UNIQUE})  # 此方法是全局单例 实例化也是类本身
NumberType = (IntType, LongType, FloatType)

# 压平多嵌套列表
flat = lambda l: sum(map(flat, l), []) if isinstance(l, list) else [l]


def get_move_duplicate_list(listing, copy=True):
    """ 有序set 列表去重后保持有序 """
    new_list = list(set(listing))
    result = sorted(new_list, key=listing.index)
    if copy:
        return result
    listing[:] = result
    return listing


def check_is_admin(f):
    """ 关于位置参数的问题  例如：username是一个位置参数
    在装饰器 或者全部传参数时候 通过 from inspect import getcallargs 获得真实的参数
    @check_is_admin
    def get_food(username, food='chocolate'):
        return "{0} get food: {1}".format(username, food)
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        func_args = getcallargs(f, *args, **kwargs)
        print func_args
        if func_args.get('username') != 'admin':
            raise Exception("This user is not allowed to get food")
        return f(*args, **kwargs)

    return wrapper


def to_items(item, type=tuple):
    """ 格式化为元祖，迭代类型中不包含字符 1 > (1,)  ["a"] > ["a"] """
    if isinstance(item, Iterable) and not isinstance(item, StringTypes):
        r = item
    else:
        r = type([item, ])
    return r


def replaces(str, **kwargs):
    """ 多次替换 replaces("abc", a="1", b="2") """
    for k, v in kwargs.iteritems():
        str = str.replace(k, v)
    return str


def closed_eval(eval_py="", must_vars=None):
    """ eval_py执行的语句 must_vars 需要使用的变量 """
    must_vars = must_vars if must_vars else {}
    for var, value in must_vars.items():
        locals()[var] = value
    return eval(eval_py)


# 过滤器 =========================================================================================

RESERVED_NUMBERS_FUNC = lambda item: isinstance(item, NumberType) or item  # 是数字或存在


def filter_one(function, sequence, default=None):
    """ 只获得一个满足条件的数据 """

    if not hasattr(function, "__call__"):
        function = bool
    return next((item for item in sequence if function(item)), default)  # 这里很高级 (...for...) 居然是生成器


filter_reserved_number = partial(filter, RESERVED_NUMBERS_FUNC)  # filter_reserved_number([0, True, 2, 3])

filter_one_reserved_number = partial(filter_one, RESERVED_NUMBERS_FUNC)  # 很多情况下的0也是要的  不是过滤掉

f = filter
fn = filter_reserved_number
fo = filter_one
fon = filter_one_reserved_number


# 基础 ============================================================================================
def check_field(field):
    key, default, func = field, UNIQUE, DEFAULT_FUNC
    if isinstance(field, Iterable) and not isinstance(field, basestring):
        if len(field) == 2:
            key, func = field
            if not hasattr(func, '__call__'):  # 2个参数 不是回调 就是默认值
                default, func = func, DEFAULT_FUNC
        elif len(field) == 3:
            key, default, func = field
            if not hasattr(func, '__call__'):  # 3个参数 可能会反了
                default, func = func, default
    else:
        key = field

    return key, default, func


def get_result(dictionary, key, default=UNIQUE, func=DEFAULT_FUNC):
    result = dictionary[key] if default is UNIQUE else dictionary.get(key, default)  # 直选 预知的错误
    return func(result) if result is not default or default is UNIQUE else result  # 得到值-转类型 没有值-设置默认值


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
