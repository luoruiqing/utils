"use strict";
// phantom 全局变量
var driver = require('webpage'), server = require('webserver').create(), system = require('system'), auth = "luoruiqing";
var agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36';
var port, defaultJsScript = "function () {return null}", defaultHeaders = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    //'Accept-Charset': 'UTF-8,*;q=0.5',
    //'Accept-Encoding': 'gzip, deflate', // 压缩格式会有一些问题，可能内部做了解压
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': agent
};
/* [page functions]
 destroyed(QObject*)
 destroyed()
 objectNameChanged(QString)
 deleteLater()
 initialized()
 loadStarted()
 loadFinished(QString)
 javaScriptAlertSent(QString)
 javaScriptConsoleMessageSent(QString)
 javaScriptErrorSent(QString,int,QString,QString)
 resourceRequested(QVariant,QObject*)
 resourceReceived(QVariant)
 resourceError(QVariant)
 resourceTimeout(QVariant)
 urlChanged(QString)
 navigationRequested(QString,QString,bool,bool)
 rawPageCreated(QObject*)
 closing(QObject*)
 repaintRequested(int,int,int,int)
 openUrl(QString,QVariant,QVariantMap)
 release()
 close()
 evaluateJavaScript(QString)
 render(QString,QVariantMap)
 render(QString)
 renderBase64(QByteArray)
 renderBase64()
 injectJs(QString)
 _appendScriptElement(QString)
 _getGenericCallback()
 _getFilePickerCallback()
 _getJsConfirmCallback()
 _getJsPromptCallback()
 _getJsInterruptCallback()
 _uploadFile(QString,QStringList)
 sendEvent(QString,QVariant,QVariant,QString,QVariant)
 sendEvent(QString,QVariant,QVariant,QString)
 sendEvent(QString,QVariant,QVariant)
 sendEvent(QString,QVariant)
 sendEvent(QString)
 setContent(QString,QString)
 getPage(QString)
 childFramesCount()
 childFramesName()
 switchToFrame(QString)
 switchToChildFrame(QString)
 switchToFrame(int)
 switchToChildFrame(int)
 switchToMainFrame()
 switchToParentFrame()
 switchToFocusedFrame()
 currentFrameName()
 setCookieJar(CookieJar*)
 setCookieJarFromQObject(QObject*)
 cookieJar()
 setCookies(QVariantList)
 cookies()
 addCookie(QVariantMap)
 deleteCookie(QString)
 clearCookies()
 canGoBack()
 goBack()
 canGoForward()
 goForward()
 go(int)
 reload()
 stop()
 stopJavaScript()
 clearMemoryCache()
 setProxy(QString)
 */

function copy(source) {
    var result = {};
    for (var key in source) {
        result[key] = typeof source[key] === 'object' ? deepCoyp(source[key]) : source[key];
    }
    return result;
}
function getSettings(data) {
    return {
        "url": encodeURI(data.url),
        render: data.render || false, // 是否渲染
        renderingTime: data.renderingTime || 0, //  渲染保留时间(毫秒)
        snapshot: data.snapshot || false, //是否截图,将在渲染后截图
        includeJs: data.includeJs || [], // 插入的JS文件的网络地址
        javaScript: data.javaScript || defaultJsScript, // 执行的JS脚本
        width: data.width || 1024,
        height: data.height || 768,
        cookies: data.cookies || {},
        headers: function () {
            var headersResult = copy(defaultHeaders);
            for (var item in data.headers) {
                headersResult[item] = data.headers[item]
            }
            return headersResult;
        }(),
        setCookies: function (page) {
            var cookies = data.cookies || {};
            for (var item in cookies) {
                page.addCookie({name: item, value: cookies[item], 'path': '/', domain: data.url.split("/")[2]});
            }
            return true;
        },
        pageSettings: {
            userAgent: data.userAgent || agent, // 浏览器标识
            loadImages: data.loadImages || false, // 是否在渲染时加载图片
            javascriptEnabled: data.javascriptEnabled || true, // 是否禁用JavaScript
            XSSAuditingEnabled: data.XSSAuditingEnabled || false,
            webSecurityEnabled: data.webSecurityEnabled || true,
            javascriptCanOpenWindows: data.javascriptCanOpenWindows || true, // 允许打开窗口
            javascriptCanCloseWindows: data.javascriptCanCloseWindows || true, // 允许关闭窗口
            localToRemoteUrlAccessEnabled: data.localToRemoteUrlAccessEnabled || false,
        }
    };
}


