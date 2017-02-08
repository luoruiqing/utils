# coding:utf-8
from math import ceil


class Pager:
    """
    分页器: print Pager().page_list >>> [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    """

    def __init__(self, page=1, total=None, start=0, limit=20, list_limit=20, strict=False):
        self.total = limit if total is None else total  # 总条数 认为至少一页
        _page = (page if page > 0 else 1) - 1  # 当前页数
        self.max_page = int(ceil(float(self.total) / limit))  # 最大页数
        self._page = _page if _page < self.max_page else self.max_page - 1
        self._start = start
        self._limit = limit
        self.list_limit = list_limit  # 页码合集限制

    @property
    def is_pages(self):
        """ 是否可以分页 """
        if self.max_page != 1:
            return True
        return False

    @property
    def start(self):
        """开始于多少条"""
        return self._page * self._limit

    @property
    def end(self):
        """本页结束于多少条"""
        return self.start + self._limit

    @property
    def limit(self):
        """每页多少条"""
        return self._limit

    @property
    def is_first(self):
        """是否是第一页"""
        if self.page == 1:
            return True
        return False

    @property
    def first(self):
        """首页"""
        return 1

    @property
    def previous(self):
        """上一页"""
        r = self._page
        if r <= 0:
            r = 1
        return r

    prev = previous

    @property
    def page(self):
        """当前页"""
        return self._page + 1

    @property
    def next(self):
        """下一页"""
        r = self._page + 2
        if r > self.max_page:
            r = self.max_page
        return r

    @property
    def last(self):
        """最后一页"""
        return self.max_page

    @property
    def is_last(self):
        """是否是最后一页"""
        if self.page == self.last:
            return True
        return False

    @property
    def page_list(self):
        """页码列表"""
        result = []
        paging_diff, odd = divmod(self.list_limit, 2)  # 分页左或右的半段距离
        start = self._page - paging_diff + (1 if odd else 2)  # 左半段偏移 # 如果要求奇数列表 左边多偏移一个量
        stop = self._page + paging_diff + 2  # 右边段偏移 多1个是range的原因
        for x in xrange(start, stop):
            if 0 < x <= self.max_page:  # 不加入小于零页和大于最大页面的页码
                result.append(x)
        diff = self.list_limit - len(result)  # 页码不足要求个数的差距值
        # 补差
        if result[0] == 1:  # 第一个页码是1
            paging_max = result[-1] + 1  # 分页中最大的数字 + 1
            diff_paging = range(paging_max, paging_max + diff)
            diff_paging = filter(lambda p: p <= self.max_page, diff_paging)
            result = result + diff_paging  # 末尾追加差值
        elif result[-1] == self.max_page:  # 最后一个页码是最大值
            paging_min = result[0]  # 页码范围内最小的数字
            diff_paging = range(paging_min - diff, paging_min)
            result = filter(lambda p: p > 0, diff_paging) + result  # 头部追加差值
        return result


if __name__ == '__main__':
    # print Pager(page=15, list_limit=10, total=3000).page_list
    p = Pager(page=10000, list_limit=10, total=300)
    print "是否可以分页", p.is_pages  # True
    print "当前页", p.page  # 15
    print "上一页", p.prev  # 14
    print "下一页", p.next  # 15
    print "首页", p.first  # 1
    print "末页", p.last  # 15
    print "是否是第一页", p.is_first  # False
    print "是否是最后一页", p.is_last  # True
    print "从多少条开始", p.start  # 280
    print "从多少条结束", p.end  # 300
    print "共有多少条", p.total  # 300
    print "共有多少页/最大页数", p.max_page  # 15
    print "一页多少条", p.limit  # 20
    print "需多少个分页", p.list_limit  # 10
    print "分页后页码列表", p.page_list  # [6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
