# v.0.0.1 library wip
_title = 'RF Asset Library'
_version = 'v.0.0.1'
_des = 'wip'
uiName = 'RFLibrary'

#Import python modules
import sys
import os 
import logging
import getpass
import json

moduleDir = os.path.dirname(sys.modules[__name__].__file__)
appName = os.path.splitext(os.path.basename(sys.modules[__name__].__file__))[0]
rootDir = os.path.split(os.path.split(moduleDir)[0])[0]
configDir = '%s/config' % os.path.split(rootDir)[0]

try: 
    import maya.cmds as mc 
    import maya.mel as mm 
    import maya.OpenMayaUI as mui
    isMaya = True 
except ImportError: 
    isMaya = False
    sys.path.append(rootDir)
    
if not configDir in sys.path: 
    sys.path.append(configDir)

from rf.utils import tool_path
import config_env
# read config environment 
env = config_env.read()

# initial env setup 
RFSCRIPT_VAR = env.get('SCRIPT_VAR')
RFSCRIPT = os.environ.get(RFSCRIPT_VAR)
tool_path.add(RFSCRIPT)
user = '%s-%s' % (os.environ.get('RFUSER'), getpass.getuser())

from rf.utils import log_utils
from rf.utils import load
from rf.utils import file_utils
from startup import setEnv
from startup import config

if isMaya: 
    from rftool.utils import maya_utils
    from rftool.fix.polytag import polytag_core2 as polytag_core
if not isMaya: 
    setEnv.setProject()

import file_hook as db_hook
try: 
    import sg_hook
except Exception as e: 
    logger.error(e)

# set logger
logFile = log_utils.name(appName, user=user)
logger = log_utils.init_logger(logFile)
logger.setLevel(logging.INFO)

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

class Icon: 
    logo = '%s/%s/riff_bg.png' % (os.environ.get(RFSCRIPT_VAR), env.get('ICON'))
    noPreviewImg = '%s/%s/tmp_thumbnail_wide.jpg' % (os.environ.get(RFSCRIPT_VAR), env.get('ICON'))

class DbKey: 
    projectPath = 'sg_project_path'
    projectName = 'name'
    projectId = 'id'

class SettingCache: 
    project = 'project'
    type = 'type'
    subtype = 'subtype'


