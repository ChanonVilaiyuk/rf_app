# v.0.0.1 wip

#Import python modules
import sys
import os 
import json 
import logging
import launcher_env

moduleDir = os.path.dirname(sys.modules[__name__].__file__)
appName = os.path.splitext(os.path.basename(sys.modules[__name__].__file__))[0]
launcherEnv = launcher_env.read()

import log_utils 
logFile = log_utils.name(appName, user='TA')
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)

# read config environment 
relConfigPath = '%s/%s' % ('/'.join(moduleDir.split('\\')[0:-3]), launcherEnv.get('CONFIG'))
sys.path.append(relConfigPath)

# read global config 
import env 
import config_env
env.setup()
config = config_env.read() 

RFSCRIPT_VAR = config.get('SCRIPT_VAR')
RFSCRIPT = os.environ.get(RFSCRIPT_VAR)
env.add(RFSCRIPT)


try: 
    import maya.cmds as mc 
    import maya.mel as mm 
    import maya.OpenMayaUI as mui
    isMaya = True 
except ImportError: 
    isMaya = False

from rf.utils import log_utils
from rf.utils import load
from rf.userCheck import check 
import config

os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui


# If inside Maya open Maya GUI
def getMayaWindow():
    ptr = mui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

logger.info('Running RFSCRIPT from %s' % os.environ.get(RFSCRIPT_VAR))
logger.info('\n\n==============================================')



class RFLauncher(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFLauncher, self).__init__(parent)

        # ui read
        uiFile = '%s/ui.ui' % moduleDir

        if isMaya: 
            self.ui = load.setup_ui_maya(uiFile, self)
        else: 
            self.ui = load.setup_ui(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('Riff Desktop')

        self.set_info()


    def set_info(self): 
        """ set display information on the tool """ 
        self.set_script_root()
        self.check_user()


    def set_script_root(self): 
        """ get script root """ 
        root = os.environ.get(RFSCRIPT_VAR)
        self.ui.scriptRoot_label.setText(root)

    def check_user(self): 
        """ check user """ 
        pass


def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'RFLauncher'
        deleteUI(uiName)
        myApp = RFLauncher(getMayaWindow())
        # myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = RFLauncher()
        # myApp.show()
        if os.path.exists('%s/styleSheet/darkorange.css' % moduleDir) :
            try:
                app.setStyle('plastique')

                data = open('%s/styleSheet/darkorange.css' % moduleDir,'r').read()
                app.setStyleSheet(data+'QLabel { color : white; }')

            except Exception as e:
                logger.info(str(e))

        sys.exit(app.exec_())

def deleteUI(ui):
    if mc.window(ui, exists=True):
        mc.deleteUI(ui)
        deleteUI(ui)

if __name__ == '__main__': 
    show()
