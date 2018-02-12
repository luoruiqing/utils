# coding:utf-8
from time import strptime, mktime, time as _now
from datetime import datetime as _datetime, date, timedelta
from re import compile, _pattern_type as RegexType
from types import StringTypes, IntType, FloatType, LongType, NoneType
from dateutil import parser  # 任意时间字符串转换为时间对象 非常强大
from croniter import croniter  # 根据crontab的定时规则计算真正触发时间

DateType = (type(date), type(date(1970, 1, 1)))  # 所有日期类型
DatetimeType = (type(_datetime), type(_datetime.now()))  # 所有日期时间类型
NumberType = (IntType, FloatType, LongType)  # 所有数字类型
TimedeltaType = type(timedelta())  # 时间相减后的差值对象

DEFAULT_FORMATTER = "%Y-%m-%d %H:%M:%S"  # 普通时间格式转换

PICOSECOND = 0.000000000001  # 皮秒
NANOSECOND = PICOSECOND * 1000  # 纳秒
MICROSECOND = NANOSECOND * 1000  # 微秒
MILLISECOND = MICROSECOND * 1000  # 毫秒
SECOND = MILLISECOND * 1000  # 秒 这里秒作为基础单位
MINUTE = SECOND * 60  # 分
HOUR = MINUTE * 60  # 时
DAY = HOUR * 24  # 天
YESTERDAY = DAY * 2  # 昨天
BEFORE_DAY = DAY * 3  # 前天
WEEK = DAY * 7  # 星期
MONTH = DAY * 30  # 月
YEAR = DAY * 365  # 年
CENTURY = YEAR * 100  # 世纪/百年

STYLES = [
    ("%Y-%m-%d", strptime),
    ("%Y/%m/%d", strptime),
    ("%Y年%m月%d日", strptime),
    ("%Y-%m-%d %H:%M:%S", strptime),
    ("%Y/%m/%d %H:%M:%S", strptime),
    ("%Y年%m月%d日 %H点%M分%S秒", strptime),
    ("%Y-%m-%dT%H:%M:%SZ", strptime),
    (compile(r'刚刚'), lambda *args: _now()),
    (compile('(\d+)\s*分钟前'), lambda *args: _now() - int(args[0]) * MINUTE),
    (compile('(\d+)\s*小时前'), lambda *args: _now() - int(args[0]) * HOUR),
    (compile('昨天'), lambda *args: _now() - DAY),
    (compile('前天'), lambda *args: _now() - YESTERDAY),
    (compile('(\d+)\s*天前'), lambda *args: _now() - int(args[0]) * DAY),
    (compile('(\d+)\s*周前'), lambda *args: _now() - int(args[0]) * WEEK),
    (compile('(\d+)\s*(?:个|)月前'), lambda *args: _now() - int(args[0]) * MONTH),
    (compile('(\d+)\s*年前'), lambda *args: _now() - int(args[0]) * YEAR),
    (compile('(\d+)\s*月(?:份|)'), lambda *args: replace_time(month=int(args[0]))),
    (compile('(\d+)\s*(?:日|号)'), lambda *args: replace_time(day=int(args[0]))),

]


def remove_microsecond(object):
    ''' 将时间转换为不带毫秒的形式 '''
    if isinstance(object, datetime):  # 普通时间对象
        return object.replace(microsecond=0)
    if isinstance(object, TimedeltaType):  # 时间计算对象
        return timedelta(seconds=int(object.total_seconds()))  # 取整
    raise Exception('时间对象去除毫秒数据的转换不支持!')


def timestamp(datetime_object=None, **kwargs):
    """ 获得一个时间戳 
    >>> from time import time
    >>> int(timestamp()) == int(time())
    True
    """
    return mktime(datetime(datetime_object, **kwargs).timetuple())


def datetime(object=None, year=None, month=None, day=None, hour=None, minute=None, second=None,
             millisecond=None, microsecond=None, format=DEFAULT_FORMATTER):
    """ 获得时间对象 默认使用当前时间 可以是<datetime对象>、<date对象>和<时间戳> 
    >>> from time import time
    >>> from datetime import datetime as _dt, date
    
    >>> timestamp(datetime()) == int(time())
    True
    >>> isinstance(datetime(_dt.now()), DatetimeType)
    True
    >>> datetime(date(1995,02,06))
    datetime.date(1995, 2, 6)
    >>> print format_time(datetime(year=1995, month=02, day=06), format="%Y-%m-%d")
    1995-02-06
    >>> now = _dt.now()
    >>> format_time(datetime(None, now.year, now.month, now.day, now.hour, now.minute, now.second)) == format_time(time())
    True
    >>> format_time(datetime(time())) == format_time(_datetime.fromtimestamp(time()))
    True
    """
    dt_obj, now = None, _datetime.now()
    if isinstance(object, (DatetimeType, DateType)):
        return object
    elif isinstance(object, StringTypes):
        dt_obj = _datetime.strptime(object, format)
    elif isinstance(object, NumberType):
        dt_obj = _datetime.fromtimestamp(object)
    elif any([year, month, day, hour, minute, second, millisecond, microsecond]):
        if isinstance(microsecond, NoneType) and not isinstance(millisecond, NoneType):
            microsecond = (millisecond * 1000.0)
        dt_obj = _datetime(year=year or now.year,
                           month=month or now.month,
                           day=day or now.day,
                           hour=hour or now.hour,
                           minute=minute or now.minute,
                           second=second or now.second,
                           microsecond=int(microsecond or now.microsecond))
    return dt_obj or now


