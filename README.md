# fileStorage
showlib local file storage function

## 需求

源于文件整理，将磁盘中的文件进行去重，达到节省空间的效果。不考率网络传输的事情。
### 细分项
* 文件夹历史和快照
* 取重和恢复


## 原则

本项目希望能够贯彻`实现优先`的原则,杜绝以往想东想西，想的挺美，发现实现不了了的问题。先实现，再优化。

## 详细设计

### 操作历史
* 动作，起始时间，结束时间  .showlib/infos/logs/yyyymmddhhmmss.log or sqlite
### 快照
* 扫描保存原始文件夹快照，.showlib/infos/snapshot/oss_yyyymmddhhmmss.xml
* 去重快照，.showlib/infos/snapshot/rss_yyyymmddhhmmss.xml
### 去重

* 将重复hash的首个文件，移动到.showlib/objects/ 以hash命名
* 在原文件位置处创建size=0 ，name=原文件名.rd_backup
* 进行去重操作快照

### 相似

* hash相同
* 文件名相同
* 4k分片hash，有大量分片hash相同
* 大小相同
