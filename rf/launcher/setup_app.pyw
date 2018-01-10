# v.0.0.1 wip

#Import python modules
import sys
import os 
import json 
import logging
import launcher_env
import getpass
import subprocess
import _subprocess


moduleDir = os.path.dirname(sys.modules[__name__].__file__)
appName = os.path.splitext(os.path.basename(sys.modules[__name__].__file__))[0]
launcherEnv = launcher_env.read()

import log_utils 
logFile = log_utils.name(appName, user=getpass.getuser())
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
RFUSER = config.get('USER')
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

class IconPath: 
    logo = '%s/icons/title2.png' % moduleDir

class Path: 
    python = 'C:/python27/python.exe'
    install_env = 'O:/install_env.py'


class RFSetup(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFSetup, self).__init__(parent)

        # ui read
        uiFile = '%s/setup_ui.ui' % moduleDir

        if isMaya: 
            self.ui = load.setup_ui_maya(uiFile, self)
        else: 
            self.ui = load.setup_ui(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('Riff Setup')

        self.set_info()


    def set_info(self): 
        """ set display information on the tool """ 
        self.set_logo()
        self.set_custom_command()
        self.set_script_root()
        self.check_user()


    def set_custom_command(self): 
        """ add command """ 
        self.set_user_ui()
        self.install_env_ui()


    def set_user_ui(self): 
        # ui 
        self.userLayout = QtWidgets.QHBoxLayout()
        self.userLabel = QtWidgets.QLabel()
        self.inputUser = QtWidgets.QLineEdit()
        self.userPushButton = QtWidgets.QPushButton()

        self.userLabel.setText('1. Please set user name')
        self.userPushButton.setText('Set User')

        self.ui.custom_verticalLayout.addWidget(self.userLabel, 0)
        self.userLayout.addWidget(self.inputUser, 2, 0)
        self.userLayout.addWidget(self.userPushButton, 2, 1)
        self.ui.custom_verticalLayout.addLayout(self.userLayout)

        # button signals 
        self.userPushButton.clicked.connect(self.set_user)

        self.check_user()

    def check_user(self): 
        # guess user 
        currentUser = os.environ.get(RFUSER)

        if not currentUser: 
            self.inputUser.setText(getpass.getuser())
        else: 
            self.userLabel.setText('Current User : ')
            self.inputUser.setText(currentUser)


    def set_user(self): 
        """ set user call back """ 
        user = str(self.inputUser.text())
        result = QtWidgets.QMessageBox.information(self, 'Confirm', 'Do you want to set user to %s?' % user, QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Cancel)

        if result == QtWidgets.QMessageBox.Ok: 
            os.environ[RFUSER] = user
            env.set_env(RFUSER, user)
            self.check_user()
            self.output('User set to %s' % user)


    def install_env_ui(self): 
        """ install env pushButton """
        self.ui.env_pushButton.clicked.connect(self.install_env)


    def install_env(self): 
        self.output('Installing env ...')
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
        p = subprocess.Popen([Path.python, Path.install_env], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        returnCode = p.returncode
        self.output(stdout)
        self.output(stderr)

        logger.info(stdout)
        logger.info(stderr)

        self.output('Install env complete')

    def set_script_root(self): 
        """ get script root """ 
        root = os.environ.get(RFSCRIPT_VAR)
        self.ui.scriptRoot_label.setText(root)


    def set_logo(self): 
        self.ui.logo_label.setPixmap(QtGui.QPixmap(IconPath.logo).scaled(444, 59, QtCore.Qt.KeepAspectRatio))

    def output(self, message): 
        self.ui.log_plainTextEdit.appendPlainText('%s\n' % message)


def show():
    if isMaya:
        logger.info('Run in Maya\n')
        uiName = 'RFSetup'
        deleteUI(uiName)
        myApp = RFSetup(getMayaWindow())
        # myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = RFSetup()
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
