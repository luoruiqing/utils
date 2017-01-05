# coding=utf-8
import sys
import os

reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, os.path.split(os.path.dirname(__file__))[0])
print sys.path
from Queue import Queue, Empty
from threading import Thread
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from time import localtime, strftime, sleep
from traceback import print_exc
from PIL import Image
from tools import decode_img
from damatu import DamatuApi
from itertools import count


def get_account(self):
    self.accounts = self.get_account()
    with open(self.file) as f:
        return [a.replace("\n", "").split(",", 1) for a in f.readlines()]


dmt = DamatuApi("wwwqqqwq", "1111111")
print "打码兔余额", dmt.getBalance()


class IQIYI_Cookies:
    def __init__(self, browser, queue):
        self.queue = queue
        self.browser = browser
        self.login_url = "http://passport.iqiyi.com"
        self.success_url = "http://www.iqiyi.com/u/accountset"

    def login(self, username, password):
        try:
            self.browser.get(self.login_url)
        except TimeoutException:
            return False
        user_box, password_box = self.browser.find_elements_by_class_name("text0")
        submit = self.browser.find_element_by_class_name("bindBlock")
        user_box.send_keys(username)
        password_box.send_keys(password)
        submit.click()
        submit.click()
        sleep(2)
        if self.verify():
            return True
        for i in range(2):
            print "请求验证码,第%s次。" % (i + 1),
            img = self.browser.find_elements_by_class_name("free-msg-img")
            if img:
                img = img[0]
                savepath = r'verify_imgs/%s.png' % username
                size = img.size
                location = img.location
                self.browser.save_screenshot(savepath)
                im = Image.open(savepath)
                left, top = location['x'], location['y']
                right = left + size['width']
                bottom = location['y'] + size['height']
                im = im.crop((left, top, right, bottom))
                im.save(savepath)
                verify_result = dmt.decode(savepath, 200)
                print verify_result
                # verify_result = decode_img(savepath)
                verify_box = self.browser.find_elements_by_class_name("inputComm1")
                verify_box[0].send_keys(verify_result)
                submit.click()
                sleep(2)
                if self.verify():
                    print "验证码输入成功.",
                    return True
            else:
                print "无需验证码.",
                return True
        print "打码失败"
        return False

    @staticmethod
    def get_filename(username):
        return "cookies/%s@iqiyi.txt" % username

    def verify(self):
        if self.success_url in self.browser.current_url:
            return True
        elif "passport.iqiyi.com/apis/secure/secure_modify_pwd.action" in self.browser.current_url:
            return True
        return False

    def save_cookie(self, username):
        with open(self.get_filename(username), "w") as ck_file:
            ck_file.write("#LWP-Cookies-2.0\n")
            for cookie in self.browser.get_cookies():
                s = 'Set-Cookie3: %s="%s"; path="%s"; domain="%s"; path_spec; expires="%s"; version=0' % \
                    (cookie["name"], cookie["value"], cookie["path"], cookie["domain"],
                     strftime("%Y-%m-%d %H:%M:%SZ", localtime(cookie["expiry"])))
                ck_file.write(s + "\n")

    def __del__(self):
        self.browser.quit()

    def handler_cookies(self):
        while 1:
            try:
                data = self.queue.get(timeout=5)
            except Empty:
                return
            username = data["username"]
            password = data["password"]
            file_name = self.get_filename(username)
            print "处理账号是:%s\t%s" % (username, password),
            if os.path.exists(file_name):
                print "[已处理] 跳过"
                continue
            self.login(username=username, password=password)
            for ac in count(1):
                if self.verify():
                    break
                sleep(2)
            if "www.pps.tv" in self.browser.current_url:
                self.browser.get("http://www.iqiyi.com/u/accountset")
                print "PPS主页，跳转.",
            self.save_cookie(username=username)
            self.browser.delete_all_cookies()
            print "[成功添加]"


def start(file="iqiyi.txt", windows=10):  # windows 是窗口数
    accounts_queue = Queue()
    index = 0
    with open(file, "r") as f:
        for index, x in enumerate(f.readlines()):
            account = x.replace("\n", "").split(",", 1)
            accounts_queue.put({"username": account[0], "password": account[1]}, timeout=5)

    print "账号总量:%s,窗口/线程个数%s" % (index + 1, windows)
    tasks = []
    for key in range(windows):
        browser = webdriver.Firefox()  # Firefox Chrome Ie Edge Opera Safari Android

        browser.maximize_window()
        ic = IQIYI_Cookies(browser, accounts_queue)
        task = Thread(target=ic.handler_cookies)
        tasks.append(task)

        task.start()
        sleep(60)
    for t in tasks:
        t.join()


if __name__ == '__main__':
    start()
