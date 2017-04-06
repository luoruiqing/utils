# utils
==============================================================================
## 时间转换和偏移
```
    - print "我要获得3月份的时间戳", format_time(get_timestamp("3月份"))
    [2017-03-06 15:56:15]
    - print "我要获得向前偏移1星期的日期", format_time(offset_time(weeks=-1))
    [2017-01-30 15:56:15]
    - print "向前偏移1天", format_time(offset_time(day=-1))
    [2017-02-05 15:56:15]
    - print "我要本月3号的日期", format_time(replace_time(day=3))
    [2017-02-03 15:56:15]
    - print "我要获得当前是周几", get_week()
    [1]
    - print "我要获得本月3号是周几", get_week(replace_time(day=3))
    [5]
    - print '"我昨天看电影了",昨天几号?', format_time(get_timestamp("我昨天看电影了"))
    [2017-02-05 15:56:15]
    - print "下载剩余%s" % convert_second(3600 * 21 + 3765)
    [22:02:45]
```
## 分页器
```
    - print Pager(page=15, total=300).page_list
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

```
```
 各种小工具
```



#我的笔记
##-swiper
```
    Swiper(Swiper master)是目前应用较广泛的移动端网页触摸内容滑动js插件。
```