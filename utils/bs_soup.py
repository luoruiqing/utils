# coding:utf-8
"""
 简单扩展BeautifulSoup,爬虫中经常会根据class和id去跑，通过这个方法能很简单的使用
 容错一些None的情况 例如.find().find().findAll() 都可以容错，直到结果为None
 递归深度 recursive=False  例如find("div") 只查找子级别 不查找孙级别及以下的

===================================笔记==========================================

    # 删除子dom
    dom = '<div class="crumbs">
            <a href="http://video.duowan.com">多玩视频</a>
            <i></i><a href="http://video.duowan.com/u/1434552658">虎牙视频</a>
            <i></i>提取字符串
           </div>'
    soup = BeautifulSoup(dom)
    [s.extract() for s in soup(['a','i'])] # 都删除 并且会提高效率
    BeautifulSoup(html, parseOnlyThese=SoupStrainer('a', href=True)) # 只加载A标签 并且符合条件的

    soup.prettify() -> 格式化html
    soup.decompose() 删除所有子节点，保留当前节点

=================================================================================


"""
from types import ListType
from functools import partial, wraps
from BeautifulSoup import BeautifulSoup, Tag, BeautifulStoneSoup

# Tag = partial(Tag, BeautifulStoneSoup(), '')
__str__ = lambda self: 'None'

# 用来兼容的Tag 例: (soup.find(*) or FTT()).findAll(*)
FaultToleranceTag = type('FaultToleranceTag', (Tag,), {'__str__': __str__, "__repr__": __str__})
FaultToleranceTag = partial(FaultToleranceTag, BeautifulStoneSoup(), '')

FTT = FaultToleranceTag


def fault_tolerance_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # TODO args[1] 可能遇到下标越界问题，遇到了修改吧
        if result is None and args[1] != 'attrMap':
            return FTT()
        if isinstance(result, ListType):
            setattr(result, 'links', links)
        return result

    return wrapper


def find_class(self, class_name, tag_name=True):
    return self.find(tag_name, {"class": class_name})


def findAll_class(self, class_name, tag_name=True):
    return self.findAll(tag_name, {"class": class_name})


@property
def links(self, removal=True):
    return set(a["href"] for a in self.findAll("a", {"href": True}))


@property
def texts(self):
    """ 列表的形式返回列表内所有BS/TAG对象的文本 soup.findAll().texts """
    return [soup.getText().strip() for soup in self]


BeautifulSoup.find = fault_tolerance_wrapper(BeautifulSoup.find)
BeautifulSoup.findAll = fault_tolerance_wrapper(BeautifulSoup.findAll)
if hasattr(BeautifulSoup, 'find_all'):
    BeautifulSoup.find_all = fault_tolerance_wrapper(BeautifulSoup.find_all)
BeautifulSoup.find_class = find_class
BeautifulSoup.findAll_class = findAll_class
BeautifulSoup.links = links

Tag.find = fault_tolerance_wrapper(Tag.find)
Tag.findAll = fault_tolerance_wrapper(Tag.findAll)
if hasattr(Tag, 'find_all'):
    Tag.find_all = fault_tolerance_wrapper(Tag.find_all)
Tag.find_class = find_class
Tag.findAll_class = findAll_class
Tag.links = links

if __name__ == '__main__':
    soup = BeautifulSoup(open("../front_end/html/test.html"))
    block_soup = soup.find_class("scroll-div")
    print type(soup)
    print type(block_soup)
    print block_soup
    print soup.find(None, {"class": "scroll-div"})
    print block_soup.links
    print soup.find_class("column-right fr").find_class('user').find('None').links
