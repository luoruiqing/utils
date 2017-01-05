# coding:utf-8
from chardet import detect
from sys import getfilesystemencoding

default_code = getfilesystemencoding()
if default_code.lower() == 'ascii':
    default_code = 'utf-8'


def get_codeformat(string):
    """ 获得编码格式 """
    return detect(string)["encoding"]


def recoding(string, encode="utf-8"):
    try:
        charset = get_codeformat(string)
    except ValueError:
        return string
    if isinstance(string, unicode):
        string = string.decode('unicode-escape')
    if charset != encode:
        string = string.decode(charset).encode(encode)
    return string


def recoding_sys(string, coding="utf-8"):
    """ 根据系统编码解码后转码 """
    return string.decode(getfilesystemencoding()).encode(coding)
