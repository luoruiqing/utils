# coding:utf-8

from time import sleep
from requests import Session
from traceback import print_exc
from json import loads as json_loads
from logging import getLogger, DEBUG
from types import NoneType, UnicodeType
from BeautifulSoup import BeautifulSoup as BS
from core import ClientBase, get_platform_agent, InterceptRedirectException

logger = getLogger(__name__)
logger.setLevel(DEBUG)


class Client(ClientBase):
    def __init__(self, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.session = Session()  # requests 在一个session中请求相同的站点会复用TCP链接 性能提升
        self.session.headers.update(self.headers)  # 默认头
        if not isinstance(self.proxies, NoneType):
            self.session.proxies = self.proxies  # 整个会话中使用的代理

    def request(self, url, data=None, headers=None, method=None, redirect=None, refer=None, platform=None,
                proxies=None, timeout=None, retries=None, interval=None, *args, **kwargs):
        method = kwargs.pop("method", method or 'POST' if data else 'GET')
        # TODO DATA 有个类型问题
        redirect = self.redirect if isinstance(redirect, NoneType) else redirect
        headers = headers or {}
        if platform:
            headers["User-Agent"] = get_platform_agent(self.check_platform(platform or self.platform))
        if refer:
            headers['Referer'] = refer

        for retrying in range(self.retries if isinstance(retries, NoneType) else retries):
            try:
                logger.debug("request: %s %s" % (url, ("retrying %s..." % retrying if retrying > 0 else "")))
                response = self.session.request(method=method, url=url, data=data, headers=headers,
                                                timeout=timeout or self.timeout, allow_redirects=redirect,
                                                stream=True, proxies=proxies, *args, **kwargs)

                for rep in response.history + [response]:
                    if self.check_not_redirect(rep.url):
                        raise InterceptRedirectException()
                return response
            except InterceptRedirectException:
                raise
            except:
                print_exc()
                if retries == retrying + 1:
                    raise
                sleep(interval or self.interval)

    def get_content(self, *args, **kwargs):
        string = self.request(*args, **kwargs).content
        if isinstance(string, UnicodeType):
            string = string.decode('unicode-escape')
        return string

    def get_json(self, *args, **kwargs):
        """
        get_json(url, func=lambda s: s.replace("getData(", "")[:-2])
        """
        func = kwargs.pop("func", None)
        if func:
            return json_loads(func(self.get_content(*args, **kwargs)))
        else:
            return self.request(*args, **kwargs).json()

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


class PhantomJsClient():
    phantom_host = "http://127.0.0.1:8080"  # PhantomJS 服务器地址

    def request(self, url, rendering_time=0, javascript="", render=False, cookies=None, headers=None,
                load_images=False):
        data = {
            "url": url,
            "render": render,
            "renderingTime": rendering_time,
            "javaScript": javascript,
            "cookies": cookies or {},
            "headers": headers or {},
            "loadImages": load_images,
        }
        with Session() as session:
            return session.request(url=self.phantom_host, method="POST", data=data)


if __name__ == '__main__':
    from logging import basicConfig

    basicConfig()
    url = "http://www.baidu.com"
    with Client(not_redirect=["albumlist/show"], redirect=True) as client:
        pass
