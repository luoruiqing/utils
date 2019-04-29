#!/usr/bin/env bash

# Webpack打包同时推送到服务器
ADDRESS=$(echo $1 | awk -F ':' '{print $1}')     # 目标服务器
TARGET_PATH=$(echo $1 | awk -F ':' '{print $2}') # 目标服务器路径
DATE=$(date +%Y-%m-%d_%H%M%S)                    # 增加打包时间, 不覆盖文件
function build() {
    cd $(dirname $0)                              # 脚本所在的目录
    VUE_PROJECT=$(pwd | awk -F '/' '{print $NF}') # 当前目录名称与远端名称相同
    npm run build                                 # 打包
    ssh $ADDRESS "mkdir -p $TARGET_PATH"
    zip -r $VUE_PROJECT\_$DATE.zip ./dist # 压缩本地文件
    scp $VUE_PROJECT.zip $1               # 推送到目标服务器
    # rm $VUE_PROJECT.zip # 删除本地包
    # 解包
    ssh $ADDRESS "cd $TARGET_PATH && unzip -o $VUE_PROJECT.zip "
}

build $1    # 执行

echo "Done" # 提示完成
