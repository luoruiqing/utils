# !/usr/bin env python
# coding:utf-8
__auth__ = "luoruiqing@waqu.com"


# 可以返回多个URL 所有跳转的URL

class Redirected:
    LINE = b"\r\n"
    LINE2 = b"\r\n" * 2
    HEADERS = {
        "Connection": "keep-alive",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
    }

    def __init__(self, url, timeout=10):
        self.url = url
        self.timeout = timeout
        from urlparse import urlparse
        self.params, self.port = urlparse(url), 80
        netloc = self.host = self.params.netloc
        if ":" in netloc:
            self.host, self.port = netloc.split(":", 1)
        self.path = self.params.path or "/"

    def socket(self):
        url = None
        client = None
        response = b""
        try:
            from socket import socket
            from socket import AF_INET, SOCK_STREAM
            content_list = ["GET %s HTTP/1.1" % self.path, "Host: %s" % self.host]
            content_list.extend(["%s: %s" % (k, v) for k, v in self.HEADERS.items()])
            content = self.LINE.join(content_list) + self.LINE2

            client = socket(AF_INET, SOCK_STREAM)
            client.connect((self.host, 80))
            client.send(content)
            # read flow
            while True:
                response += client.recv(1024)
                if self.LINE2 in response or not response:
                    break
            headers = (response.split(self.LINE2) or [b""])[0].lower()
            if "location" in headers:
                from re import search
                address = search(r"location:(.*?)\n", headers)
                if not address is None: address = address.group(1)
                self.path = address.strip()
                url = self.socket()
            else:
                port = "" if self.port == 80 else str(self.port)
                url = self.host + port + self.path
        finally:
            if client:
                client.close()
        return url

    def httplib(self):
        url = None
        conn = None
        self.agree = ""
        try:
            from httplib import HTTPConnection
            conn = HTTPConnection(self.host, self.port, timeout=self.timeout)
            conn.request(method="GET", url=self.path, body=self.params.params, headers=self.HEADERS)
            response = conn.getresponse()
            conn.close()
            if response.status in (302, 301):
                from re import search
                nu = response.getheader("location")
                address = search(r"(http://|https://)(.*?)(/.*)", nu)
                if address:
                    self.agree, self.host, self.path = address.groups()
                    print self.agree, self.host, self.path
                url = self.httplib()
            else:
                url = self.agree + self.host + self.path
        finally:
            if conn:
                conn.close()
        print self.agree
        return url

    def urllib(self):
        raise NotImplementedError()

    def requests(self):
        from requests import Request
        return Request(self.url).url

    def getRedirect(self):
        pass

    def getIp(url):
        pass


def get_default_logger():
    from sys import stderr
    from logging import StreamHandler, getLogger, DEBUG

    default_logger = getLogger(__name__)
    default_logger.setLevel(DEBUG)
    default_logger.addHandler(StreamHandler(stderr))
    return default_logger


if __name__ == '__main__':
    # print Redirected(
    #     "http://www.youku.com/playlist_show/id_18820116.html"
    # ).socket()

    print Redirected(
        "http://www.youku.com/playlist_show/id_18820116.html"
    ).httplib()

































#
#
# def get_redirected_url(url, timeout=10):
#     '''
#     >>> get_redirected_url("http://www.baidu.com")
#     :param url: .
#     :param timeout: .
#     :return: Bool
#     '''
#     from urlparse import urlparse
#     from httplib import HTTPConnection
#     try:
#         params, port = urlparse(url), 80
#         netloc = host = params.netloc
#         if ":" in netloc: host, port = netloc.split(":", 1)
#         conn = HTTPConnection(host, port, timeout=timeout)
#         conn.request(method="GET", url=params.path or "/", body=params.params)
#         response = conn.getresponse()
#         conn.close()
#         if response.status in (302, 301):
#             url = response.getheader("location")
#             return get_redirected_url(url)
#     except:
#         from requests import get
#         url = get(url).url
#     return url
#
#
# def get_redirect_status(url):
#     new_url = get_redirected_url(url)
#     if url == new_url:
#         return False
#     return True
#
#
# def url_size(self, url):
#     '''获得头长度'''
#     import urllib2
#     opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
#     urllib2.install_opener(opener)
#     response = urllib2.urlopen(url)
#     size = int(response.headers['content-length'])
#     return size
#
#
#
# if __name__ == '__main__':
#     print get_redirected_url(
#         "http://www.wasu.cn/wap/Api/getVideoUrl/id/7386742/key/659482c90f2ffd2d5d8ba8b09b3f12a3/url/aHR0cDovL2h6bG9hZC1hbC53YXN1LmNuL3Bjc2FuMTEvbWFtcy92b2QvMjAxNjA0LzIwLzA5LzIwMTYwNDIwMDkwNDU2ODE0MTZjNGU0ZmJfNDI4N2Q4MWUubXA0/type/txt")
