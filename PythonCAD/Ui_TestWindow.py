# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\mboscolo\Desktop\R38\pythoncad\PythonCAD\TestWindow.ui'
#
# Created: Tue Jun 01 13:04:10 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_TestDialog(object):
    def setupUi(self, TestDialog):
        TestDialog.setObjectName("TestDialog")
        TestDialog.resize(609, 377)
        self.horizontalLayout = QtGui.QHBoxLayout(TestDialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetMaximumSize)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.uiTextEditor = QtGui.QPlainTextEdit(TestDialog)
        self.uiTextEditor.setProperty("cursor", QtCore.Qt.IBeamCursor)
        self.uiTextEditor.setReadOnly(True)
        self.uiTextEditor.setCenterOnScroll(True)
        self.uiTextEditor.setObjectName("uiTextEditor")
        self.verticalLayout.addWidget(self.uiTextEditor)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ImputCmd = QtGui.QLineEdit(TestDialog)
        self.ImputCmd.setEnabled(True)
        self.ImputCmd.setAutoFillBackground(True)
        self.ImputCmd.setObjectName("ImputCmd")
        self.horizontalLayout_2.addWidget(self.ImputCmd)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(TestDialog)
        QtCore.QObject.connect(self.uiTextEditor, QtCore.SIGNAL("textChanged()"), self.uiTextEditor.update)
        QtCore.QObject.connect(self.ImputCmd, QtCore.SIGNAL("returnPressed()"), self.uiTextEditor.centerCursor)
        QtCore.QMetaObject.connectSlotsByName(TestDialog)

    def retranslateUi(self, TestDialog):
        TestDialog.setWindowTitle(QtGui.QApplication.translate("TestDialog", "Dialog", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    TestDialog = QtGui.QDialog()
    ui = Ui_TestDialog()
    ui.setupUi(TestDialog)
    TestDialog.show()
    sys.exit(app.exec_())

