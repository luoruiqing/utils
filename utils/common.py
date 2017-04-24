# coding:utf-8
from re import compile
from recode import recoding
from HTMLParser import HTMLParser

number_regex = compile(r"([\d\.]+)")

unescape = HTMLParser().unescape  # HTML 转义


def convert_number(string):
    """格式化数字"""
    string = recoding(string)
    y, w, q = ("亿", "万", "千")
    r, n = number_regex.search(string), None
    if r:
        n = r.group(1)
    result = float(n)
    if y in string and string.index(y) == string.index(n) + len(n):
        result *= 100000000
    elif w in string and string.index(w) == string.index(n) + len(n):
        result *= 10000
    elif q in string and string.index(q) == string.index(n) + len(n):
        result *= 1000
    return int(result)
