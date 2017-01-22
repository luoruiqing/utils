# coding:utf-8
"""
    一个关于处理URL的类，目的是为了方便 简洁
"""
from types import NoneType
from urllib import quote, unquote
from requests.models import RequestEncodingMixin
from urlparse import urlparse, urlunparse, parse_qs


# @property
# def ip(self):  # ip地址
#     return gethostbyname(self._url)
# @property
# def get_server(self):
#     return getservbyname('http', 'tcp')

def quotes(items):
    return map(lambda item: quote(str(item)), items)


class UrlParse():
    """
    解析url 获得一些url相关的信息
    这里不会管key重复的情况
    """
    encode_params = staticmethod(RequestEncodingMixin._encode_params)

    def __init__(self, url):
        self.default_url = unquote(url)  # 解码一次 保证能看出来的尽量看出来
        self.parse_object = urlparse(url)
        self.params = parse_qs(self.parse_object.query)
        self.scheme = (self.parse_object.scheme or "HTTP").upper()  # 协议
        self.netloc = self.parse_object.netloc  #
        self.path = self.parse_object.path  # 路径
        self.fragment = self.parse_object.fragment  # 返回#号的指向 例如 #top ->top

    @property
    def url(self):
        return urlunparse((
            self.scheme.lower(),
            self.netloc,
            self.path,
            '',
            self.params_str,
            self.fragment))

    def replace(self, scheme=None, netloc=None, path=None, params=None, fragment=None):
        """ 以上任何一个参数为 空字符类型 均认为替换为空 """
        self.scheme = self.scheme.lower() if isinstance(scheme, NoneType) else scheme
        self.netloc = self.netloc if isinstance(netloc, NoneType) else netloc
        self.path = self.path if isinstance(path, NoneType) else path
        self.params = self.params if isinstance(params, NoneType) else params
        self.fragment = self.fragment if isinstance(fragment, NoneType) else fragment
        return self

    @property
    def params_str(self):  # 参数字符类型
        return self.encode_params(self.params)

    def get_param(self, word, default=None):
        """ 获得url中一个参数 """
        result = self.params.get(word, [default])[0]
        if result:
            result = unquote(result)
        return result

    def add_params(self, key, *items):
        """ 添加参数 up.add_params("2", 15, "hi py").add_params("2", 15, 14).url """
        self.params.setdefault(key, []).extend(quotes(items))
        return self

    def replace_params(self, key, *items):
        self.params[key] = quotes(items)
        return self

    def remove_params(self, key):
        del self.params[key]
        return self


up = UrlParse
if __name__ == '__main__':
    url = "http://www.baidu.com/s?ie=utf-8#top"
    print UrlParse(url).params.get("ie")
    print UrlParse(url).get_param("oq")
    print UrlParse(url).add_params("params", 15, 14, "python good!").replace(scheme='HTTPS').remove_params('ie').url
    print UrlParse(url).params
