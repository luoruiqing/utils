# coding=utf-8
from __future__ import unicode_literals

'''
command: # 浏览器API接口命令列表
    status, newSession, getAllSessions, deleteSession, close, quit, get, goBack, goForward, refresh, addCookie, getCookie, getCookies, deleteCookie, deleteAllCookies, findElement, findElements, findChildElement, findChildElements, clearElement, clickElement, sendKeysToElement, sendKeysToActiveElement, submitElement, uploadFile, getCurrentWindowHandle, getWindowHandles, getWindowSize, w3cGetWindowSize, getWindowPosition, setWindowSize, w3cSetWindowSize, setWindowPosition, switchToWindow, switchToFrame, switchToParentFrame, getActiveElement, getCurrentUrl, getPageSource, getTitle, executeScript, getElementText, getElementValue, getElementTagName, setElementSelected, isElementSelected, isElementEnabled, isElementDisplayed, getElementLocation, getElementLocationOnceScrolledIntoView, getElementSize, getElementRect, getElementAttribute, getElementValueOfCssProperty, elementEquals, screenshot, elementScreenshot, implicitlyWait, executeAsyncScript, setScriptTimeout, setTimeouts, windowMaximize, w3cMaximizeWindow, getLog, getAvailableLogTypes, dismissAlert, acceptAlert, setAlertValue, getAlertText, setAlertCredentials, mouseClick, mouseDoubleClick, mouseButtonDown, mouseButtonUp, mouseMoveTo, setScreenOrientation, getScreenOrientation, touchSingleTap, touchDown, touchUp, touchMove, touchScroll, touchDoubleTap, touchLongPress, touchFlick, executeSql, getLocation, setLocation, getAppCache, getAppCacheStatus, clearAppCache, getLocalStorageItem, removeLocalStorageItem, getLocalStorageKeys, setLocalStorageItem, clearLocalStorage, getLocalStorageSize, getSessionStorageItem, removeSessionStorageItem, getSessionStorageKeys, setSessionStorageItem, clearSessionStorage, getSessionStorageSize, getNetworkConnection, setNetworkConnection, getCurrentContextHandle, getContextHandles, switchToContext

WebDriver:
    # ====================== 设置/功能 ==========================

    name # 浏览器的名字
    start_client/stop_client # 启动/停止
    set_page_load_timeout # 设置页面加载超时
    implicitly_wait # 设置找不到元素等待超时，默认30秒
    maximize_window # 最大化窗口
    get_window_size/set_window_size # 获得/设置 窗口大小
    get_window_position/set_window_position # 获得/设置 窗口位置
    back/forward # 后退/前进(跳转上一页/跳转下一页)
    refresh # 刷新页面
    close # 关闭当前窗口
    quit # 关闭浏览器并退出驱动
    get # 请求网页

    # ======================== 标签 ============================

    current_window_handle # 当前标签页
    window_handles # 所有标签页

    # ======================== 属性 ============================

    current_url # 当前的url
    mobile # TODO 未知的属性
    page_source # 当前页面源码
    title # 当前网页标题

    # ======================== cookie =========================

    add_cookie # 代码添加cookie 要求字典
    get_cookie # 根据key获得一个cookie值
    get_cookies # 获得所有cookie
    delete_cookie # 根据key删除一个cookie
    delete_all_cookies # 删除所有cookie

    # ===================== javascript ========================

    execute_script # 执行一段JS脚本
    execute_async_script # 异步执行一段JS脚本
    set_script_timeout # 设置脚本超时

    # ========================= 截图 ===========================

    save_screenshot/get_screenshot_as_file # 截图并保存
    get_screenshot_as_png # 截图保存为png格式
    get_screenshot_as_base64 # 截图

    # ========================= 特殊 ===========================

    switch_to_active_element, switch_to_window, switch_to_frame, switch_to_default_content, switch_to_alert
    # 对应下面的 SwitchTo 对象

    # ========================= 选择器 ===========================

    find_element # 基础选择器，还包含WebElement的所有选择器
    create_web_element # 新建节点

    # ========================= 其他 ===========================


    file_detector # TODO 研究
    orientation # TODO
    application_cache # TODO
    log_types # todo
    get_log # todo
    start_session # TODO
    rect # TODO
    parent # TODO
    id # TODO
    # ========================= end =============================


WebElement:
    # ======================== 属性 ==============================
        tag_name # 标签名字
        text # 文字
        is_selected # 是否选中
        is_enabled # 是否可用
        is_displayed # 是否可见
        location # 元素的坐标
        size # 返回元素的大小

        get_attribute(name) # 根据属性名称获得节点的属性
        value_of_css_property # 获得CSS的属性值 例如宽高等

    # ======================== 选择器 ============================

        find_element_by_id # 选择ID
        find_element_by_class_name # 选择类名
        find_element_by_xpath # 根据xpath选择一个
        find_element_by_css_selector # CSS选择器
        find_element_by_tag_name # 根据标签/元素名称
        find_element_by_name # 选择name属性名称 // <input name="a"/>
        find_element_by_link_text # 根据链接的内容选择元素 // <button>登 陆</button> -> find_element_by_link_text("登 陆")
        find_element_by_partial_link_text # 根据链接的部分内容选择元素 // <button>贴吧<button>  -> find_element_by_partial_link_text("贴")

    # ======================== 事件 ============================
        click # 单击
        submit # 提交
        clear # 清除
        send_keys # 输入

    # ========================= 截图 ============================
        screenshot_as_base64 # 屏幕截图
        screenshot_as_png # 截图为png格式
        screenshot # 截图并保存到文件

    # ========================== end ==============================


SwitchTo:
    alert # 返回浏览器的Alert对象，可对浏览器alert/confirm/prompt框操作
    default_content() # 切到主文档
    frame # 切到那个框架
    parent_frame # 切到父frame
    window(window_name) # 切换到窗口 顺序问题 [1 2 3 4 5] [0 4 3 2 1]
    active_element # 返回当前焦点的WebElement对象
    # ========================== end ==============================

'''

''' 切换窗口代码
print "begin get the handles"
        winBeforeHandle = self.driver.current_window_handle
        print "winBeforeHandle==",winBeforeHandle

        winHandles = self.driver.window_handles
        print "winHandles==",winHandles


        for handle in winHandles:
            if winBeforeHandle != handle:
                self.driver.switch_to_window(handle)
                self.driver.close()
                break

'''

import sys

reload(sys)
sys.setdefaultencoding('utf-8')
from time import sleep
from functools import wraps
from logging import getLogger, DEBUG
from selenium.webdriver.common.keys import Keys  # 键盘
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Firefox, Chrome, PhantomJS
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains  # PC端操作
from selenium.webdriver.common.touch_actions import TouchActions  # 移动端操作

logger = getLogger()
logger.setLevel(DEBUG)


def retry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except NoSuchElementException:
                sleep(.5)

    return wrapper


# 增强方法
Chrome.__del__ = Chrome.quit  # 退出Chrome的时候关闭浏览器
WebElement.find_element = retry(WebElement.find_element)
Chrome.find_element = retry(Chrome.find_element)
