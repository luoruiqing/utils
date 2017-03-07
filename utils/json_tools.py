# coding:utf-8
from json import loads, dumps
from collections import OrderedDict


def loads_order(string):
    """加载json保证字典顺序"""
    return loads(string, object_pairs_hook=OrderedDict)


def format_json(dict_object, indent=4, *args, **kwargs):
    """ 格式化为易于查看的字典 """
    indent = kwargs.pop("indent", indent)
    return dumps(dict_object, indent=indent, *args, **kwargs)


def loads_quotes(string, *args, **kwargs):
    """ 格式化因为单双引号引起问题的JSON """
    return loads(dumps(string), *args, **kwargs)
