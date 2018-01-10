from PySide import QtCore
from PySide import QtGui

class UserWidget(QtGui.QWidget) :
    def __init__(self, parent = None) :
        super(UserWidget, self).__init__(parent)
        # set label
        self.allLayout = QtGui.QVBoxLayout()

        self.text1Label = QtGui.QLabel()
        self.listWidget = QtGui.QListWidget()


        self.text1Label.setText('hello')


        self.allLayout.addWidget(self.text1Label)
        self.allLayout.addWidget(self.listWidget)


        self.setLayout(self.allLayout)

        # set font
        font = QtGui.QFont()
        font.setPointSize(9)
        # font.setWeight(70)
        font.setBold(True)
        self.text1Label.setFont(font)


