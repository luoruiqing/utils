# coding:utf-8

import csv
from collections import OrderedDict


def install_patch():
    csv.DictWriter = DictManager


class DictManager:
    """ 按照指定顺序写入csv文件
    1. ->  DictManager(open("test.scv", "wb"), keys=OrderedDict([("id", "ID"),("url", "链接地址"),])
            ).writeheader().writerows([{},{},....])
    2. ->  DictManager(open("test.scv", "wb"),
                keys=["id", "flower", "url", "online"],
                headers=["ID", "其他", "直播地址", "在线人数"]
            ).writerows([{},{},....])
    """

    def __init__(self, file, keys, headers=(), dialect="excel", *args, **kwargs):
        self.keys, self.headers = keys, headers
        if isinstance(keys, OrderedDict):
            self.keys, self.headers = zip(*[(key, value) for key, value in keys.iteritems()])
        self.writer = csv.writer(file, dialect, *args, **kwargs)

    def writeheader(self, headers=()):
        return self.writer.writerow(headers or self.headers) or self

    def writerow(self, rowdict):
        return self.writer.writerow([rowdict[key] for key in self.keys]) or self

    def writerows(self, rowlist):
        return map(self.writerow, rowlist) or self


if __name__ == '__main__':
    result = {
        "2218262": {
            "flower": "90200",
            "url": "http://www.tuho.tv/2218262",
            "nick": "2030丶♚千♞足♚",
            "fans": "291粉丝",
            "intro": "不把我怼爽，你特么的滚远点。。。",
            "online": "1605人在看",
            "id": 2218262
        },
        "3016952": {
            "flower": "92750",
            "url": "http://www.tuho.tv/3016952",
            "nick": "✨自⭐己✨",
            "fans": "224粉丝",
            "intro": "陪你聊聊天，为你唱首歌，我的驿站等你来做客~",
            "online": "1602人在看",
            "id": 3016952
        },
        "4963215": {
            "flower": "104201",
            "url": "http://www.tuho.tv/4963215",
            "nick": "甜心小公主",
            "fans": "5011粉丝",
            "intro": "直播时间下午一点，晚上九点，风里雨里直播间等你😚",
            "online": "2373人在看",
            "id": 4963215
        },
        "6360024": {
            "flower": "63901",
            "url": "http://www.tuho.tv/6360024",
            "nick": "柠檬味的芋头",
            "fans": "287粉丝",
            "intro": "来看主播不后悔😘",
            "online": "1601人在看",
            "id": 6360024
        },
        "6792870": {
            "flower": "9400",
            "url": "http://www.tuho.tv/6792870",
            "nick": "a怀中猫",
            "fans": "607粉丝",
            "intro": "游泳馆",
            "online": "1264人在看",
            "id": 6792870
        },
        "6802918": {
            "flower": "8700",
            "url": "http://www.tuho.tv/6802918",
            "nick": "既然青春留不住(1105)",
            "fans": "326粉丝",
            "intro": "因为有了你们，人生才变的如此精彩！感谢你们的陪伴！么么哒",
            "online": "828人在看",
            "id": 6802918
        },
        "6982094": {
            "flower": "0",
            "url": "http://www.tuho.tv/6982094",
            "nick": "阿孜古丽苏姆",
            "fans": "0粉丝",
            "intro": "聊天可否",
            "online": "204人在看",
            "id": 6982094
        }
    }

    DictManager(open("test.scv", "wb"), keys=OrderedDict(
        [("id", "ID"), ("url", "链接地址"), ])
                ).writeheader().writerows(result.itervalues())
