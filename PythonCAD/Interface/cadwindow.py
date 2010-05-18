############################################################################
# 
#  Copyright (C) 2004-2005 Trolltech AS. All rights reserved.
# 
#  This file is part of the example classes of the Qt Toolkit.
# 
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE.GPL included in the packaging of
#  this file.  Please review the following information to ensure GNU
#  General Public Licensing requirements will be met:
#  http://www.trolltech.com/products/qt/opensource.html
# 
#  If you are unsure which license is appropriate for your use, please
#  review the following information:
#  http://www.trolltech.com/products/qt/licensing.html or contact the
#  sales department at sales@trolltech.com.
# 
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
# 
############################################################################

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui

import cadwindow_rc
from customevent import testCmdLine
from Interface.cadscene import CadScene
from Interface.cadview  import CadView
from Ui_TestWindow      import Ui_TestDialog
from Interface.Commandline.cmdlinedock import CmdlineDock


class CadWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(CadWindow, self).__init__()

        self._scene = CadScene()
        self._view = CadView(self._scene, self)
        
        self.setCentralWidget(self._view)

        self._createActions()
        self._createMenus()
        self._createToolBars()
        self._createStatusBar()
        self._createDockWindows()
        
        self.setWindowTitle("PythonCAD (Qt)")

        self.setUnifiedTitleAndToolBarOnMac(True)
        

    def _onNewDrawing(self):
        """
            Create a new drawing 
        """
        self._scene.newDocument()
    

    def _onOpenDrawing(self):
        # ask the user to select an existing drawing
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Open Drawing", "/home", "Drawings (*.pdr)");
        # open a document and load the drawing
        if drawing != None:
            self._scene.openDocument(drawing)
    
    def _onImportDrawing(self):
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Import Drawing", "/home", "Dxf (*.dxf)");
        # open a document and load the drawing
        if drawing != None:
            self._scene.importDocument(drawing)
            
    def _onCloseDrawing(self):
        self._scene.closeDocument()
    
        
    def _onPrint(self):
        # TODO: printing
        self.statusBar().showMessage("Ready", 2000)

        
    def _onUndo(self):
        pass


    def _onAbout(self):
        QtGui.QMessageBox.about(self, "About PythonCAD",
                "<b>PythonCAD</b> is a 2D CAD system.")
        
    def _onDevelop(self):
        """
            on develop 
        """
        TestDialog = QtGui.QDialog()
        ui = Ui_TestDialog()
        ui.setupUi(TestDialog)
        tcl=testCmdLine(ui, self._scene)
        TestDialog.exec_()
        
        #qw=Ui_TestWindow()
        #self.setActiveWindow(qw)
        

    def _createActions(self):
        self.__new_drawing_action = QtGui.QAction(QtGui.QIcon(':/images/new.png'),
                "&New Drawing", self, shortcut=QtGui.QKeySequence.New,
                statusTip="Create a new drawing",
                triggered=self._onNewDrawing)

        self.__open_drawing_action = QtGui.QAction(QtGui.QIcon(':/images/open.png'),
                "&Open Drawing", self, shortcut=QtGui.QKeySequence.Open,
                statusTip="Open an existing drawing",
                triggered=self._onOpenDrawing)

        self.__import_drawing_action = QtGui.QAction(QtGui.QIcon(':/images/open.png'),
                "&Import Drawing", self, 
                statusTip="Import An external file ",
                triggered=self._onImportDrawing)
                
        self.__close_drawing_action = QtGui.QAction(QtGui.QIcon(':/images/close.png'),
                "&Close Drawing", self, shortcut=QtGui.QKeySequence.Open,
                statusTip="Close the current drawing",
                triggered=self._onCloseDrawing)

        self.__print_action = QtGui.QAction(QtGui.QIcon(':/images/print.png'),
                "&Print...", self, shortcut=QtGui.QKeySequence.Print,
                statusTip="Print the current drawing",
                triggered=self._onPrint)

        self.__undo_action = QtGui.QAction(QtGui.QIcon(':/images/undo.png'),
                "&Undo", self, shortcut=QtGui.QKeySequence.Undo,
                statusTip="Undo the last editing action", triggered=self._onUndo)

        self.__quit_action = QtGui.QAction("&Quit", self, shortcut="Ctrl+Q",
                statusTip="Quit the application", triggered=self.close)

        self.__about_action = QtGui.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self._onAbout)

        self.__about_qt_action = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtGui.qApp.aboutQt)
        
        self.__develop_action = QtGui.QAction("&Develop", self,
                statusTip="Open the develop windows",
                triggered=self._onDevelop)
                
    def _createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.__new_drawing_action)
        self.fileMenu.addAction(self.__open_drawing_action)
        self.fileMenu.addAction(self.__import_drawing_action)
        self.fileMenu.addAction(self.__close_drawing_action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.__print_action)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.__quit_action)

        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.__undo_action)

        self.viewMenu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.__about_action)
        self.helpMenu.addAction(self.__about_qt_action)
        
        self.develop = self.menuBar().addMenu("&Develop")
        self.develop.addAction(self.__develop_action)
        
    def _createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.__new_drawing_action)
        self.fileToolBar.addAction(self.__print_action)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.__undo_action)
        

    def _createStatusBar(self):
        self.statusBar().showMessage("Ready")
        

    def _createDockWindows(self):
        layer_dock = QtGui.QDockWidget("Layers", self)
        layer_dock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.__layer_list = QtGui.QListWidget(layer_dock)
        self.__layer_list.addItems((
            "Layer 0",
            "Just an layer name",
            "Another layer",
            "The last layer"))
        layer_dock.setWidget(self.__layer_list)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, layer_dock)
        self.viewMenu.addAction(layer_dock.toggleViewAction())
        
        # commandline
        command_dock = CmdlineDock("Command", self)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, command_dock)




