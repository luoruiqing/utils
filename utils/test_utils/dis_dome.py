# coding:utf-8
from dis import dis


def test():
    x = 1
    if x < 3:
        return "yes"
    else:
        return "no"


def get_func_constant():
    """ 取出方法体内定义的常量 """

    def dome():
        x = 99

    consts = dome.__code__.co_consts  # 所有常量
    varnames = dome.__code__.co_varnames  # 所有变量名字
    print consts[varnames.index("x") + 1]


if __name__ == '__main__':
    dis(test)
    get_func_constant()
