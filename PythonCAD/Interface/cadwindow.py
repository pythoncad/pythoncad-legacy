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

from Generic.application            import Application
from Interface.LayerIntf.layerdock  import LayerDock
from Interface.cadscene             import CadScene
from Interface.cadview              import CadView
from Ui_TestWindow                  import Ui_TestDialog
from customevent                    import testCmdLine
from Interface.CmdIntf.cmdintf      import CmdIntf
from Kernel.exception               import *  

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
    @property    
    def view(self):    
        return self.__view
    @property    
    def scene(self):    
        return self.__scene        
    @property
    def Application(self):
        """
        get the kernel application object
        """
        return self.__application
    @property
    def LayerDock(self):
        """
        get the layer tree dockable window
        """
        return self.__layer_dock      
        
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
        # Edit
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'undo', '&Undo', self._onUndo)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'redo', '&Redo', self._onRedo)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'move', '&Move', self._onMove)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'delete', '&Delete', self._onDelete)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'mirror', '&Mirror', self._onMirror)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'rotare', '&Rotare', self._onRotate)
        # Draw
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'point', '&Point', self._onPoint)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'segment', '&Segment', self._onSegment)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'rectangle', '&Rectangle', self._onRectangle)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'polyline', '&Polyline', self._onPolyline)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'arc', '&Arc', self._onArc)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'ellipse', '&Ellipse', self._onEllipse)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'poligon', '&Poligon', self._onPolygon)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'fillet', '&Fillet', self._onFillet)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'chamfer', '&Chamfer', self._onChamfer)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'biscect', '&Bisect', self._onBisect)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'text', '&Text', self._onText)
        # Help
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Help, 'about', '&About PyCAD', self._onAbout)
        # Debug
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
    
    def _onPoint(self):
        self.statusBar().showMessage("CMD:Point", 2000)
        self.callDocumentCommand('POINT')
        self.statusBar().showMessage("Ready", 2000)
        return    
    def _onSegment(self):
        self.statusBar().showMessage("CMD:Segment", 2000)
        self.callDocumentCommand('SEGMENT')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onArc(self):
        self.statusBar().showMessage("CMD:Arc", 2000)
        self.callDocumentCommand('ARC')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onEllipse(self):
        self.statusBar().showMessage("CMD:Ellipse", 2000)
        self.callDocumentCommand('ELLIPSE')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onRectangle(self):
        self.statusBar().showMessage("CMD:Rectangle", 2000)
        self.callDocumentCommand('RECTANGLE')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onPolygon(self):
        self.statusBar().showMessage("CMD:Polygon", 2000)
        self.callDocumentCommand('POLYGON')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onPolyline(self):
        self.statusBar().showMessage("CMD:Polyline", 2000)
        self.callDocumentCommand('POLYLINE')
        self.statusBar().showMessage("Ready", 2000)
        return
    
    def _onFillet(self):
        self.statusBar().showMessage("CMD:Fillet", 2000)
        self.callDocumentCommand('FILLET')
        self.statusBar().showMessage("Ready", 2000)
        return
        
    def _onChamfer(self):
        self.statusBar().showMessage("CMD:Chamfer", 2000)
        self.callDocumentCommand('CHAMFER')
        self.statusBar().showMessage("Ready", 2000)
        return
            
    def _onBisect(self):
        self.statusBar().showMessage("CMD:Bisect", 2000)
        self.callDocumentCommand('BISECTOR')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onText(self):
        self.statusBar().showMessage("CMD:Bisect", 2000)
        self.callDocumentCommand('TEXT')
        self.statusBar().showMessage("Ready", 2000)
        return      
    # Edit
    def _onMove(self):
        self.statusBar().showMessage("CMD:Move", 2000)
        self.callDocumentCommand('MOVE')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onDelete(self):
        self.statusBar().showMessage("CMD:Delete", 2000)
        self.callDocumentCommand('DELETE')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onMirror(self):
        self.statusBar().showMessage("CMD:Mirror", 2000)
        self.callDocumentCommand('MIRROR')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onRotate(self):
        self.statusBar().showMessage("CMD:Rotate", 2000)
        self.callDocumentCommand('ROTATE')
        self.statusBar().showMessage("Ready", 2000)
        return
    
    def _onPrint(self):
        printer=QtGui.QPrinter()
        printDialog=QtGui.QPrintDialog(printer)
        if (printDialog.exec_() == QtGui.QDialog.Accepted): 
            painter=QtGui.QPainter(printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing);
            self.__scene.render(painter)  
        self.statusBar().showMessage("Ready", 2000)
        return
        
    def _onUndo(self):
        try:
            self.__scene.undo()
        except UndoDb:
            PyCadApp.critical("Unable To Perform Undo")
        self.statusBar().showMessage("Ready", 2000)
        return
        
    def _onRedo(self):
        try:
            self.__scene.redo()
        except UndoDb:
            PyCadApp.critical("Unable To Perform Redo")
        self.statusBar().showMessage("Ready", 2000)
        
    def callDocumentCommand(self, commandName):
        try:
            from Interface.pycadapp import PyCadApp
            pointCmd=PyCadApp.Application().getCommand(commandName)
            self.__cmd_intf.evaluateInnerCommand(pointCmd)
        except EntityMissing:
            PyCadApp.critical("You need to have an active document to perform this command")
    def _onAbout(self):
        QtGui.QMessageBox.about(self, "About PythonCAD",
                "<b>PythonCAD</b> is a 2D CAD system.")
        return
        
    def _onDebug(self):
        """
            debug dialog
        """
        from Interface.pycadapp import PyCadApp
        if PyCadApp.ActiveDocument():
            TestDialog = QtGui.QDialog()
            ui = Ui_TestDialog()
            ui.setupUi(TestDialog)
            testCmdLine(ui,self.__scene )
            TestDialog.show()
            TestDialog.exec_()
        else:
            PyCadApp.critical("You must have a document open before use this function !!")
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
        




