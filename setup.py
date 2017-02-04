# coding:utf-8
from setuptools import setup, find_packages

requirements = [
    "mongolog",  # mongo的日志库 可选
    "sh",  # 贼好用的库 可选
    "requests",  # HTTP库
    "paramiko",  # SSH登陆
    "tornado",  # web框架
    "jieba",  # 分词 可选
    "chardet",  # 检测字符串编码 可选
    "pika",  # 队列 必选
    "curl_httpclient",  # tornado 异步请求代理实现 没实现
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
