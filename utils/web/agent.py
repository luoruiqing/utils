# coding:utf-8
from user_agent.base import generate_user_agent

platform_map = ("win", "linux", "mac", 'android', "iphone")
browser_map = ('chrome', 'firefox', 'ie')


def get_platform_agent(platform=None, browser=None):
    if platform == "android":
        return "Mozilla/5.0 (Linux; U; Android 4.3; en-us; SM-N900T Build/JSS15J) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
    elif platform == "iphone":
        return "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13E238 Safari/601.1"
    return generate_user_agent(platform=platform, navigator=browser)


if __name__ == '__main__':
    print get_platform_agent(platform="win")
    print get_platform_agent(platform="linux")
    print get_platform_agent(platform="mac")
    print get_platform_agent(platform="android")
    print get_platform_agent(platform="iphone")
    print get_platform_agent(browser="chrome")
    print get_platform_agent(browser="firefox")
