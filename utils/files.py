# coding:utf-8
from glob import glob
from random import sample
from collections import Iterable
from os.path import join, dirname, exists
from os import path as os_path, remove, makedirs, walk
from types import IntType, LongType, FloatType, StringTypes

NumberType = (IntType, LongType, FloatType)
base = [
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]


def to_items(item, type=tuple):
    """ 格式化为元祖，迭代类型中不包含字符 1 > (1,)  ["a"] > ["a"] 

    >>> print to_items(1)
    (1,)
    >>> print to_items("a", type=list)
    ['a']
    >>> from types import GeneratorType
    >>> case = to_items((x for x in range(5)))
    >>> isinstance(case, GeneratorType)
    True
    """
    if isinstance(item, Iterable) and not isinstance(item, StringTypes):
        r = item
    else:
        r = type([item, ])
    return r


def get_abspath(path, __file__="."):
    """ 根据相对路径 获得绝对路径  __file__ 其他文件的属性，用来直接定位
        其他文件 执行 get_abspath("test.txt",__file__) 
    """
    return join(dirname(__file__), path)


def ensure_path(path):  # 可以优化
    #  os.path.isdir(path)  os.path.isfile(path):
    """ 路径不存在 自动创建路径 """
    file_name, (path, ext) = '', os_path.splitext(path)  # 剥离ext
    if ext:  # ext存在 剥离文件名
        path, file_name = os_path.split(path)
    if not os_path.exists(path):
        makedirs(path)
    return os_path.join(path, file_name + ext)


def remove_files_by_ext(pattern="*.pyc"):
    # TODO 未完成
    """  从执行目录开始 清楚所有符合条件的文件 """
    for item in to_items(pattern):
        for file in glob(item):
            if exists(file):
                remove(file)


def random_filename(limit=16, ext=''):
    return "".join(sample(base, limit)) + ext


def get_files(root):
    """
    :param root: 一级根目录
    :return: 所有文件的相对路径
    """
    return [join(root, file) for root, dirs, files in walk(root) for file in files]
