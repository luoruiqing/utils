/*
 所有扩展方法
 */
// 字符串 **************************************************************************************************

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

// 数组 **************************************************************************************************

// 获得元素在数组内的下标
Array.prototype.index = function (value) {
    for (let [index, item] of this.entries())
        if (item === value) return index;
    return -1;
};

// 数组删除元素
Array.prototype.remove = function (value) {
    let index = this.index(value);
    if (index > -1)
        this.splice(index, 1);
};
// 去重,changed 是否 改变引用/新建对象
Array.prototype.unique = function (changed = false) {
    let values = Array.from(new Set(this));
    if (!changed) {
        this.splice(0, this.length); // 清空本数组
        for (let item of values)
            this.push(item)
        return this
    }
    return values
};
// 清空数组
Array.prototype.clear = function () {
    this.splice(0, this.length);
};
// 过滤 键值对
Array.prototype.filterObject = function (key, value) {
    for (let object of this)
        if (object[key] === value)
            return object;
};
// 过滤 键值对
Array.prototype.filterObjects = function (key, value) {
    let result = [];
    for (let object of this)
        if (object[key] === value)
            result.push(object);
    return result
};

// 对象 **************************************************************************************************

// 浅拷贝
Object.copy = (object = {}) => {
    let new_object = {};
    Object.keys(object).forEach((key) => new_object[key] = object[key]);
    return new_object
};
// 深拷贝
Object.deepcopy = (object = {}) => JSON.parse(JSON.stringify(object));

// 原地更新对象，不改变对象的引用
Object.update = (object, new_object) => {
    Object.keys(new_object).forEach((key) => object[key] = new_object[key]);
    return object
};
// 原地清空对象，不改变对象的引用
Object.clear = (object) => {
    Object.keys(object).forEach((key) => delete obj[key]);
    return object
};


// 表单 **************************************************************************************************

// Juqery序列化form表单为Json
function installSerializeJson($ = JQuery) { // Jquery转JSON
    $.fn.serializeJson = function () {
        let serializeObj = {};
        $(this.serializeArray()).each(function () {
            serializeObj[this.name] = this.value;
        });
        return serializeObj;
    };
}
// 调试 **************************************************************************************************

// 打印
log = console.log;
table = console.table;
// 查看对象内部方法
dir = (object = {}) => {
    for (let [key, value] of object) console.log(key + ": \t" + value)
};
// 事件 **************************************************************************************************


// 其他 **************************************************************************************************

// 校验对象值
let test = {name: 1, age: 22};
for (let [key, value] of Object.entries(test))
    log(`${key} :\t\t\t\t\t${value}`);