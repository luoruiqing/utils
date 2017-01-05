# coding:utf-8
# 字节 _bit * 8 = 1Byte
_bit = 1

Byte = 1  # 1B
Kilobyte = 1024 * Byte  # 1KB
Megabyte = 1024 * Kilobyte  # 1MB
Gigabyte = 1024 * Megabyte  # 1GB
Terabyte = 1024 * Gigabyte  # 1TB

DISK_CAPACITY_DIC = {
    Byte: 'B',
    Kilobyte: 'KB',
    Megabyte: 'MB',
    Gigabyte: 'GB',
    Terabyte: 'TB',
}

DISK_CAPACITY_MAP = list(DISK_CAPACITY_DIC.items())


def get_filesize(length):
    """ 根据文件长度获得标准写法 """
    company_tuple = filter(lambda (a, _): length >= a, DISK_CAPACITY_MAP)[-1]
    return "%.2f%s" % (length / (company_tuple[0] or 1), company_tuple[1])
