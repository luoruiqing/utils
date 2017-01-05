# coding:utf-8
from math import ceil


class Pager:
    """
    分页器: print Pager().page_list >>> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    """

    def __init__(self, page=1, total=None, start=0, limit=20, list_limit=20, strict=False):
        _page = (page if page > 0 else 1) - 1  # 当前页数
        total = limit if total is None else total  # 总页数
        self.max_page = int(ceil(float(total) / limit))  # 最大页数

        self._page = _page if _page <= self.max_page else self.max_page
        self._start = start
        self._limit = limit
        self.list_limit = list_limit  # 需要的分页个数
        self.strict = strict  # 该值为True且total为None page_list返回值只是[1]

    @property
    def start(self):  # 开始于多少条
        return self._page * self._limit

    @property
    def end(self):  # 本页结束于多少条
        return self.start + self._limit

    @property
    def limit(self):  # 每页多少条
        return self._limit

    @property
    def prev_page(self):  # 上一页页码
        r = self._page
        if r <= 0:
            r = 1
        return r

    @property
    def page(self):  # 当前页页码
        return self._page + 1

    @property
    def next_page(self):  # 下一页页码
        r = self._page + 2
        if r > self.max_page:
            r = self.max_page
        return r

    @property
    def page_list(self):  # 页码列表
        result = []
        paging_diff = self.list_limit / 2  # 分页左或右的半段距离
        start = self._page - paging_diff + 2  # 左半段偏移
        stop = self._page + paging_diff + 2  # 右边段偏移
        for x in xrange(start, stop):
            if 0 < x <= self.max_page:  # 不加入小于零页和大于最大页面的页码
                result.append(x)
        diff = self.list_limit - len(result)  # 页码不足要求个数的差距值
        # 补差
        if result[0] == 1:  # 第一个页码是1
            paging_max = result[-1] + 1  # 分页中最大的数字 + 1
            diff_paging = range(paging_max, paging_max + diff)
            if self.strict:
                diff_paging = filter(lambda p: p <= self.max_page, diff_paging)
            result = result + diff_paging  # 末尾追加差值
        elif result[-1] == self.max_page:  # 最后一个页码是最大值
            paging_min = result[0]  # 页码范围内最小的数字
            diff_paging = range(paging_min - diff, paging_min)
            result = filter(lambda p: p > 0, diff_paging) + result  # 头部追加差值
        return result

    def get_page_list(self, list_limit=None, strict=True):
        self.list_limit = list_limit if list_limit else self.list_limit
        temp, self.strict = self.strict, strict
        r = self.page_list
        self.strict = temp
        return r


if __name__ == '__main__':
    print Pager(strict=True).page_list
    print Pager().page_list
