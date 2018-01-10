# pyside package 
import sys
import os 
import config_env 
env = config_env.read()

def add(root): 
    packagePath = '%s/%s' % (root, env.get('PACKAGE'))
    qtPath = '%s/%s' % (root, env.get('QTPATH'))
    toolPath = '%s/%s' % (root, env.get('TOOLPATH'))
    configPath = '%s/%s' % (root, env.get('CONFIG'))
    mayaToolPath = '%s/%s' % (root, env.get('MAYATOOL'))

    appendPaths = [packagePath, qtPath, toolPath, configPath, mayaToolPath]

    # add PySide lib path
    for path in appendPaths:
        if not path in sys.path:
            sys.path.append(path)
