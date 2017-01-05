from hashlib import md5


def get_md5(src):
    return md5(src).hexdigest().upper()
