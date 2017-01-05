# coding:utf-8
from re import compile, _pattern_type
from datetime import datetime as _datetime, date
from time import strptime, mktime, strftime, localtime, time as _now
from types import StringTypes, IntType, FloatType, LongType, NoneType

DateType = (type(date), type(date(1970, 1, 1)))
DatetimeType = (type(_datetime), type(_datetime.now()))
NumberType = (IntType, FloatType, LongType)

MICROSECOND = 0.000001  # 微秒
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

TimerError = type('TimerError', (Exception,), dict())


def format_time(timestamp, formatter="%Y-%m-%d %H:%M:%S"):
    """ 时间戳转字符 默认格式: %Y-%m-%d %H:%M:%S """
    return strftime(formatter, localtime(timestamp))


def datetime_object(datetime=None, year=None, month=None, day=None,
                    hours=None, minutes=None, seconds=None, microsecond=None):
    """ 获得时间对象 默认使用当前时间 可以是<datetime对象>、<date对象>和<时间戳> 不支持星期 """
    datetime_obj = None
    if isinstance(datetime, NumberType):
        datetime_obj = _datetime.fromtimestamp(datetime)
    elif datetime is None:
        datetime_obj = _datetime.now()
    if isinstance(datetime_obj, (DatetimeType, DateType)):
        return datetime_obj or datetime
    raise TimerError('Unable to convert to date time object.')


def get_timestamp(string, default=None):
    """根据时间日期字符获得时间戳
    get_timestamp('刚刚') >>> _now()
    """

    string = string.strip()
    for style, func in STYLES:
        if isinstance(style, StringTypes):
            try:
                return mktime(func(string, style))
            except ValueError:
                pass
        elif isinstance(style, _pattern_type):
            r = style.search(string)
            if r:
                return func(*r.groups())
    if isinstance(default, NoneType):
        raise ValueError("Conversion failed, please expand the formats list.")
    return default


def get_sec_from_duration(duration):
    tmp = duration.split(":")
    dur = 0
    for i in range(0, len(tmp)):
        dur = dur * 60 + int(tmp[i])
    return dur


def offset_time(timestamp=None, year=0, month=0, day=0, hours=0, minutes=0, seconds=0, milliseconds=0, weeks=0):
    """ 偏移时间 负数左偏移 正数右偏移 0不偏移 默认使用当前时间 """
    timestamp = (timestamp if isinstance(timestamp, NumberType) else _now())
    offset = (year * YEAR) + (month * MONTH) + (day * DAY) + (hours * HOUR) + (minutes * MINUTE) + (
        seconds * SECOND) + (milliseconds * MILLISECOND) + (weeks * WEEK)
    return timestamp + offset


def replace_time(datetime=None, year=None, month=None, day=None,
                 hours=None, minutes=None, seconds=None, microsecond=None):
    """ 替换时间  默认使用当前时间 可以是<datetime对象>、<date对象>和<时间戳> 不支持星期，替换星期没意义 替换值必须是存在日期 """
    datetime_obj = datetime_object(datetime, year, month, day, hours, minutes, seconds, microsecond)
    kwargs = dict(year=year, month=month, day=day, hour=hours, minute=minutes, second=seconds, microsecond=microsecond)
    kwargs = dict((k, v) for k, v in kwargs.items() if v)  # 过滤空参数
    return mktime(datetime_obj.replace(**kwargs).timetuple())


def get_week(*args, **kwargs):
    """ 获得当前或指定日期的星期数 """
    return datetime_object(*args, **kwargs).strftime("%w")


def convert_second(second):
    """
    :param second: 秒数
    :return: 小于1天时返回根据秒数获得的时分秒
    """
    _second = float(abs(second))
    hour, minute, second = 0, 0, 0
    minute = _second / MINUTE
    if minute >= 60:
        hour = minute / 60
        minute = minute % 60
    if hour >= 24:
        return "more days"
    hour, minute, second = map(int, [hour, minute, _second % MINUTE])
    return "%s%02d:%02d" % ("%02d:" % hour if hour > 0 else "", minute, second)


def get_utc_time(timestamp):
    # UTC时间 暂时没想法也没遇到这样的工作
    pass


del get_utc_time
if __name__ == '__main__':
    print "我要获得3月份的时间戳", format_time(get_timestamp("3月份"))
    print "我要获得向前偏移1星期的日期", format_time(offset_time(weeks=-1))
    print "向前偏移1天", format_time(offset_time(day=-1))
    print "我要本月3号的日志", format_time(replace_time(day=3))
    print "我要获得当前是周几", get_week()
    print "我要获得本月3号是周几", get_week(replace_time(day=3))
    print '"我昨天看电影了",昨天几号?', format_time(get_timestamp("我昨天看电影了"))
    print "下载剩余%s" % convert_second(3799)
