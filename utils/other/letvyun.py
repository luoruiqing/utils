# coding:utf-8
'''
乐视云的破解，私钥KEY可能不同网站也不同
'''
__auth__ = "luoruiqing@waqu.com"

from urllib import quote
from hashlib import md5
from requests import request
from urllib import urlencode
from json import loads
from time import time

KEY = "fbeh5player12c43eccf2bec3300344"

HEAD_DERVICE = "firefox45.0"


def getSign(uu, vu, ran, cf="html5", bver=HEAD_DERVICE):
    # http://yuntv.letv.com/player/vod/bcloud.js :: ['cf' + d.cf, 'ran' + d.ran, 'uu' + d.uu, 'bver' + d.bver, 'vu' + d.vu]
    assert cf in ("ipad", "iphone", "html5_ios", "html5")
    text = "".join(["cf", cf, "ran", str(int(ran)), "uu", uu, "bver", quote(bver), "vu", vu])
    md = md5()
    md.update(text + KEY)
    return md.hexdigest()


def getYunLetvJsonData(pu, vu, uu):  # pu, vu, uu
    flv_address = "http://yuntv.letv.com/bcloud.html?uu=%s&vu=%s&pu=%s" % (uu, vu, pu,)
    # TODO 返回值内URL需要使用base64解码字符
    t = int(time())
    api_address = "http://api.letvcloud.com/gpc.php?"
    heads = {
        "Host": "api.letvcloud.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 %s" % HEAD_DERVICE,
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": flv_address,
        "Connection": "keep-alive",
    }
    sign = getSign(vu=vu, uu=uu, ran=t)
    web_form = {
        'ver': '2.1',
        'format': 'jsonp',
        'ran': t,
        'bver': HEAD_DERVICE,
        'pu': pu,
        'cf': 'html5',
        'sign': sign,
        'uu': uu,
        'pver': 'H5_Vod_20160317_4.1.9',
        'playid': '0',
        'vu': vu,
        'pf': 'html5',
        'callback': 'letvcloud%s0987' % t,
        'spf': '0',
        'page_url': flv_address,
    }

    cookie = {}  # {"Cookie": "JSESSIONID=03FB635359D22B419408E609BD7FC0B9"}
    # TODO 至关重要的一个请求
    request(method="GET", url="http://www.le.com/crossdomain.xml")
    request(method="GET", url="http://www.le.com/cmsdata/playerapi/lecloud_20160307_pccs.xml?tn=%s" % t)
    request(method="GET", url="http://api.letvcloud.com/crossdomain.xml")
    api_url = api_address + urlencode(web_form)
    response = request(method="GET", url=api_url, headers=heads, cookies=cookie).content
    info = response[24:-1]
    return loads(info)


if __name__ == '__main__':
    pu = "062d6f3659"
    vu = "f9a560f25a"
    uu = "69ddc93cfa"
    print getYunLetvJsonData(pu=pu, vu=vu, uu=uu)
