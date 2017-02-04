from dis import dis


def test():
    x = 1
    if x < 3:
        return "yes"
    else:
        return "no"


if __name__ == '__main__':
    dis(test)
