# coding:utf-8
from setuptools import setup, find_packages

requirements = [
    "sh", # 贼好用的库
    "requests",  # HTTP库
    "paramiko",  # SSH登陆
    "tornado",  # web框架
    "jieba",  # 分词
    "chardet",  # 检测字符串编码
    "pika",  # 队列
    "curl_httpclient",  # tornado 异步请求代理实现
    "user_agent",  # HTTP 随机头
]
setup(
    name="utils",
    version="0.1",
    description="",
    author="luoruiqing",
    url="http://www.waqu.com",
    license="LGPL",
    install_requires=requirements,
    packages=find_packages(),
    # scripts=["scripts/test.py"],
)
