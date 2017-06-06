# coding:utf-8
"""
    使用俩个元类的情况，例如：一边抽象接口一遍需要做其他操作
"""
from __future__ import unicode_literals
from abc import ABCMeta, abstractproperty


class MyMetaClass(type):
    def __new__(cls, name, bases, attr):
        print "我要在这里对我的被抽象类操作", name
        return type.__new__(cls, name, bases, attr)


class APIMetaClasses(ABCMeta, MyMetaClass):
    """"""


class MyClassBasic:
    """ 父类 """
    __metaclass__ = APIMetaClasses

    @abstractproperty
    def first_method(self):
        """ 必须实现的抽象方法 """


class MyClass(MyClassBasic):
    """ 子类 """
    # first_method = lambda self: None


if __name__ == '__main__':
    MyClass()
