# read write file
import os,traceback
import shutil
import time
from datetime import datetime
import glob
import json 

# from yaml import load, dump
# from yaml import Loader, Dumper
# import yaml

def createFile(file) :
    if '\\' in file :
        file = file.replace('\\', '/')

    dir = file.replace(file.split('/')[-1], '')
    if not os.path.exists(dir) :
        os.makedirs(dir)

    f = open(file, 'w')
    f.close()
    return True

def writeFile(file, data) :
    f = open(file, 'w')
    f.write(data)
    f.close()
    return True

def appendData(file, data) :
    f = open(file, 'a')
    f.write(data)
    f.close()
    return True

def readFile(file) :
    f = open(file, 'r')
    data = f.read()
    return data

def eraseData(file) :
    f = open(file, 'w')
    f.close()
    return True

def copy(src, dst) :
    if os.path.exists(src) :
        dstDir = dst.replace(dst.split('/')[-1], '')
        if not os.path.exists(dstDir) :
            os.makedirs(dstDir)

        shutil.copy2(src, dst)

    if os.path.exists(dst):
        return dst

def remove(file):
    os.remove(file)

def copyTree(src, dst) :
    if os.path.exists(src) :
        shutil.copytree(src, dst, symlinks=False, ignore=None)
    return dst

def listFolder(path='',prefix='',pad=''):
    dirs = []
    try:
        if os.path.exists(path):
            # print path
            # path = path.replace('\\','/')
            # print os.path.join(path, d).replace('\\','/')
            for i in [d for d in os.listdir(path) if os.path.isdir(os.path.join(path,d))]:
                if len(prefix) and pad:
                    if i[:len(prefix)] == prefix:
                        if type(pad) == type(int()):
                            number = i[len(prefix):(len(prefix)+int(pad))]
                            if int(len(number)) == int(pad):
                                dirs.append(i)

                elif len(prefix):
                    if i[:len(prefix)] == prefix:
                        dirs.append(i)

                elif type(pad) == type(int()):
                    number = i[len(prefix):(len(prefix)+int(pad))]
                    if int(len(number)) == int(pad):
                        dirs.append(i)

                elif not len(prefix):
                    dirs.append(i)


        return sorted(dirs)
    except:
        traceback.print_exc()
        return dirs

def listFile(path,ex='',prefix='',pad=''):
    dirs = []
    # print path,ex,prefix,pad
    try:
        if os.path.exists(path):
            for i in [d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d))]:
                # if len(ex):
                #     if not os.path.splitext(i)[-1][1:] == ex:
                #         continue

                if len(prefix) and pad:
                    if i[:len(prefix)] == prefix:
                        print i[:len(prefix)], prefix
                        if type(pad) == type(int()):
                            number = i[len(prefix):(len(prefix)+int(pad))]
                            if int(len(number)) == int(pad):
                                if len(ex):
                                    if i.split('.')[-1] == ex:
                                        dirs.append(i)
                                else:
                                    dirs.append(i)

                elif len(prefix):
                    if i[:len(prefix)] == prefix:
                        if len(ex):
                           if i.split('.')[-1] == ex:
                                dirs.append(i)
                        else:
                            dirs.append(i)

                elif type(pad) == type(int()):
                    number = i[len(prefix):(len(prefix)+int(pad))]
                    if int(len(number)) == int(pad):
                        if len(ex):
                           if i.split('.')[-1] == ex:
                                dirs.append(i)
                        else:
                            dirs.append(i)

                elif not len(prefix):
                    if len(ex):
                       if i.split('.')[-1] == ex:
                            dirs.append(i)
                    else:
                        dirs.append(i)

        return sorted(dirs)
    except:
        return dirs

def rename(src, dst) :
    if os.path.exists(src) :
        return os.rename(src, dst)

    else :
        print 'File not Exists'

