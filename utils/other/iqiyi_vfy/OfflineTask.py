# coding=utf-8
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')
from selenium import webdriver
from time import localtime, strftime, sleep
from traceback import print_exc


def run(username, password):
    driver.delete_all_cookies()
    driver.get("http://passport.iqiyi.com")
    sleep(1)
    user_box, password_box = driver.find_elements_by_class_name("text0")
    submit = driver.find_element_by_class_name("bindBlock")

    user_box.send_keys(username)
    password_box.send_keys(password)
    sleep(0.5)
    submit.click()
    submit.click()

    sleep(4)

    if correct_url not in driver.current_url:
        raw_input()

    if correct_url in driver.current_url:
        with open("%s@iqiyi.txt" % username, "w") as ck_file:
            ck_file.write("#LWP-Cookies-2.0\n")
            for cookie in driver.get_cookies():
                s = 'Set-Cookie3: %s="%s"; path="%s"; domain="%s"; path_spec; expires="%s"; version=0' % \
                    (cookie["name"], cookie["value"], cookie["path"], cookie["domain"],
                     strftime("%Y-%m-%d %H:%M:%SZ", localtime(cookie["expiry"])))
                ck_file.write(s + "\n")
        return True
    return False


def get_account():
    with open(FILE) as f:
        return [a.replace("\n", "").split(",", 1) for a in f.readlines()]


if __name__ == '__main__':
    FILE = "iqiyi.txt"
    correct_url = "accountset"
    accounts = get_account()
    driver = webdriver.Firefox()
    driver.get("http://www.baidu.com")
    driver.set_page_load_timeout(5)
    count = len(accounts)
    end = []
    end_count = 0
    fail = []
    fail_count = 0
    index = 0
    print accounts
    try:
        for index, (username, password) in enumerate(accounts):
            index = index + 1
            print "running: username:%s" % (username)
            try:
                if not os.path.exists("%s@iqiyi.txt" % username):
                    result = run(username, password)
                    if result:
                        end.append(username)
                        end_count += 1
                    else:
                        assert False
            except:
                print_exc()
                print "[Error] username:%s,password:%s" % (username, password)
                fail.append(username)
                fail_count += 1
                print "task: %s" % (count - index)

    except:
        print_exc()
        print "[Error] username:%s,password:%s" % (username, password)
        fail.append(username)
        fail_count += 1
        print u"剩余的任务数: %s" % (count - index)

    finally:
        print end
        print accounts[index:]
        print fail
        from json import dumps

        with open("residual tasks", "w") as f:
            f.write(dumps(accounts[index:]))

        print "over."
        driver.close()
    raw_input(u"任意键退出")