class RFAssetLibrary(QtWidgets.QMainWindow):

    def __init__(self, sg=True, parent=None):
        #Setup Window
        super(RFAssetLibrary, self).__init__(parent)

        # ui read
        uiFile = '%s/ui.ui' % moduleDir

        if isMaya: 
            self.ui = load.setup_ui_maya(uiFile, self)
        else: 
            self.ui = load.setup_ui(uiFile, self)
        self.ui.show()
        self.ui.setWindowTitle('%s %s - %s' % (_title, _version, _des))

        if sg: 
            global db_hook
            db_hook = sg_hook

        # cache 
        self.projectCaches = dict()
        self.assetCached = dict()

        # assetMode
        self.mayaFile = 'mayaFile'
        self.mayaAsm = 'mayaAsm'
        self.mayaGpu = 'mayaGpu'
        self.mayaPolytag = 'mayaPolytag'

        # button name 
        self.importMode = 'import'
        self.referenceMode = 'reference'
        self.openMode = 'open'
        self.polytagMode = 'import polytag'

        # temp file for tool 
        self.tempDataPath = '%s/%s/%s.json' % (os.environ.get('TEMP'), env.get('TEMPTOOL'), uiName)
        self.tempData = dict()

        self.init_signals()
        self.set_info()


    def set_info(self): 
        """ set display information on the tool """ 
        self.read_cache_data()
        self.set_default_value()
        self.set_script_root()
        self.check_user()
        self.set_logo()
        self.list_project()


    def read_cache_data(self): 
        """ read previous cache data """
        if not os.path.exists(self.tempDataPath): 
            self.tempData = file_utils.json_dumper(self.tempDataPath, self.tempData)
        self.tempData = file_utils.json_loader(self.tempDataPath)


    def write_temp_data(self, key, value): 
        """ write temp setting """ 
        tempData = file_utils.json_loader(self.tempDataPath)
        tempData.update({key: value})
        file_utils.json_dumper(self.tempDataPath, tempData)


    def set_default_value(self): 
        self.icon_size_default()
        self.ui.ref_listWidget.setEnabled(False)
        self.set_action_button()


    def icon_size_default(self): 
        self.ui.icon_horizontalSlider.setMinimum(60)
        self.ui.icon_horizontalSlider.setMaximum(200)
        self.ui.icon_horizontalSlider.setSingleStep(10)
        self.ui.icon_horizontalSlider.setValue(100)

    def init_signals(self): 
        # comboBox
        self.ui.project_comboBox.currentIndexChanged.connect(self.project_signal)
        self.ui.type_comboBox.currentIndexChanged.connect(self.type_signal)
        self.ui.subtype_comboBox.currentIndexChanged.connect(self.subtype_signal)

        # library listWidget
        self.ui.library_listWidget.itemSelectionChanged.connect(self.library_signal)

        # icon 
        self.ui.icon_horizontalSlider.valueChanged.connect(self.set_icon_size)

        # button
        self.ui.reference_radioButton.clicked.connect(self.set_action_button)
        self.ui.import_radioButton.clicked.connect(self.set_action_button)
        self.ui.open_radioButton.clicked.connect(self.set_action_button)
        self.ui.polytag_radioButton.clicked.connect(self.set_action_button)
        self.ui.command_pushButton.clicked.connect(self.action_button)

        self.ui.custom_radioButton.toggled.connect(self.set_ref_ui)

        # search lineEdit 
        self.ui.search_lineEdit.returnPressed.connect(self.search)
        self.ui.search_pushButton.clicked.connect(self.search)


    def set_script_root(self): 
        """ get script root """ 
        root = os.environ.get(RFSCRIPT_VAR)

    def check_user(self): 
        """ check if user name is proper setup """ 
        user = os.environ.get(env.get('USER'))


    def set_logo(self): 
        self.ui.logo_label.setPixmap(QtGui.QPixmap(Icon.logo).scaled(600, 60, QtCore.Qt.KeepAspectRatio))

    def set_preview(self, path): 
        self.ui.preview_label.setPixmap(QtGui.QPixmap(path).scaled(360, 360, QtCore.Qt.KeepAspectRatio))        


    def list_project(self): 
        """ list project from db """ 
        self.ui.project_comboBox.clear()
        projects = self.get_project()
        
        # read selection cache
        defaultSel = self.tempData.get(SettingCache.project, None)

        for row, project in enumerate(projects): 
            self.ui.project_comboBox.addItem(project)
        
        # set to last selection 
        if defaultSel in projects: 
            index = projects.index(defaultSel)
            self.ui.project_comboBox.setCurrentIndex(index)


    def project_signal(self): 
        """ list type """
        selProject = self.list_type()
        # write project selection 
        self.write_temp_data(SettingCache.project, selProject)


    def list_type(self): 
        project = str(self.ui.project_comboBox.currentText())
        projectData = self.projectCaches.get(project)
        
        # read selection cache
        defaultSel = self.tempData.get(SettingCache.type, None)

        self.ui.type_comboBox.clear()

        if projectData: 
            root = projectData.get(DbKey.projectPath, '')
            projectName = projectData.get(DbKey.projectName, '')

            if root and projectName: 
                types = db_hook.get_type(root, projectName)
                self.ui.type_comboBox.addItems(types)

        # set to last selection 
        if defaultSel in types: 
            index = types.index(defaultSel)
            self.ui.type_comboBox.setCurrentIndex(index)

        return project


    def type_signal(self): 
        selType = self.list_subtype()
         # write type selection 
        self.write_temp_data(SettingCache.type, selType)

    
    def list_subtype(self): 
        """ list subtype """ 
        self.ui.subtype_comboBox.clear()

        project = str(self.ui.project_comboBox.currentText())
        projectData = self.projectCaches.get(project)

        # read selection cache
        defaultSel = self.tempData.get(SettingCache.subtype, None)

        assetType = str(self.ui.type_comboBox.currentText())
        subtypes = db_hook.get_subtypes(projectData, assetType)
        self.ui.subtype_comboBox.addItems(subtypes)

        # set to last selection 
        if defaultSel in subtypes: 
            index = subtypes.index(defaultSel)
            self.ui.subtype_comboBox.setCurrentIndex(index)

        return assetType


    def subtype_signal(self): 
        selSubType = self.list_asset()
         # write type selection 
        self.write_temp_data(SettingCache.subtype, selSubType)


    def list_asset(self): 
        """ list asset """ 
        # ui selection 
        project = str(self.ui.project_comboBox.currentText())
        projectData = self.projectCaches.get(project)
        assetType = str(self.ui.type_comboBox.currentText())
        assetSubType = str(self.ui.subtype_comboBox.currentText())
        searchFilter = str(self.ui.search_lineEdit.text())


        assets = self.get_asset(projectData, assetType, assetSubType)

        self.ui.library_listWidget.clear()

        for asset in assets: 
            # search filter 
            if searchFilter: 
                if searchFilter.lower() in asset.name.lower(): 
                    self.add_asset(asset)
            
            # normal loop 
            else: 
                self.add_asset(asset)

        return assetSubType


    def add_asset(self, asset):
        mediaFile = asset.mediaFile
        refPath, filetype = self.get_ref_path(asset)

        if not os.path.exists(mediaFile): 
            mediaFile = Icon.noPreviewImg
        
        size = self.ui.icon_horizontalSlider.value()

        item = QtWidgets.QListWidgetItem(self.ui.library_listWidget)
        iconWidget = QtGui.QIcon()
        iconWidget.addPixmap(QtGui.QPixmap(mediaFile),QtGui.QIcon.Normal,QtGui.QIcon.Off)
        item.setIcon(iconWidget)
        item.setText(asset.name)
        item.setData(QtCore.Qt.UserRole, [asset, mediaFile])
        self.ui.library_listWidget.setIconSize(QtCore.QSize(size, size))
        
        # file exists 
        if not os.path.exists(refPath): 
            color = [100, 0, 0]
            item.setBackground(QtGui.QColor(color[0], color[1], color[2]))


    def get_asset(self, projectData, assetType, assetSubType): 
        """ cache for asset list """ 
        if assetType in self.assetCached.keys(): 
            if assetSubType in self.assetCached[assetType].keys(): 
                assets = self.assetCached[assetType][assetSubType]
                logger.debug('Read from cache')

            else: 
                assets = db_hook.get_assets(projectData, assetType, assetSubType)
                self.assetCached[assetType].update({assetSubType: assets})
                logger.debug('Rescan asset')

        else: 
            assets = db_hook.get_assets(projectData, assetType, assetSubType)
            self.assetCached.update({assetType: {assetSubType: assets}})
            logger.debug('Rescan asset')

        return assets


    def library_signal(self): 
        """ signal for select asset """ 
        item = self.ui.library_listWidget.currentItem()
        asset, mediaFile = item.data(QtCore.Qt.UserRole)

        # preview 
        self.set_preview(mediaFile)
        self.list_ref(asset)

    def list_ref(self, asset): 
        # list ref 
        self.ui.ref_listWidget.clear()
        files = asset.getRefs()
        self.ui.ref_listWidget.addItems(files)



    def get_project(self): 
        if not self.projectCaches: 
            projects = db_hook.get_project()

            for project in projects: 
                self.projectCaches.update({project.get('name'): project})

        return sorted(self.projectCaches)


    def set_icon_size(self): 
        value = self.ui.icon_horizontalSlider.value()
        self.ui.library_listWidget.setIconSize(QtCore.QSize(value, value))


    def set_action_button(self): 
        """ set action button """
        mode = self.get_button_mode()
        self.ui.command_pushButton.setText(mode.capitalize())

        if mode == self.referenceMode: 
            asm = True
            rig = True
            gpu = True
            model = True
            custom = True

        if mode == self.importMode: 
            asm = False
            rig = True
            gpu = False
            model = True
            custom = True

        if mode == self.openMode: 
            asm = True
            rig = True
            gpu = True
            model = True
            custom = True

        if mode == self.importMode: 
            asm = False
            rig = True
            gpu = False
            model = True
            custom = True

        if mode == self.polytagMode: 
            asm = False
            rig = True
            gpu = True
            model = True
            custom = False

        self.ui.asm_radioButton.setEnabled(asm)
        self.ui.rig_radioButton.setEnabled(rig)
        self.ui.gpu_radioButton.setEnabled(gpu)
        self.ui.model_radioButton.setEnabled(model)
        self.ui.custom_radioButton.setEnabled(custom)
        self.ui.rig_radioButton.setChecked(True)


    def action_button(self): 
        """ button icon """
        # get selected asset
        item = self.ui.library_listWidget.currentItem()
        mode = self.get_button_mode()

        if item: 
            asset, mediaFile = item.data(QtCore.Qt.UserRole)

            if isMaya: 
                namespace = asset.name
                refPath, filetype = self.get_ref_path(asset)

                if os.path.exists(refPath): 
                    # regular ma file
                    if filetype == self.mayaFile: 
                        if mode == self.referenceMode: 
                            maya_utils.create_reference(namespace, refPath)
                            logger.info('Create reference %s' % refPath)

                        if mode == self.importMode: 
                            maya_utils.import_file(namespace, refPath)
                            logger.info('Import file %s' % refPath)

                        if mode == self.polytagMode: 
                            maya_utils.import_polytag(namespace, refPath)
                            logger.info('Import polytag %s' % refPath)

                        if mode == self.openMode: 
                            maya_utils.open_file(refPath)
                            logger.info('Open file %s' % refPath)

                    # ad file 
                    if filetype == self.mayaAsm: 
                        maya_utils.create_asm_reference(namespace, refPath)
                        logger.info('Create assembly reference %s' % refPath)

                    if filetype == self.mayaGpu: 
                        node = maya_utils.create_gpu(namespace, refPath)
                        logger.info('Create gpu node %s' % refPath)


    def set_ref_ui(self, value): 
        self.ui.ref_listWidget.setEnabled(not value)


    def get_ref_path(self, asset): 
        step, ext, filetype = self.get_filetype()
        res = self.get_res()
        mode = self.get_button_mode()
        
        # if scene assembly 
        if step == config.asmSuffix: 
            res = None

        refPath = '%s/%s' % (asset.libPath(), asset.libName(step=step, res=res, ext=ext))
        return refPath, filetype

    def get_filetype(self): 
        if self.ui.asm_radioButton.isChecked(): 
            filetype = [config.asmSuffix, config.refExt, self.mayaAsm]
        if self.ui.rig_radioButton.isChecked(): 
            filetype = ['rig', config.refExt, self.mayaFile]
        if self.ui.gpu_radioButton.isChecked(): 
            filetype = ['gpu', config.gpuExt, self.mayaGpu]
        if self.ui.model_radioButton.isChecked(): 
            filetype = ['model', config.refExt, self.mayaFile]
        if self.ui.custom_radioButton.isChecked(): 
            filetype = ['custom', config.refExt, self.mayaFile]
        return filetype

    def get_res(self): 
        if self.ui.pr_radioButton.isChecked(): 
            res = config.proxyRes
        if self.ui.md_radioButton.isChecked(): 
            res = config.medRes
        return res

    def get_button_mode(self): 
        if self.ui.reference_radioButton.isChecked(): 
            mode = self.referenceMode
        if self.ui.import_radioButton.isChecked(): 
            mode = self.importMode
        if self.ui.open_radioButton.isChecked(): 
            mode = self.openMode
        if self.ui.polytag_radioButton.isChecked(): 
            mode = self.polytagMode
        return mode


    def search(self): 
        """ search asset on the list """ 
        self.list_asset()



def show(sg=True):
    if isMaya:
        logger.info('Run in Maya\n')
        deleteUI(uiName)
        myApp = RFAssetLibrary(sg=sg, parent=getMayaWindow())
        # myApp.show()
        return myApp

    else:
        logger.info('Run in standalone\n')
        app = QtWidgets.QApplication.instance()
        if not app: 
            app = QtWidgets.QApplication(sys.argv)
        myApp = RFAssetLibrary(sg=sg)
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
    show(sg=False)
