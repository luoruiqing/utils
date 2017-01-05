# coding:utf-8
from sys import version_info

# python 版本
pyver = float('%s.%s' % version_info[:2])
# 正无穷
POSITIVE_INFINITY = float("inf")
# 负无穷
NEGATIVE_INFINITY = float("-inf")
# 无意以的默认方法
DEFAULT_LAMBDA = lambda item: item
# 全局单例
UNIQUE = type("Unique", tuple([]), {"__new__": lambda *args, **kwargs: UNIQUE})  # 此方法是全局单例 实例化也是类本身

