# coding:utf-8
""" 任务调度 但是这个模块是阻塞的 适合多线程 多进程模型 """
from __future__ import print_function
from sched import scheduler as _scheduler
from time import time as now, sleep


def scheduler(func=lambda: print(now()), seconds=None, max_length=float("inf")):
    assert seconds
    sched = _scheduler(now, sleep)
    sched._n = 0

    def task(seconds):
        # 安排inc秒后再次运行自己，即周期运行
        if sched._n >= max_length: return
        func()
        sched._n += 1
        sched.enter(seconds, 0, task, (seconds,))

    sched.enter(seconds, 0, task, (seconds,))
    sched.run()


if __name__ == '__main__':
    scheduler(seconds=0.01, max_length=500)