def format_time(object=None, format=DEFAULT_FORMATTER, **kwargs):
    """ 时间戳转字符 默认格式: %Y-%m-%d %H:%M:%S """
    format = kwargs.pop("format", format)
    return datetime(object, **kwargs).strftime(format)


def get_timestamp(string, default=None):
    """根据时间日期字符获得时间戳
    get_timestamp('刚刚') >>> _now()
    >>> from time import time
    >>> int(get_timestamp('刚刚')) == int(time())
    True
    """
    string = string.strip()
    for style, func in STYLES:
        if isinstance(style, StringTypes):
            try:
                return mktime(func(string, style))
            except ValueError:
                pass
        elif isinstance(style, RegexType):
            r = style.search(string)
            if r:
                return func(*r.groups())
    if isinstance(default, NoneType):
        raise ValueError("Conversion failed, please expand the formats list.")
    return default


def offset_time(object=None, year=0, month=0, day=0, hour=0, minute=0, second=0,
                millisecond=0, microsecond=0, weeks=0):
    """ 偏移时间 负数左偏移 正数右偏移 0不偏移 默认使用当前时间 """
    _timestamp = timestamp(object)
    offset = (year * YEAR) + (month * MONTH) + (day * DAY) + (hour * HOUR) + (minute * MINUTE) + (
        second * SECOND) + (millisecond * MILLISECOND) + (microsecond * MICROSECOND) + (weeks * WEEK)
    return _timestamp + offset


def replace_time(dt=None, year=None, month=None, day=None,
                 hour=None, minute=None, second=None, microsecond=None):
    """ 替换时间  默认使用当前时间 可以是<datetime对象>、<date对象>和<时间戳> 不支持星期，替换星期没意义 替换值必须是存在日期 
    # >>> a,b = replace_time(), datetime()
    # >>> print a,b
    # >>> replace_time()
    # >>> replace_time()
    # >>> replace_time()
    # >>> replace_time()
    # >>> replace_time()
    # >>> replace_time()
    # >>> replace_time()
    # >>> replace_time()
    """
    datetime_obj = datetime(dt, year, month, day, hour, minute, second, microsecond)
    kwargs = dict(year=year, month=month, day=day, hour=hour, minute=minute, second=second, microsecond=microsecond)
    kwargs = dict((k, v) for k, v in kwargs.items() if v)  # 过滤空参数
    return mktime(datetime_obj.replace(**kwargs).timetuple())


WEEK_NUMBER_CN = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 0: "日"}
WEEK_CN_NUMBER = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "日": 0}


def get_week(*args, **kwargs):
    """ 获得当前或指定日期的星期数 """
    return int(datetime(*args, **kwargs).strftime("%w"))


def convert_second(second):
    """
    :param second: 秒数
    :return: 小于1天时返回根据秒数获得的时分秒
    """
    _second = int(abs(second))
    minute, second = divmod(_second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    if day:
        return "more than %s days" % day
    return "%s%02d:%02d" % ("%02d:" % hour if hour > 0 else "", minute, second)


def get_utc_time(timestamp):
    # UTC时间 暂时没想法也没遇到这样的工作
    pass


ftm = format_time
del get_utc_time

""" 这种赋值会有延时的 a 和 b 是差距1秒的
from time import sleep, time as now
a, _, b = now(), sleep(1), now()
print a, b
"""
if __name__ == '__main__':
    from doctest import testmod

    testmod()
    print "1888年的今天：", datetime(year=1888)
    print "我要获得3月份的时间戳：", format_time(get_timestamp("3月份"))
    print "我要获得向前偏移1星期的日期：", format_time(offset_time(weeks=-1))
    print "向前偏移1天：", format_time(offset_time(day=-1))
    print "我要本月3号的日期：", format_time(replace_time(day=3))
    print "我要获得当前是周几：", get_week()
    print "我要获得本月3号是周几：", get_week(replace_time(day=3))
    print '"我昨天看电影了",昨天几号?', format_time(get_timestamp("我昨天看电影了"))
    print "下载剩余:%s" % convert_second(3600 * 21 + 3765)
