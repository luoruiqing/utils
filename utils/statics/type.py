# coding:utf-8
from decimal import Decimal
from datetime import date, datetime
from re import _pattern_type as RegexType  # 正则类型
from collections import Iterable as IterType  # 迭代类型
from types import IntType, FloatType, LongType, UnicodeType

# 日期类型
DateType = (type(date), type(date(1970, 1, 1)))
# 日期时间类型
DatetimeType = (type(datetime), type(datetime.now()))
# 数值类型
NumberType = (IntType, FloatType, LongType)
# 浮点运算类型
DecimalType = type(Decimal)
