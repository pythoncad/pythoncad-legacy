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
from Interface.idocument            import IDocument
from Interface.CmdIntf.cmdintf      import CmdIntf

from Kernel.exception               import *  

class CadWindowMdi(QtGui.QMainWindow):
    def __init__(self):
        super(CadWindowMdi, self).__init__()
        self.mdiArea = QtGui.QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)
        self.mdiArea.subWindowActivated.connect(self.subWindowActivatedEvent)

        self.readSettings() #make some studis on this 
        self.setWindowTitle("PythonCad")
        self.setUnifiedTitleAndToolBarOnMac(True)
        #pythoncad kernel
        self.__application = Application()
        self.__cmd_intf = CmdIntf(self)
        self.__cmd_intf.FunctionHandler.commandExecuted+=self.commandExecuted
        # create all dock windows
        self._createDockWindows()
        # create status bar
        self._createStatusBar()
        self.setUnifiedTitleAndToolBarOnMac(True)
        self._registerCommands()
        self.updateMenus()
        self.statusBar().showMessage("Ready")
        return
    @property
    def scene(self):
        if self.mdiArea.activeSubWindow():
            return self.mdiArea.activeSubWindow().scene
        
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
        
    def _createStatusBar(self):
        '''
        Creates the statusbar object.
        '''
        self.statusBar().showMessage("Ready")
        return    
        
    def commandExecuted(self):
        self.statusBar().showMessage("Ready")
        
    def _createDockWindows(self):
        '''
        Creates all dockable windows for the application
        '''
        # commandline
        command_dock = self.__cmd_intf.Commandline
        # if the commandline exists, add it
        if not command_dock is None:
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, command_dock)
        return    
        
    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            
    def subWindowActivatedEvent(self):
        """
            sub windows activation
        """
        self.updateMenus()
        self.resetCommand()
        if self.mdiArea.activeSubWindow():
            self.__application.setActiveDocument(self.mdiArea.activeSubWindow().document)   

    def resetCommand(self):    
        """
            Resect the active command
        """
        self.__cmd_intf.resetCommand()
        
        
    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        #File
        self.__cmd_intf.setVisible('import', hasMdiChild)
        self.__cmd_intf.setVisible('saveas', hasMdiChild)
        self.__cmd_intf.setVisible('close', hasMdiChild)
        self.__cmd_intf.setVisible('print', hasMdiChild)
        #Edit
        self.__cmd_intf.setVisible('undo', hasMdiChild)
        self.__cmd_intf.setVisible('redo', hasMdiChild)
        self.__cmd_intf.setVisible('move', hasMdiChild)
        self.__cmd_intf.setVisible('delete', hasMdiChild)
        self.__cmd_intf.setVisible('mirror', hasMdiChild)
        self.__cmd_intf.setVisible('rotare', hasMdiChild)
        #Draw
        self.__cmd_intf.setVisible('point', hasMdiChild)
        self.__cmd_intf.setVisible('segment', hasMdiChild)
        self.__cmd_intf.setVisible('rectangle', hasMdiChild)
        self.__cmd_intf.setVisible('polyline', hasMdiChild)
        self.__cmd_intf.setVisible('arc', hasMdiChild)
        self.__cmd_intf.setVisible('ellipse', hasMdiChild)
        self.__cmd_intf.setVisible('poligon', hasMdiChild)
        self.__cmd_intf.setVisible('fillet', hasMdiChild)
        self.__cmd_intf.setVisible('chamfer', hasMdiChild)
        self.__cmd_intf.setVisible('biscect', hasMdiChild)
        self.__cmd_intf.setVisible('text', hasMdiChild)
        #window
        self.__cmd_intf.setVisible('tile', hasMdiChild)
        self.__cmd_intf.setVisible('cascade', hasMdiChild)
        self.__cmd_intf.setVisible('next', hasMdiChild)
        self.__cmd_intf.setVisible('previous', hasMdiChild)
        
    
        #hasSelection = (self.activeMdiChild() is not None and
        #                self.activeMdiChild().textCursor().hasSelection())
        #self.cutAct.setEnabled(hasSelection)
        #self.copyAct.setEnabled(hasSelection)
        
    def subWindowActivated(self, activeIDocument):    
        """
            event fired on change of the active document
        """
        print "document change"
        
    def createMdiChild(self, file=None):
        """
            Create new IDocument 
        """
        if file:
            newDoc=self.__application.openDocument(file)
        else:
            newDoc=self.__application.newDocument()
        child = IDocument(newDoc,self.__cmd_intf)
        self.mdiArea.addSubWindow(child)

        #child.copyAvailable.connect(self.cutAct.setEnabled)
        #child.copyAvailable.connect(self.copyAct.setEnabled)
        return child

    def _registerCommands(self):
        '''
        Register all commands that are handed by this object
        '''
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'new', '&New Drawing', self._onNewDrawing)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'open', '&Open Drawing...', self._onOpenDrawing)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'import', '&Import Drawing...', self._onImportDrawing)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'saveas', '&Save In A Different location...', self._onSaveAsDrawing)
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
        # window
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'tile', '&Tile', self.mdiArea.tileSubWindows)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'cascade', '&Cascade', self.mdiArea.cascadeSubWindows)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'next', 'Ne&xt', self.mdiArea.activateNextSubWindow)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'previous', 'Pre&vious', self.mdiArea.activatePreviousSubWindow)

        
        # Help
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Help, 'about', '&About PyCAD', self._onAbout)
        return
        
    def _onNewDrawing(self):
        '''
        Create a new drawing 
        '''
        child = self.createMdiChild()
        child.show()
        return

    def _onOpenDrawing(self):
        # ask the user to select an existing drawing
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Open Drawing", "/home", "Drawings (*.pdr)");
        # open a document and load the drawing
        if drawing != None:
            child = self.createMdiChild(drawing)
            child.show()            
        return
    
    def _onImportDrawing(self):
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Import Drawing", "/home", "Dxf (*.dxf)");
        # open a document and load the drawing
        if drawing != None:
            self.mdiArea.activeSubWindow().importExternalFormat(drawing)
        return
        
    def _onSaveAsDrawing(self):
        drawing = QtGui.QFileDialog.getSaveFileName(self, "Save As Drawing", "/home", "Drawings (*.pdr)");
        self.__application.saveAs(drawing)
            
    def _onCloseDrawing(self):
        path=self.mdiArea.activeSubWindow().fileName
        self.__application.closeDocument(path)
        self.mdiArea.closeActiveSubWindow()
        return
    
    def _onPoint(self):
        self.statusBar().showMessage("CMD:Point", 2000)
        self.callDocumentCommand('POINT')
        return    
    def _onSegment(self):
        self.statusBar().showMessage("CMD:Segment", 2000)
        self.callDocumentCommand('SEGMENT')
        return
    def _onArc(self):
        self.statusBar().showMessage("CMD:Arc", 2000)
        self.callDocumentCommand('ARC')
        return
    def _onEllipse(self):
        self.statusBar().showMessage("CMD:Ellipse", 2000)
        self.callDocumentCommand('ELLIPSE')
        return
    def _onRectangle(self):
        self.statusBar().showMessage("CMD:Rectangle", 2000)
        self.callDocumentCommand('RECTANGLE')
        return
    def _onPolygon(self):
        self.statusBar().showMessage("CMD:Polygon", 2000)
        self.callDocumentCommand('POLYGON')
        return
    def _onPolyline(self):
        self.statusBar().showMessage("CMD:Polyline", 2000)
        self.callDocumentCommand('POLYLINE')
        return
    
    def _onFillet(self):
        self.statusBar().showMessage("CMD:Fillet", 2000)
        self.callDocumentCommand('FILLET')
        return
        
    def _onChamfer(self):
        self.statusBar().showMessage("CMD:Chamfer", 2000)
        self.callDocumentCommand('CHAMFER')
        return
            
    def _onBisect(self):
        self.statusBar().showMessage("CMD:Bisect", 2000)
        self.callDocumentCommand('BISECTOR')
        return
    def _onText(self):
        self.statusBar().showMessage("CMD:Bisect", 2000)
        self.callDocumentCommand('TEXT')
        return      
    # Edit
    def _onMove(self):
        self.statusBar().showMessage("CMD:Move", 2000)
        self.callDocumentCommand('MOVE')
        return
    def _onDelete(self):
        self.statusBar().showMessage("CMD:Delete", 2000)
        self.callDocumentCommand('DELETE')
        self.statusBar().showMessage("Ready", 2000)
        return
    def _onMirror(self):
        self.statusBar().showMessage("CMD:Mirror", 2000)
        self.callDocumentCommand('MIRROR')
        return
    def _onRotate(self):
        self.statusBar().showMessage("CMD:Rotate", 2000)
        self.callDocumentCommand('ROTATE')
        return
    
    def _onPrint(self):
        printer=QtGui.QPrinter()
        printDialog=QtGui.QPrintDialog(printer)
        if (printDialog.exec_() == QtGui.QDialog.Accepted): 
            painter=QtGui.QPainter(printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing);
            #self.__scene.render(painter) 
            self.mdiArea.activeSubWindow().renderCurrentScene(painter) 
        self.statusBar().showMessage("Ready", 2000)
        return
        
    def _onUndo(self):
        try:
           self.mdiArea.activeSubWindow().unDo() 
        except UndoDb:
            self.critical("Unable To Perform Undo")
        self.statusBar().showMessage("Ready", 2000)
        return
        
    def _onRedo(self):
        try:
            self.mdiArea.activeSubWindow().redo()
        except UndoDb:
            PyCadApp.critical("Unable To Perform Redo")
        self.statusBar().showMessage("Ready", 2000)
        
    def _onAbout(self):
        QtGui.QMessageBox.about(self, "About PythonCAD",
                "<b>PythonCAD</b> is a 2D CAD system.")
        return
        
    def callDocumentCommand(self, commandName):
        try:
            pointCmd=self.__application.getCommand(commandName)
            self.__cmd_intf.evaluateInnerCommand(pointCmd)
        except EntityMissing:
            self.critical("You need to have an active document to perform this command")
            
    @staticmethod
    def critical(text):
        '''
        Shows an critical message dialog
        '''
        dlg = QtGui.QMessageBox()
        dlg.setText(text)
        dlg.setIcon(QtGui.QMessageBox.Critical)
        dlg.exec_()
        return

    def readSettings(self):
        settings = QtCore.QSettings('Trolltech', 'MDI Example')
        #settings = QtCore.QSettings('PythonCAD', 'MDI Settings')
        pos = settings.value('pos', QtCore.QPoint(200, 200))
        size = settings.value('size', QtCore.QSize(400, 400))
        #self.move(pos)
        #self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings('Trolltech', 'MDI Example')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None

    def switchLayoutDirection(self):
        if self.layoutDirection() == QtCore.Qt.LeftToRight:
            QtGui.qApp.setLayoutDirection(QtCore.Qt.RightToLeft)
        else:
            QtGui.qApp.setLayoutDirection(QtCore.Qt.LeftToRight)
        
    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)


