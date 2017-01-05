# coding:utf-8
REDIRECT_CODES = (301, 302)  # HTTP跳转状态码
# 默认头
DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36'
}
# 关闭链接头
CLOSE_CONN_HEADERS = DEFAULT_HEADERS.copy()
CLOSE_CONN_HEADERS['Connection'] = 'close'
