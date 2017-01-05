# coding:utf-8
from copy import deepcopy
from functools import partial
from statics import NumberType, IterType, UNIQUE, DEFAULT_LAMBDA

RESERVED_NUMBERS_FUNC = lambda item: isinstance(item, NumberType) or item  # 是数字或存在

# 压平多维嵌套列表
flat = lambda l: sum(map(flat, l), []) if isinstance(l, list) else [l]


# 过滤器 =========================================================================================

def filter_one(function_or_none, sequence):
    """ 只获得一个满足条件的数据 """
    for item in sequence:
        if function_or_none(item):
            return item


filter_reserved_number = partial(filter, RESERVED_NUMBERS_FUNC)  # filter_reserved_number([0, True, 2, 3])

filter_one_reserved_number = partial(filter_one, RESERVED_NUMBERS_FUNC)  # 很多情况下的0也是要的  不是过滤掉

f = filter
fn = filter_reserved_number
fo = filter_one
fon = filter_one_reserved_number


# 过滤器 =========================================================================================



# 基础 ============================================================================================
def check_field(field):
    key, default, func = field, UNIQUE, DEFAULT_LAMBDA
    if isinstance(field, IterType) and not isinstance(field, basestring):
        if len(field) == 2:
            key, func = field
            if not hasattr(func, '__call__'):  # 2个参数 不是回调 就是默认值
                default, func = func, DEFAULT_LAMBDA
        elif len(field) == 3:
            key, default, func = field
            if not hasattr(func, '__call__'):  # 3个参数 可能会反了
                default, func = func, default
    else:
        key = field

    return key, default, func


def get_result(dictionary, key, default=UNIQUE, func=DEFAULT_LAMBDA):
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
