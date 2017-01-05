# coding:utf-8


class Error(Exception):
    def __init__(self, code, default_message, data=None):
        self.code = code
        self.data = data
        self.default_message = default_message
        self.message = "%d - %s" % (code, default_message)
        if data:
            self.message += "\n[DATA]: %s" % str(data)
        super(Error, self).__init__(self.message)

    def __call__(self, msg=None, data=None, **kwargs):
        return Error(self.code, msg or self.default_message, data or self.data)


NORMAL = Error(0, "正常")

if __name__ == '__main__':
    def test():
        try:
            raise NORMAL
        except Error, e:
            try:
                raise NORMAL()
            except Exception:
                from traceback import print_exc
                print_exc()


    test()
