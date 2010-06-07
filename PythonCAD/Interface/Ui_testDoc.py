# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\Interface\testDoc.ui'
#
# Created: Mon Jun 07 09:00:18 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_DockWidgetDebug(object):
    def setupUi(self, DockWidgetDebug):
        DockWidgetDebug.setObjectName("DockWidgetDebug")
        DockWidgetDebug.resize(476, 92)
        self.dockWidgetContents = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.verticalLayout_2.setMargin(2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textEditOutput = QtGui.QTextEdit(self.dockWidgetContents)
        self.textEditOutput.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.textEditOutput.sizePolicy().hasHeightForWidth())
        self.textEditOutput.setSizePolicy(sizePolicy)
        self.textEditOutput.setBaseSize(QtCore.QSize(0, 10))
        self.textEditOutput.setObjectName("textEditOutput")
        self.verticalLayout_2.addWidget(self.textEditOutput)
        self.lineEditInput = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEditInput.setEnabled(True)
        self.lineEditInput.setMinimumSize(QtCore.QSize(0, 16))
        self.lineEditInput.setObjectName("lineEditInput")
        self.verticalLayout_2.addWidget(self.lineEditInput)
        DockWidgetDebug.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidgetDebug)
        QtCore.QMetaObject.connectSlotsByName(DockWidgetDebug)

    def retranslateUi(self, DockWidgetDebug):
        DockWidgetDebug.setWindowTitle(QtGui.QApplication.translate("DockWidgetDebug", "DockWidget", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    DockWidgetDebug = QtGui.QDockWidget()
    ui = Ui_DockWidgetDebug()
    ui.setupUi(DockWidgetDebug)
    DockWidgetDebug.show()
    sys.exit(app.exec_())

