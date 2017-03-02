# coding:utf-8
from abc import ABCMeta, abstractmethod, abstractproperty


class __ClientBase__(object):
    __metaclass__ = ABCMeta
    DEFAULT_HEADERS = abstractproperty()  # 默认头

    @abstractmethod
    def request(self, *args, **kwargs):
        """ 返回响应对象 """

    @abstractmethod
    def get_content(self, *args, **kwargs):
        """ 返回响应体内容 """

    @abstractmethod
    def get_json(self, *args, **kwargs):
        """ 响应体json格式 """

    @abstractmethod
    def get_soup(self, *args, **kwargs):
        """ 响应体的 BS对象 """

    @abstractmethod
    def get_html_soup(self, *args, **kwargs):
        """ 响应体的HTML内容和SOUP对象 """

    @abstractmethod
    def check_alive(self, *args, **kwargs):
        """ 检测URL是否死链 """

    @abstractmethod
    def get_redirect_urls(self, *args, **kwargs):
        """ 返回所有跳转经历的URL """


if __name__ == '__main__':
    __ClientBase__()