function Server(port) {
    var listening = server.listen(port, {"keepAlive": false}, function (request, response) {
        var discard = function () {
            response.write(JSON.stringify({"status": "false", "message": ""}));
            response.close();
        };
        if (request.method != "POST")  discard();
        var settings = getSettings(JSON.parse(request.post)); // 每次请求都创建新的page对象
        if (!settings.url) discard(); // 没有url 忽略

        // -------------------------------------------------------------------------------------

        var page = driver.create();
        page.clearCookies(); // 清除 COOKIES
        page.customHeaders = settings.headers;  // HTTP头
        page.settings = settings.pageSettings;
        page.viewportSize = {width: settings.width, height: settings.height};  // 窗口宽高
        settings.setCookies(page); // 请求前插入的COOKIES

        //page.settings.resourceTimeout = data.timeout; // FIXME 这个不确定

        console.debug("Requesting: " + settings.url);
        var start = new Date();
        page.open(settings.url, function (status) {
            for (var i = 0; i < settings.includeJs.length; i++) {
                console.debug("includeJs is " + settings.includeJs[i]);
                page.includeJs(settings.includeJs[i])
            }
            var scriptResult;
            if (settings.javaScript != defaultJsScript) {
                console.debug("Start run extra javascript...");
                scriptResult = page.evaluateJavaScript(settings.javaScript);
            }

            setTimeout(function () {
                if (settings.snapshot) {
                    console.debug("Screen snapshot capturing...");
                    page.render('test.jpeg', {format: 'jpeg', quality: '100'});
                }
                response.statusCode = 200;
                response.headers = {"Cache": "no-cache", "Content-Type": "application/json"};
                dir(page);
                response.write(JSON.stringify({
                    "url": page.url,
                    "title": page.title,
                    "status": status,
                    "scriptResult": scriptResult,
                    "time": new Date() - start,
                    "settings": settings,

                    //"objectName": page.objectName,
                    //"frameTitle": page.frameTitle,
                    "content": page.content,
                    //"frameContent": page.frameContent,
                    //"frameUrl": page.frameUrl,
                    "loading": page.loading,
                    "loadingProgress": page.loadingProgress,
                    "canGoBack": page.canGoBack,
                    "canGoForward": page.canGoForward,
                    //"plainText": page.plainText,
                    //"framePlainText": page.framePlainText,
                    "libraryPath": page.libraryPath,
                    //"offlineStoragePath": page.offlineStoragePath,
                    //"offlineStorageQuota": page.offlineStorageQuota,
                    "viewportSize": page.viewportSize,
                    "paperSize": page.paperSize,
                    "clipRect": page.clipRect,
                    "scrollPosition": page.scrollPosition,
                    "navigationLocked": page.navigationLocked,
                    "customHeaders": page.customHeaders,
                    //"zoomFactor": page.zoomFactor,
                    "cookies": page.cookies,
                    "windowName": page.windowName,
                    "pages": page.pages,
                    "pagesWindowName": page.pagesWindowName,
                    "ownsPages": page.ownsPages,
                    //"framesName": page.framesName,
                    //"frameName": page.frameName,
                    "framesCount": page.framesCount,
                    "focusedFrameName": page.focusedFrameName,
                    //"cookieJar": page.cookieJar
                }));
                response.close();
                page.close();
                console.debug("request " + settings.url + " done.")
            }, settings.renderingTime);
        });

    });
    if (!listening) {
        console.log("could not create web server listening on port " + port);
        phantom.exit();
    }
}


function dir(object) {
    for (var item in object) {
        console.log(item); //+ "\t" + object[item])
    }
}

if (system.args.length !== 2) {
    console.log('Usage: server.js <some port>');
    phantom.exit(1);
} else {
    port = system.args[1];
    Server(port);

}
