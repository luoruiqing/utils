# coding:utf-8
# 字节 _bit * 8 = 1Byte
_bit = 1

# 1B
Byte = 1
# 1KB
Kilobyte = 1024 * Byte
# 1MB
Megabyte = 1024 * Kilobyte
# 1GB
Gigabyte = 1024 * Megabyte
# 1TB
Terabyte = 1024 * Gigabyte

DISK_CAPACITY_DIC = {
    Byte: 'B',
    Kilobyte: 'KB',
    Megabyte: 'MB',
    Gigabyte: 'GB',
    Terabyte: 'TB',
}

DISK_CAPACITY_MAP = list(DISK_CAPACITY_DIC.items())
