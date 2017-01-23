# coding:utf-8
from time import sleep
from abc import ABCMeta
from types import NoneType
from itertools import count
from requests import Session
from types import BooleanType
from traceback import print_exc
from json import loads as json_loads
from logging import getLogger, DEBUG
from user_agent import generate_user_agent

# from common import recoding, get_file_name, DEATH_CHAIN_CODES, REDIRECT_CODES, DEFAULT_HEADERS, CLOSE_CONN_HEADERS

# getLogger("requests").setLevel(logging.WARNING)
# from operator import itemgetter

from simplejson import JSONDecodeError
from BeautifulSoup import BeautifulSoup as BS

logger = getLogger(__name__)
logger.setLevel(DEBUG)


class Client(object):
    """
    >>> html = Client().get_content("http://www.wasu.cn")
    """
    DEFAULT_TIMEOUT = 5
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Charset': 'UTF-8,*;q=0.5',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36'
    }

    def __init__(self, not_found_urls=(), redirect=True, proxies=None, headers=None, refer=None,
                 timeout=DEFAULT_TIMEOUT):
        self.not_found_urls = not_found_urls  # 这个属性用来屏蔽404页面、主页面以及要防止跳转到主页
        self.redirect = redirect
        _headers = self.DEFAULT_HEADERS.copy()
        _headers["User-Agent"], _headers["Referer-Agent"] = generate_user_agent(), refer
        _headers.update(headers)
        self.session = Session()  # requests 在一个session中请求相同的站点会复用TCP链接 性能提升
        if not isinstance(proxies, NoneType):
            self.session.proxies = proxies  # 整个会话中使用的代理
        self.session.headers.update(_headers)

    def request(self, url, data=None, headers=None, redirect=None, refer=None, proxies=None, retries=3,
                timeout=DEFAULT_TIMEOUT, retry_interval=3, *args, **kwargs):
        method = kwargs.pop("method", 'POST' if data else 'GET')
        redirect = redirect if isinstance(redirect, BooleanType) else self.redirect
        if refer:
            headers = headers if not isinstance(headers, NoneType) else {}
            headers['Referer'] = refer

        for retrying in count(0):
            try:
                logger.debug("request: %s %s" % (url, ("retrying %s..." % retrying if retrying > 0 else "")))
                response = self.session.request(method=method, url=url, data=data, headers=headers, timeout=timeout,
                                                allow_redirects=redirect, stream=True, proxies=proxies, *args, **kwargs)
                return response
            except:
                print_exc()
                if retries == retrying + 1:
                    raise
                sleep(retry_interval or 0)

    def request_unredirect(self, *args, **kwargs):
        response = self.request(redirect=False, *args, **kwargs)
        return response

    def get_content(self, *args, **kwargs):
        return recoding(self.request(*args, **kwargs).content)

    def get_json(self, *args, **kwargs):
        """
        get_json(url, func=lambda s: s.replace("getData(", "")[:-2])
        """
        func = kwargs.pop('func', lambda argv: args)
        content = self.get_content(*args, **kwargs)
        try:
            result = json_loads(func(content))
        except JSONDecodeError:
            result = json_loads(func(content))
        return result

    def get_soup(self, *args, **kwargs):
        return self.get_html_soup(*args, **kwargs)[1]

    def get_html_soup(self, *args, **kwargs):
        content = self.get_content(*args, **kwargs)
        try:
            soup = BS(content, from_encoding="utf-8")
        except TypeError:
            soup = BS(content, fromEncoding="utf-8")
        return content, soup

    def check_alive(self, *args, **kwargs):
        response = self.request(redirect=False, *args, **kwargs)
        if response.status_code in (404, 403, 503):
            return False
        return True

    def get_redirect_urls(self, *args, **kwargs):
        response = self.request(redirect=True, *args, **kwargs)
        return [history.url for history in response.history + [response]]

    __enter__ = lambda self: self
    __exit__ = lambda self, *args, **kwargs: self.session.close()  # 关闭会话


class ClientBase(Client):
    __metaclass__ = ABCMeta
    not_found_urls = ()
    redirect = True
    proxies = {}
    headers = {}
    refer = None
    timeout = 5

    def __init__(self):
        super(ClientBase, self).__init__(not_found_urls=self.not_found_urls, redirect=self.redirect, refer=self.refer,
                                         proxies=self.proxies, headers=self.headers, timeout=self.timeout)


if __name__ == '__main__':
    from logging import basicConfig

    basicConfig()
    url = "http://www.baidu.com"
    with Client(redirect=True) as client:
        # print client.request('http://video2.91huagu.com/dyj168/v/20160601/ghlp.mp4').headers
        print client.download_file('http://video2.91huagu.com/dyj168/v/20160601/ghlp.mp4')
