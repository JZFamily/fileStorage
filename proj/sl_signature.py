import hashlib
import sqlite3
import os
import time
import logging
import datetime
import mmap
from sys import argv

'''
@author:jzf
@date: 2019-11-20
@desc: 签名模块
'''

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DBName = "Signature.db"
def TimeStampToTime(timestamp):
	timeStruct = time.localtime(timestamp)
	return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)

class SL_Signature:
    #签名类
    def __init__(self, rootdir, DBName = None):
        self.logger = logging.getLogger("Signature")
        fileHandler = logging.FileHandler(filename='Signature.log',encoding="utf-8")
        formatter = logging.Formatter(LOG_FORMAT)
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)
        self.logger.setLevel(logging.INFO)
        self.rootdir = rootdir
        if DBName is None:
            #DBName = os.path.basename(os.path.abspath(rootdir))
            #DBName += ".db"
            DBName = "Signature.db"
            DBName = os.path.abspath(rootdir)+os.sep+".showlib"+os.sep+ DBName
            self.DBName = DBName
            print(DBName)
        else:
            DBName = os.path.abspath(rootdir)+os.sep+".showlib"+os.sep+ DBName
            self.DBName = DBName
            print(DBName)
        self.conn = sqlite3.connect(DBName)
        self.cur = self.conn.cursor()
        self.cur.execute('''create table IF NOT EXISTS SignatureLib(
            name varchar(256) not null,
            hash varchar(256) not null,
            size decimal(19,2) not null,
            primary key(hash))
            ''')
        self.conn.commit()

    def __del__(self):
        print('close')
        self.conn.close()

    def GetFileHash(self, FileName):
        #获取FileName的hash值
        hs = hashlib.sha256()
        with open(FileName,'rb') as f:
            while True:
                block = f.read(4096)  
                if block:
                    hs.update(block)
                else:
                    break
        return hs.hexdigest()
    def GetFileHash_bymmap(self, FileName):
        #获取FileName的hash值
        hs = hashlib.sha256()
        with open(FileName,'rb') as f:
            mm = mmap.mmap(f.fileno(), 0,access=mmap.ACCESS_READ)
            while True:
                block = mm.read(4096)  
                if block:
                    hs.update(block)
                else:
                    break
            mm.close()
        return hs.hexdigest()
    def InsertToDB(self,record):
        #将记录插入到数据库
        try: 
            self.conn.execute('''insert into SignatureLib (name, hash, size) 
                values(?,?,?)''',tuple(record))
            self.conn.commit()
        except Exception as e:
            self.logger.warning("%s  name is %s" %(e,record[0]))
            self.cur.close()
            self.conn.close()
            self.conn = sqlite3.connect(self.DBName)
            self.cur = self.conn.cursor()
    def InsertDB_Records(self, records):
        try:
            self.cur.executemany('''insert into SignatureLib (name, hash, size) values(?,?,?)''',records)
            self.conn.commit()
        except Exception as e:
            self.logger.warning("%s len is %s" %(e,str(len(records))))
            self.cur.close()
            self.conn.close()
            self.conn = sqlite3.connect(self.DBName)
            self.cur = self.conn.cursor()
    def GetHashList(self) :
        hashlist = []
        for row in self.conn.execute('SELECT distinct hash FROM SignatureLib'):
            hashlist.append(row[0])
        self.conn.commit()
        return hashlist
    def GenRecord(self,root,name):
        #生成单条记录并插入到库
        record = []
        record.append(name)
        FileAbsPath = root+os.sep+name
        h = self.GetFileHash(FileAbsPath)
        record.append(h)
        record.append(os.path.getsize(FileAbsPath))
        #self.InsertToDB(record)
        return record
    def GetRecords(self):
        self.cur.execute(''' SELECT * FROM SignatureLib''')
        ls = self.cur.fetchall()
        self.conn.commit()
        return ls
    def GetFileName_byHash(self, hash):
        name = None
        for row in self.conn.execute(''' SELECT name FROM SignatureLib where hash = ? ''',hash):
            name = row[0]
        self.conn.commit()
        return name
    def GetRecord_byHash(self,hash):
        ls = []
        for row in self.conn.execute(''' SELECT name,hash,size FROM SignatureLib where hash = ? ''',hash):
            ls.append(row)
        self.conn.commit()
        return ls
    def TraversePathAndGenRecord(self,root_path = None):
        #编译路径，存库
        RootPath = os.path.abspath(self.rootdir)
        if root_path is not None:
            RootPath = os.path.abspath(self.root_path)
        logging.debug(RootPath)
        recordset = []
        for root, dirs, files in os.walk(RootPath) :
            print(root)
            if os.path.basename(root) == ".showlib":
                continue
            for name in files :
                if DBName ==  (root+os.sep+name):
                    continue
                print(name)
                self.GenRecord(root,name)
        return  recordset   

if __name__ == "__main__" :
    # 使用xx.py xxx路径
    old = datetime.datetime.now()
    print(old.strftime('%Y-%m-%d %H:%M:%S.%f'))

    f = SL_Signature(argv[1])
    f.TraversePathAndGenRecord()

    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
    print(datetime.datetime.now()-old)