# coding:utf-8
from copy import copy
from types import DictType
from urllib import urlencode
from logging import getLogger, DEBUG
from json import loads as json_loads
from tornado.gen import coroutine, Return
from BeautifulSoup import BeautifulSoup as BS
from tornado.httpclient import HTTPRequest, AsyncHTTPClient

'''
 url, method="GET", headers=None, body=None,
                 auth_username=None, auth_password=None, auth_mode=None,
                 connect_timeout=None, request_timeout=None,
                 if_modified_since=None, follow_redirects=None,
                 max_redirects=None, user_agent=None, use_gzip=None,
'''
logger = getLogger()
logger.setLevel(DEBUG)

HTTPRequest._DEFAULTS["allow_nonstandard_methods"] = True  # 必须设置这个属性


def recoding(string, encode="utf-8"):
    if isinstance(string, unicode):
        return string.decode('unicode-escape')
    return string


class Client:
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Charset': 'UTF-8,*;q=0.5',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36'
    }

    def __init__(self):
        self.async_client = AsyncHTTPClient()

    @coroutine
    def request(self, *args, **kwargs):
        """重试的时候需要用同步的方式 检测599的http code 这种状态代表为等待中"""
        _args, _kwargs = map(copy, args, kwargs)  # 默认参数
        args = list(args)
        url = kwargs.pop("url", args.pop(0))
        headers = self.DEFAULT_HEADERS.copy()
        headers.update(kwargs.pop("headers", {}))

        request_timeout = kwargs.pop("request_timeout", 15)

        data = kwargs.pop("body", None) or kwargs.pop("data", {})
        body = urlencode(data) if isinstance(data, DictType) else data

        logger.debug("request: %s" % url)
        response = yield self.async_client.fetch(
            url, body=body, headers=headers, request_timeout=request_timeout, *args, **kwargs)
        if response.code == 599:  # 599是taonado默认超时，需要重试
            raise Return((yield self.request(*_args, **_kwargs)))
        raise Return((response))

    @coroutine
    def get_content(self, *args, **kwargs):
        response = yield self.request(*args, **kwargs)
        raise Return(recoding(response.body))

    @coroutine
    def get_json(self, *args, **kwargs):
        response = yield self.request(*args, **kwargs)
        raise Return(json_loads(response.body))

    @coroutine
    def get_soup(self, *args, **kwargs):
        _, soup = yield self.get_html_soup(*args, **kwargs)
        raise Return(soup)

    @coroutine
    def get_html_soup(self, *args, **kwargs):
        content = yield self.get_content(*args, **kwargs)
        soup = BS(content, fromEncoding="utf-8")
        raise Return([content, soup])


if __name__ == '__main__':
    from tornado.ioloop import IOLoop


    @coroutine
    def test():
        url = "http://www.baidu.com"
        r = yield Client().get_html_soup(url)
        print r


    IOLoop.current().run_sync(test)
