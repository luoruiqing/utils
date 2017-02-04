# coding:utf-8
from types import StringTypes
from collections import Iterable
from unittest import TestLoader, TestSuite, TextTestRunner, main as test_main


def to_items(item, type=tuple):
    """ 格式化为元祖，迭代类型中不包含字符 1 > (1,)  ["a"] > ["a"] """
    if isinstance(item, Iterable) and not isinstance(item, StringTypes):
        r = item
    else:
        r = type([item, ])
    return r


def test_cases(cls, cases=(), debug=True):
    '''
    :param cls: Test case class (can't be is single model).
    :param cases: Test class member models
    :param thread: ...
    :return: None
    >>> test_cases(cls, "test_dome") #单方法测试
    >>> test_cases(cls, ["test_dome1", "test_dome2"]) #多方法测试
    >>> test_cases(cls) #全部测试
    '''

    cases = to_items(cases)
    cases = [n if n.startswith("test_") else "test_" + n for n in cases]

    if debug:
        loaders = TestLoader().getTestCaseNames(cls)
        print "TEST CLASS: %s \nCASES: \n\t%s\n" % (
            cls.__name__, "\n\t".join(to_items(loaders)))

    if cases:

        suite = TestSuite()
        suite.addTests(map(lambda c: cls(c), cases))
        TextTestRunner().run(suite)
    else:
        test_main()
