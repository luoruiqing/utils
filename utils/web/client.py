# coding:utf-8

from time import sleep
from abc import ABCMeta
from itertools import count
from requests import Session
from urlparse import urlparse
from types import BooleanType
from traceback import print_exc
from json import loads as json_loads
from logging import getLogger, DEBUG
from core import ClientBase, get_platform_agent, InterceptRedirectException
from types import NoneType, UnicodeType, StringTypes
from user_agent import generate_navigator, generate_user_agent

# from common import recoding, get_file_name, DEATH_CHAIN_CODES, REDIRECT_CODES, DEFAULT_HEADERS, CLOSE_CONN_HEADERS
# stream=True
# getLogger("requests").setLevel(logging.WARNING)
# from operator import itemgetter

from BeautifulSoup import BeautifulSoup as BS

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



if __name__ == '__main__':
    from logging import basicConfig

    basicConfig()
    url = "http://www.baidu.com"
    from json import dumps
    from re import compile

    with Client(not_redirect=["albumlist/show"], redirect=True) as client:
        # print client.request('http://video2.91huagu.com/dyj168/v/20160601/ghlp.mp4').headers
        # print client.download_file('http://video2.91huagu.com/dyj168/v/20160601/ghlp.mp4')
        # print client.get_redirect_urls("http://i.youku.com/u/UMTc2MDY1MjM5Ng==")
        url = "http://www.youku.com/playlist_show/id_22097096.html"
        # url = "https://movie.douban.com/trailer/video_url?tid=127848&hd=0"
        response = client.request(url)
        for key, value in response.headers.items():
            print key, value
        with open("s.mp4", "wb") as f:
            f.write(response.content)
