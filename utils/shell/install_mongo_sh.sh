#!/bin/bash
#mongodb一键安装脚本
clear
mongodb=mongodb-linux-x86_64-3.2.4.tgz
install_dir=/opt
softdir=/opt/soft

if [ ! -d $softdir ];
then mkdir /opt/soft
fi
# http://61.191.61.88/soft/mongodb-linux-x86_64-3.2.4.tgz
echo "下载软件包"
cd $softdir
wget http://61.191.61.88/soft/$mongodb

#安装mongodb
echo "安装mongodb"
cd $softdir
mkdir -p /data/logs/mongo/
mkdir -p /data/mongo_db
tar zxf $mongodb  && mv `echo $mongodb | awk -F".tgz" '{print $1}'` $install_dir/mongodb
ln -s $install_dir/mongodb/bin/* /usr/bin/

# --auth
echo "启动mongodb"
/opt/mongodb/bin/mongod --auth --dbpath=/data/mongo_db --fork --logpath=/data/logs/mongo.log --directoryperdb

echo "设置开机启动"
echo "$install_dir/mongodb/bin/mongod --dbpath=/data/mongo_db --fork --logpath=/data/logs/mongo.log --directoryperdb" >> /etc/rc.local

echo "mongodb 已经安装完毕，端口27017，安装目录 $install_dir/mongodb/"


