# coding:utf-8
from sys import stdout
from time import sleep
from cProfile import run
from pstats import Stats

"""
    命令行的版本
    python -m cProfile -o log.txt XXX.py
    -o 选项是针对一些图形工具的 VPT（http://visualpytune.googlecode.com）
"""


def main():
    """
    # http://blog.csdn.net/gzlaiyonghao/article/details/1483728 这个解释更具体
------------------------------------------------------------------------------------------------
+             324 function calls in 0.695 seconds
+
+   Ordered by: standard name
+
+   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
+        1    0.000    0.000    0.695    0.695 <string>:1(<module>)
+        1    0.000    0.000    0.695    0.695 cprofile_dome.py:11(main)
+       20    0.001    0.000    0.695    0.035 cprofile_dome.py:12(b)
+        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
+        1    0.000    0.000    0.000    0.000 {range}
+      300    0.694    0.002    0.694    0.002 {time.sleep}
+
------------------------------------------------------------------------------------------------
    ncalls 函数的被调用次数
    tottime 函数总计运行时间，除去函数中调用的函数运行时间
    percall 函数运行一次的平均时间，等于tottime/ncalls
    cumtime 函数总计运行时间，含调用的函数运行时间
    percall 函数运行一次的平均时间，等于cumtime/ncalls
    filename:lineno(function) 函数所在的文件名，函数的行号，函数名

   """

    def b():
        pn = 0
        while pn < 15:
            pn += 1
            stdout.write(".")
            sleep(0.002)

    for _ in range(20):
        b()
    stdout.write("\n")


if __name__ == '__main__':
    logfile = 'cProfile.log'
    run("main()", logfile)
    info = Stats(logfile)
    info.strip_dirs().sort_stats(-1).print_stats()
    # strip_dirs():从所有模块名中去掉无关的路径信息
    # sort_stats():把打印信息按照标准的module/name/line字符串进行排序
    # print_stats():打印出所有分析信息
    # 按照函数名排序

    info.strip_dirs().sort_stats("name").print_stats()

    # 按照在一个函数中累积的运行时间进行排序

    # print_stats(3):只打印前3行函数的信息,参数还可为小数,表示前百分之几的函数信息

    info.strip_dirs().sort_stats("cumulative").print_stats(3)

    # 还有一种用法

    info.sort_stats('time', 'cum').print_stats(.5, 'foo')

    # 先按time排序,再按cumulative时间排序,然后打倒出前50%中含有函数信息



    # 如果想知道有哪些函数调用了bar,可使用

    info.print_callers(0.5, "bar")

    # 同理,查看foo()函数中调用了哪些函数

    info.print_callees("foo")
