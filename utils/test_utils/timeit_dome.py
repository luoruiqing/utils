# coding:utf-8
from timeit import timeit
from dis import dis


# http://python.jobbole.com/86545/

def t():
    a = []
    if a:
        return True
    return False  # 这里判断后发现是假 来到这里 多读取一行 所以慢了


def t1():
    a = []
    if not a:
        return False  # 这里判断是真 不读取下一行 所以快了
    return True


def t2():
    a = []
    if len(a):
        return True
    return False


def t3():
    a = []
    if len(a) > 0:
        return True
    return False


def t4():
    a = []
    r = bool(a)
    return r


def t5():
    a = []
    return bool(a)


if __name__ == '__main__':
    print "t :", timeit(t, number=1000000)
    print "t1:", timeit(t1, number=1000000)
    print "t2:", timeit(t2, number=1000000)
    print "t3:", timeit(t3, number=1000000)
    print "t4:", timeit(t4, number=1000000)
    print "t5:", timeit(t5, number=1000000)
    print "==" * 70
    dis(t)
    print "= " * 70
    dis(t1)
    print "==" * 70
