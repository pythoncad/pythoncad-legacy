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

from Generic.Kernel.application     import Application
from Interface.LayerIntf.layerdock  import LayerDock
from Interface.cadscene             import CadScene
from Interface.cadview              import CadView
from Ui_TestWindow                  import Ui_TestDialog
from customevent                    import testCmdLine
from Interface.CmdIntf.cmdintf      import CmdIntf


class CadWindow(QtGui.QMainWindow):
    '''
    Main application window, contains the graphics view and user interface controls (menu, toolbars, palettes and commandline).
    '''
    
    def __init__(self):
        '''
        Create all user interface components
        '''
        super(CadWindow, self).__init__()
        # application from the kernel
        self.__application = Application()
        # graphics scene and view
        self.__scene = CadScene()
        self.__view = CadView(self.__scene, self)
        # the graphics view is the main/central component
        self.setCentralWidget(self.__view)
        # layer tree dockable window
        self.__layer_dock = None
        # create user input interface components
        # all user interface is done by commands
        # the menu-bar, tool-bars and palettes are created by the CmdIntf
        self.__cmd_intf = CmdIntf(self)
        # create all dock windows
        self._createDockWindows()
        # create status bar
        self._createStatusBar()
        # initial window title
        self.setWindowTitle("PythonCAD [empty]")
        # show the menu and title in a correct way on the mac
        self.setUnifiedTitleAndToolBarOnMac(True)
        # register commands that are handled by the main window
        self._registerCommands()
        return
        
        
    def _getApplication(self):
        return self.__application
    
    Application = property(_getApplication, None, None, 'get the kernel application object')
    
    def _getLayerDock(self):
        return self.__layer_dock
    
    LayerDock = property(_getLayerDock, None, None, 'get the layer tree dockable window')
        
        
    def _registerCommands(self):
        '''
        Register all commands that are handed by this object
        '''
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'new', '&New Drawing', self._onNewDrawing)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'open', '&Open Drawing...', self._onOpenDrawing)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'import', '&Import Drawing...', self._onImportDrawing)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'SaveAs', '&Save In A Different location...', self._onSaveAsDrawing)
        # separator
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'close', '&Close', self._onCloseDrawing)
        # separator
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'print', '&Print', self._onPrint)
        # separator
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'quit', '&Quit PyCAD', self.close)
        
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'undo', '&Undo', self._onUndo)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Help, 'about', '&About PyCAD', self._onAbout)
        
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Debug, 'Debug', '&Debug PyCAD', self._onDebug)
        
        return
        

    def _onNewDrawing(self):
        '''
        Create a new drawing 
        '''
        self.__scene.newDocument()
        return
    

    def _onOpenDrawing(self):
        # ask the user to select an existing drawing
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Open Drawing", "/home", "Drawings (*.pdr)");
        # open a document and load the drawing
        if drawing != None:
            self.__scene.openDocument(drawing)
        return
    
    def _onImportDrawing(self):
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Import Drawing", "/home", "Dxf (*.dxf)");
        # open a document and load the drawing
        if drawing != None:
            self.__scene.importDocument(drawing)
        return
    def _onSaveAsDrawing(self):
        drawing = QtGui.QFileDialog.getSaveFileName(self, "Save As Drawing", "/home", "Drawings (*.pdr)");
        self.__scene.saveAs(drawing)
            
    def _onCloseDrawing(self):
        self.__scene.closeDocument()
        return
    
        
    def _onPrint(self):
        # TODO: printing
        self.statusBar().showMessage("Ready", 2000)
        return

        
    def _onUndo(self):
        # TODO: printing
        self.statusBar().showMessage("Ready", 2000)
        return


    def _onAbout(self):
        QtGui.QMessageBox.about(self, "About PythonCAD",
                "<b>PythonCAD</b> is a 2D CAD system.")
        return
        
    def _onDebug(self):
        """
            debug dialog
        """
    
        TestDialog = QtGui.QDialog()
        ui = Ui_TestDialog()
        ui.setupUi(TestDialog)
        testCmdLine(ui,self.__scene )
        TestDialog.show()
        TestDialog.exec_()
   
        return    

    def _createStatusBar(self):
        '''
        Creates the statusbar object.
        '''
        self.statusBar().showMessage("Ready")
        return
        

    def _createDockWindows(self):
        '''
        Creates all dockable windows for the application
        '''
        # layer list
        self.__layer_dock = LayerDock(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__layer_dock)
        
        # commandline
        command_dock = self.__cmd_intf.Commandline
        # if the commandline exists, add it
        if not command_dock is None:
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, command_dock)
            
        return
        
        




