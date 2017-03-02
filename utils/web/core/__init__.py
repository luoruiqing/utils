# coding:utf-8
from base import __ClientBase__
from types import BooleanType
from abc import abstractmethod
from re import _pattern_type as RegexType
from user_agent import generate_user_agent


def get_platform_agent(platform=None, browser=None):
    platform = platform.lower()
    if platform == "android":
        return "Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
    elif platform == "iphone":
        return "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E238 Safari/601.1"
    return generate_user_agent(platform=platform, navigator=browser)


class Controller:
    __enter__ = lambda self: self
    __del__ = __exit__ = lambda self, *args, **kwargs: self.close()  # 关闭会话


class ClientBaseException(Exception):
    pass


class InterceptRedirectException(ClientBaseException):
    """ 重定向到不允许的地址时报错"""


class ClientBase(__ClientBase__, Controller):
    DEFAULT_HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Charset': 'UTF-8,*;q=0.5',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36'
    }
    # 如果为True认为要按照移动端请求，默认为安卓
    check_platform = staticmethod(lambda p, default='Android': default if isinstance(p, BooleanType) and p else p)

    def __init__(self, not_redirect=(), redirect=True, proxies=None, headers=None, platform=None, timeout=5,
                 retries=3, interval=3):
        """
        :param not_redirect: 防止跳转的URL 屏蔽跳转主页或者404页面
            1. 可以是全路径  例如:  'http://www.youku.com/index/y404'
            2. 可以是正则    例如:  compile(r'youku.com/index/y(\d+)')
            3. 可以是其子串  例如: ' /index/y404'
        :param redirect: 是否允许跳转，可以设置全部不允许跳转主页
        :param proxies: 全局代理
        :param headers: 所有请求默认头
        :param platform: HTTP请求头时的平台 ("win", "linux", "mac", 'android', "iphone")
        :param timeout: 默认请求超时时间
        :param timeout: 默认请求失败重试次数
        :param timeout: 默认请求失败后重试间隔时间
        """
        self.not_redirect = not_redirect
        self.redirect = redirect
        self.proxies = proxies
        self.platform = platform
        self.timeout = timeout
        self.retries = retries
        self.interval = interval
        self.headers = self.DEFAULT_HEADERS.copy()
        self.default_user_agent = self.headers["User-Agent"] = generate_user_agent(platform=platform)
        self.headers.update(headers or {})

    @abstractmethod
    def request(self, url, data=None, headers=None, method=None, redirect=None, refer=None, platform=False,
                proxies=None,
                timeout=None, retries=None, interval=None, *args, **kwargs):
        """
        :param url: url地址
        :param data: 字符串(符合HTTP参数形式的字符串)或者字典
        :param headers: 头，方法级别属性将会覆盖默认
        :param method: 请求方法默认GET
        :param redirect: 跳转，方法级别属性将会覆盖默认
        :param refer: 头Refer属性
        :param platform: 本次请求 user-agent使用 手机端默认使用Android
        :param proxies: 代理
        :param retries: 请求失败重试次数
        :param timeout: 超时时间
        :param interval: 失败重试间隔
        :param args:
        :param kwargs:
        :return: 响应对象
        """

    def check_not_redirect(self, item):
        for _item in self.not_redirect:
            if isinstance(_item, RegexType):
                if _item.search(item):
                    return True
            elif _item in item or _item == item:
                return True

    def close(self, *args, **kwargs):
        """ 当Client对象被回收时的收尾工作 """


__all__ = [
    "get_platform_agent", "ClientBaseException",
    "InterceptRedirectException", "ClientBase",
]

if __name__ == '__main__':
    ClientBase()