def increment_version(filename):
    if not os.path.exists(filename):
        return filename
    dirname = os.path.dirname(filename)
    basename = os.path.basename(filename)
    ver = find_version(basename)
    firstElem = basename.split('_%s_' % ver)[0]
    lastElem = basename.split('_%s_' % ver)[-1]
    print 'num', ver
    num = int(ver[1:])+1
    verPad = 'v%03d' % num
    versionName = basename.replace(ver, verPad)
    return increment_version('%s/%s' % (dirname, versionName))

def find_next_version(files):
    vers = sorted([int(find_version(a).replace('v', '') if find_version(a) else 0) for a in files])

    if vers:
        newVer = vers[-1] + 1
        return 'v%03d' % newVer

    return 'v001'


def find_version(filename, prefix='v', padding=3):
    elems = filename.split('.')[0].split('_')
    for elem in elems:
        if elem[0] == prefix and elem[1:].isdigit():
            return elem

def find_next_image_path(img_path,chkname=''):
    # get image path with next 4 padding number
    img_dir = os.path.dirname(img_path)
    img_type = img_path.split('.')[-1]

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    if os.path.exists(img_dir):
        imgs = listFile(img_dir)

    if imgs:
        index = len(imgs) + 1
    else:
        index = 1

    image_path = '%s.%04d.%s' %(img_path,index,img_type)

    return image_path

def get_modified_time(filePath):
    return time.mtime(os.path.getmtime(filePath))

def get_now_time():
    now = str(datetime.now())
    return now.split('.')[0]

def ymlDumper(file, dictData) :
    # input dictionary data
    data = yaml.dump(dictData, default_flow_style=False)
    result = writeFile(file, data)

    return result


def ymlLoader(file) :
    data = readFile(file)
    dictData = yaml.load(data)

    return dictData

def search_replace_file(srcFile, search, replace, removeLine = True, backupFile = True) :
    if backupFile :
        backupSuccess = backup(srcFile)

    else :
        backupSuccess = True

    if backupSuccess :
        # open file
        f = open(srcFile, 'r')
        data = f.read()
        f.close()

        if removeLine :
            replace = ''

        replaceData = data.replace(search, replace)

        # write back
        f = open(srcFile, 'w')
        f.write(replaceData)
        f.close()

        return True

def search_replace_keys(srcFile, searchReplaceDict, backupFile = True) :
    if backupFile :
        backupSuccess = backup(srcFile)

    else :
        backupSuccess = True

    if backupSuccess :
        # open file
        f = open(srcFile, 'r')
        data = f.read()
        f.close()

        for search, replace in searchReplaceDict.iteritems():
            data = data.replace(search, replace)

        replaceData = data

        # write back
        f = open(srcFile, 'w')
        f.write(replaceData)
        f.close()

        return True

def backup(srcFile) :
    backupName = '.bk'
    srcDir = os.path.dirname(srcFile)
    backupDir = '%s/%s' % (srcDir, backupName)
    timeSuffix = str(datetime.now()).replace(' ', '_').split('.')[0].replace(':', '-')
    basename = os.path.basename(srcFile)
    ext = basename.split('.')[-1]
    backupFile = '%s/%s_%s.%s' % (backupDir, basename, timeSuffix, ext)

    # create backup dir
    if not os.path.exists(backupDir) :
        os.makedirs(backupDir)

    # backup
    result = backupSuccess = copy(srcFile, backupFile)

    return result

def get_latest_file(srcDir):
    # print srcDir
    # print listFile(srcDir)
    list_of_files = glob.glob('%s/*' %(srcDir)) # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def copy_to_clipboard(text): 
    result = os.system("echo '%s'|clip" % text)
    return result


def json_dumper(path, data): 
    if not os.path.exists(os.path.dirname(path)): 
        os.makedirs(os.path.dirname(path))
    with open(path, 'w') as outfile:
        json.dump(data, outfile) 


def json_loader(path): 
    with open(path) as configData: 
        config = json.load(configData)
        return config
