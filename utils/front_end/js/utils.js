// 删除左右俩边的空格
String.prototype.trim = function () {
    return this.replace(/(^\s*)|(\s*$)/g, "");
};
//删除左边的空格
String.prototype.ltrim = function () {
    return this.replace(/(^\s*)/g, "");
};
//删除右边的空格
String.prototype.rtrim = function () {
    return this.replace(/(\s*$)/g, "");
};
// 测试值是否在数组里
Array.prototype.indexOf = function (val) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] == val) return i;
    }
    return -1;
};
// 数组删除元素
Array.prototype.remove = function (val) {
    var index = this.indexOf(val);
    if (index > -1) {
        this.splice(index, 1);
    }
};
Array.prototype.unique = function () {
    var res = [];
    var json = {};
    for (var i = 0; i < this.length; i++) {
        if (!json[this[i]]) {
            res.push(this[i]);
            json[this[i]] = 1;
        }
    }
    return res;
};
// 深拷贝
function cloneObject(obj) {
    var str, newobj = obj.constructor === Array ? [] : {};
    if (typeof obj !== 'object') {
        return;
    } else if (window.JSON) {
        str = JSON.stringify(obj); //系列化对象
        newobj = JSON.parse(str); //还原
    } else {
        for (var i in obj) {
            newobj[i] = typeof obj[i] === 'object' ? cloneObject(obj[i]) : obj[i];
        }
    }
    return newobj;
}

// 获得数组中的第一个元素
function getOneByArray(array, key, value) { // 获得数组嵌套对象的中的一个对象
    for (var i = 0; i < array.length; i++) {
        if (array[i][key] == value) {
            return array[i]
        }
    }
}
// 原地更新对象，不改变对象的引用
function updateObject(old_object, new_object) {
    // 如果 val 被忽略
    for (var item in new_object) {
        if (typeof new_object[item] === "undefined") {
            // 删除属性
            delete old_object[item];
        }
        else {
            // 添加 或 修改
            old_object[item] = new_object[item];
        }
    }
    return old_object
}
// 原地清空对象，不改变对象的引用
function clearObject(object) {
    for (var item in object) {
        delete object[item];
    }
    return object
}
// 校验对象值
function checkJsonParams(object) {
    for (var item in object) {
        if (!object[item]) {
            return false
        }
    }
    return true
}
// 清除拖拉事件的默认方法
function clearDragover(JqObject) {
    JqObject.ondragover = function (event) {
        event.preventDefault();
        return true;
    };
    return JqObject
}
// Juqery序列化form表单为Json
(function ($) { // Jquery转JSON
    $.fn.serializeJson = function () {
        var serializeObj = {};
        $(this.serializeArray()).each(function () {
            serializeObj[this.name] = this.value;
        });
        return serializeObj;
    };
})(jQuery);

// 打印
log = console.log;


// 对象/数组打印
table = console.table;