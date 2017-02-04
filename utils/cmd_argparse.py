# coding:utf-8
from __future__ import unicode_literals
from argparse import ArgumentParser
from sys import argv

"""
type:
    支持任何字符串转其他对象的类
action:
    action="count" 获得这个参数出现的次数 例如 -vvvv parser.parse_args().v  -> 4
nargs:
    ?一个参数 + 至少一个 *有或没有
"""
parser = ArgumentParser(
    description="软件介绍，尽量写的详细一些！",
    epilog="这里是结尾信息:)",
    # prog="程序的名字，这个一般不填写"
)

# <位置参数> 添加顺序有区别 不带- 位置参数
parser.add_argument("x", help="第一个位置参数", type=str)  # 加default没有意义
parser.add_argument("y", help="第二个位置参数", type=str)
# <可选参数>
parser.add_argument("-e", "--echo1", help="输入范围和默认类型", type=float, choices=[-1, 0, 1.0], default=0.0)
parser.add_argument("-t", "--test", help="是否出现这个参数", action="store_true")  # action="store_true" 只要出现这个参数即是真
# <分组参数>
group = parser.add_mutually_exclusive_group()
group.add_argument("-o1", "--option1", help="只使用选项一", action="store_true")
group.add_argument("-o2", "--option2", help="只使用选项二", action="store_true")
# <多个参数>
parser.add_argument("-n", "--num", help="多个参数", nargs="+", type=int)
# 指定变量名
parser.add_argument("-abc", "--aabbcc112233", help="指定变量名", dest="var", type=int)  # print args.var
# 获得参数
args = parser.parse_args(argv[1:])  # 不填默认是 argv[1:]
