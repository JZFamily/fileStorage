import os
import time
import datetime
import xml.dom.minidom as XmlDocument
import json

class Dir_Object():
    def __init__(self):
        self.path = None
        self.name = None
        self.stat = None
        self.file_num = 0
        self.symlink_num = 0
        self.dirs = {}

def TimeStampToTime(timestamp):
	timeStruct = time.localtime(timestamp)
	return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)
class Sl_Snapshot():
    def __init__(self):
        self.root_dir = None
        pass
    def get_dir_object(self,dir_object):
        try:
            with os.scandir(dir_object.path) as it:
                for entry in it:
                    if entry.is_dir():
                        if entry.name == "System Volume Information" or "Recovery" == entry.name or "Config.Msi"  == entry.name or "$RECYCLE.BIN" == entry.name: 
                            print(entry.path)
                            continue
                        sub_dir = Dir_Object()
                        sub_dir.name = entry.name
                        sub_dir.path = entry.path
                        sub_dir.stat = entry.stat()
                        dir_object.dirs[entry.name] = sub_dir
                    elif entry.is_file():
                        dir_object.file_num += 1
                    elif entry.is_symlink():
                        dir_object.symlink_num += 1
                    else:
                        print(dir_object.name + " unknonw sub obj")
        except OSError as ex:
            print(dir_object.path + " ,errno ="+ str(ex.errno))

    def create_dir_object_tree(self,path):
        self.root_dir = Dir_Object()
        self.root_dir.path = path
        self.root_dir.name = os.path.basename(self.root_dir.path)
        self.root_dir.stat = os.stat(self.root_dir.path)
        l = []
        l.append(self.root_dir)
        while len(l) != 0:
            dir_object = l.pop(-1)
            self.get_dir_object(dir_object)
            for item in dir_object.dirs:
                l.append(dir_object.dirs[item])
    def gen_sub_xml_node(self, dir_object, parent_node, doc):
        sub_node = doc.createElement('subdir')
        parent_node.appendChild(sub_node)
        sub_node.attributes['name'] = dir_object.name
        sub_node.attributes['mtime'] = TimeStampToTime(dir_object.stat.st_mtime)
        #sub_node.attributes['ino'] = str(dir_object.stat.st_ino)
        #sub_node.attributes['dev'] = str(dir_object.stat.st_dev)
        sub_node.attributes['files'] = str(dir_object.file_num)
        sub_node.attributes['dirs'] = str(len(dir_object.dirs))
        return sub_node

    def gen_sub_xml_node_2(self, dir_object, parent_node, doc):
        sub_node = doc.createElement('subdir')
        ls_node = parent_node.getElementsByTagName("dirs")
        if len(ls_node) == 0:
            parent_node.appendChild(sub_node)
        else:
            parent_dirs_node = ls_node[0]
            parent_dirs_node.appendChild(sub_node)
        name_node = doc.createElement('name')
        sub_node.appendChild(name_node)
        name_node.appendChild(doc.createTextNode(dir_object.name))
        mtime_node = doc.createElement('mtime')
        sub_node.appendChild(mtime_node)
        mtime_node.appendChild(doc.createTextNode(TimeStampToTime(dir_object.stat.st_mtime)))
        files_node = doc.createElement('files')
        sub_node.appendChild(files_node)
        files_node.appendChild(doc.createTextNode(str(dir_object.file_num)))
        dirs_node = doc.createElement('dirs')
        sub_node.appendChild(dirs_node)
        dirs_node.attributes['num'] = str(len(dir_object.dirs))
        return sub_node
    def gen_sub_xml_node_3(self, dir_object, parent_node, doc):
        sub_node = doc.createElement('subdir')
        ls_node = parent_node.getElementsByTagName("dirs")
        if len(ls_node) == 0:
            parent_node.appendChild(sub_node)
        else:
            parent_dirs_node = ls_node[0]
            parent_dirs_node.appendChild(sub_node)
        sub_node.attributes['name'] = dir_object.name
        mtime_node = doc.createElement('mtime')
        sub_node.appendChild(mtime_node)
        mtime_node.appendChild(doc.createTextNode(TimeStampToTime(dir_object.stat.st_mtime)))
        files_node = doc.createElement('files')
        sub_node.appendChild(files_node)
        files_node.appendChild(doc.createTextNode(str(dir_object.file_num)))
        dirs_node = doc.createElement('dirs')
        sub_node.appendChild(dirs_node)
        dirs_node.attributes['num'] = str(len(dir_object.dirs))
        return sub_node
    def write_xml(self,xml_path):
        #定义XML文档对象
        doc=XmlDocument.Document()
        #创建根节点
        root = doc.createElement('root')
        doc.appendChild(root)
        root.attributes['path'] = self.root_dir.path
        root.attributes['ctime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        root.attributes['version'] = "0.7.11.23"
        root.attributes['mtime'] = TimeStampToTime(self.root_dir.stat.st_mtime)
        root.attributes['ino'] = str(self.root_dir.stat.st_ino)
        root.attributes['dev'] = str(self.root_dir.stat.st_dev)
        root.attributes['files'] = str(self.root_dir.file_num)
        root.attributes['dirs'] = str(len(self.root_dir.dirs))
        ls = []
        ls.append([self.root_dir, root])
        print("============================")
        while len(ls) != 0:
            dir_pair = ls.pop(-1)
            dir_object = dir_pair[0]
            for item in dir_object.dirs:
                sub_node = self.gen_sub_xml_node(dir_object.dirs[item], dir_pair[1], doc)
                ls.append([dir_object.dirs[item],sub_node])
        with open(xml_path,'w',encoding="utf-8") as f:
            f.write(doc.toxml())
    def gen_sub_json_node(self, dir_object, parent_node):
        sub_node = {}
        parent_node["sub_dirs"].append(sub_node)
        sub_node['name'] = dir_object.name
        sub_node['mtime'] = TimeStampToTime(dir_object.stat.st_mtime)
        #sub_node.attributes['ino'] = str(dir_object.stat.st_ino)
        #sub_node.attributes['dev'] = str(dir_object.stat.st_dev)
        sub_node['files'] = str(dir_object.file_num)
        sub_node['dirs'] = str(len(dir_object.dirs))
        return sub_node
    def to_dict(self):
        root = {}
        if self.root_dir is None:
            return root
        root['path'] = self.root_dir.path
        root['ctime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        root['version'] = "0.7.11.23"
        root['mtime'] = TimeStampToTime(self.root_dir.stat.st_mtime)
        root['ino'] = str(self.root_dir.stat.st_ino)
        root['dev'] = str(self.root_dir.stat.st_dev)
        root['files'] = str(self.root_dir.file_num)
        root['dirs'] = str(len(self.root_dir.dirs))
        ls = []
        ls.append([self.root_dir, root])
        print("============================")
        while len(ls) != 0:
            dir_pair = ls.pop(-1)
            dir_object = dir_pair[0]
            for item in dir_object.dirs:
                if dir_pair[1].get("sub_dirs") == None:
                    dir_pair[1]["sub_dirs"] = []
                sub_node = self.gen_sub_json_node(dir_object.dirs[item], dir_pair[1])
                ls.append([dir_object.dirs[item],sub_node])
        return root
    def write_json(self,json_path):
        dirs_dict = self.to_dict()
        with open(json_path,'w',encoding="utf-8") as f:
            f.write(json.dumps(dirs_dict, ensure_ascii=False, separators=(',', ':')))

if __name__ == "__main__":
    snapshot = Sl_Snapshot()
    snapshot.create_dir_object_tree(os.path.abspath("."))
    snapshot.write_xml("./test.xml")
    snapshot.write_json("./test.json")