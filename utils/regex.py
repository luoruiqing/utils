# coding:utf-8
from re import search, _pattern_type as RegexType


# ((?!字符).*?) 非字符
# regex ----------------------------------------------------------------------

def re_search(pattern, string, flags=0):
    if isinstance(pattern, RegexType):
        r = pattern.search(string, flags)
    else:
        r = search(pattern, string, flags)
    return r


def r(pattern, string):
    m = re_search(pattern, string)
    if m:
        return m.groups()


def r0(pattern, string):
    m = re_search(pattern, string)
    if m:
        return m.group(0)


def r1(pattern, string):
    m = re_search(pattern, string)
    if m and len(m.groups()) > 0:
        return m.group(1)


def r_of(patterns, string):
    for p in patterns:
        x = r(p, string)
        if x:
            return x


def r0_of(patterns, string):
    for p in patterns:
        x = r0(p, string)
        if x:
            return x


def r1_of(patterns, string):
    for p in patterns:
        x = r1(p, string)
        if x:
            return x
