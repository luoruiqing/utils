# coding:utf-8

from glob import glob
from collections import Iterable
from os import path, remove, makedirs
from types import IntType, LongType, FloatType, StringTypes

NumberType = (IntType, LongType, FloatType)


def to_items(item, type=tuple):
    """ 格式化为元祖，迭代类型中不包含字符 1 > (1,)  ["a"] > ["a"] """
    if isinstance(item, Iterable) and not isinstance(item, StringTypes):
        r = item
    else:
        r = type([item, ])
    return r


def ensure_path(path):  # 可以优化
    #  os.path.isdir(path)  os.path.isfile(path):
    """ 路径不存在 自动创建路径 """
    file_name, (path, ext) = '', path.splitext(path)  # 剥离ext
    if ext:  # ext存在 剥离文件名
        path, file_name = path.split(path)

    if not path.exists(path):
        makedirs(path)
    return path.join(path, file_name + ext)


def remove_files_by_ext(pattern="*.pyc"):
    # TODO 未完成
    """  从执行目录开始 清楚所有符合条件的文件 """
    for item in to_items(pattern):
        for file in glob(item):
            if path.exists(file):
                remove(file)
