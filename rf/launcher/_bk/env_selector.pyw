# v.0.0.1 beta
_version = 'v.0.0.1'

#Import python modules
import sys
import os 
import json 
import logging
import env_config 
import subprocess
import _subprocess


moduleDir = os.path.dirname(sys.modules[__name__].__file__)
appName = os.path.splitext(os.path.basename(sys.modules[__name__].__file__))[0]

env = env_config.read()

# initial env setup 
RFSCRIPT_VAR = env.get('SCRIPT_VAR')
root = env.get('DEV_ENV').get(RFSCRIPT_VAR)
qtPath = env.get('QTPATH')
sys.path.append('%s/%s' % (root, qtPath))


os.environ['QT_PREFERRED_BINDING'] = os.pathsep.join(['PySide', 'PySide2'])
from Qt import wrapInstance
from Qt import QtCore
from Qt import QtWidgets
from Qt import QtGui

import log_utils
import load

logFile = log_utils.name(appName, user='TA')
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)

logger.info('Running Env Selector from %s' % root)

logger.info('\n\n==============================================')

class IconPath: 
    logo = '%s/icons/riff_title.png' % moduleDir

class RFEnvSelector(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #Setup Window
        super(RFEnvSelector, self).__init__(parent)

        # ui read
        uiFile = '%s/env_selector.ui' % moduleDir

        self.ui = load.setup_ui(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('Riff Environment Selector %s' % _version)

        self.set_logo()
        self.refresh()
        self.init_signals()

    
    def set_logo(self): 
        self.ui.logo_label.setPixmap(QtGui.QPixmap(IconPath.logo).scaled(400, 50, QtCore.Qt.KeepAspectRatio))

    def refresh(self): 
        self.read_env()


    def init_signals(self): 
        self.ui.dev_pushButton.clicked.connect(self.set_dev)
        self.ui.production_pushButton.clicked.connect(self.set_production)


    def read_env(self): 
        current = os.environ.get(RFSCRIPT_VAR)
        self.ui.env_label.setText(current)


    def set_dev(self): 
        """ set env to dev """ 
        devPath = env.get('DEV_ENV').get(RFSCRIPT_VAR)
        set_env(RFSCRIPT_VAR, devPath)
        os.environ[RFSCRIPT_VAR] = devPath
        self.read_env()
        # self.close()
        # run_launcher(devPath)

    def set_production(self): 
        """ set env to production """ 
        prodPath = env.get('PROD_ENV').get(RFSCRIPT_VAR)
        set_env(RFSCRIPT_VAR, prodPath)
        os.environ[RFSCRIPT_VAR] = prodPath
        self.read_env()
        # self.close()
        # run_launcher(prodPath)


class Launcher:
    pythonPath = 'C:/python27/python.exe'
    path = '%s' % 'app/launcher/launcher_app.pyw'


def set_env(var, value): 
    """ subprocess call changing env value """ 
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen(['SETX', var, value], startupinfo=startupinfo, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_launcher(root): 
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
    path = '%s/%s' % (root, Launcher.path)
    p = subprocess.Popen([Launcher.pythonPath, path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    returnCode = p.returncode

    logger.info(stdout)
    logger.info(stderr)


def show():
    logger.info('Run in standalone\n')
    app = QtWidgets.QApplication.instance()
    if not app: 
        app = QtWidgets.QApplication(sys.argv)
    myApp = RFEnvSelector()
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
