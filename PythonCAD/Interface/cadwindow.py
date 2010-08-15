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

import os
import sys

from PyQt4 import QtCore, QtGui

import cadwindow_rc

from Generic.application            import Application

from Interface.LayerIntf.layerdock  import LayerDock
from Interface.cadscene             import CadScene
from Interface.cadview              import CadView
from Interface.idocument            import IDocument
from Interface.CmdIntf.cmdintf      import CmdIntf
from Interface.Entity.base          import BaseEntity
from Interface.Command.icommand     import ICommand
from Kernel.exception               import *  
from Kernel.initsetting             import SNAP_POINT_ARRAY, ACTIVE_SNAP_POINT

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
        qIcon=self._getIcon('pythoncad')
        if qIcon:
            self.setWindowIcon(qIcon)
        self.setUnifiedTitleAndToolBarOnMac(True)
        #pythoncad kernel
        self.__application = Application()
        self.__cmd_intf = CmdIntf(self)
        #self.__cmd_intf.FunctionHandler.commandExecuted+=self.commandExecuted
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
    def view(self):
        if self.mdiArea.activeSubWindow():
            return self.mdiArea.activeSubWindow().view 
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
        self.resetCommand()
        
    def _createDockWindows(self):
        '''
            Creates all dockable windows for the application
        '''
        # commandline
        command_dock = self.__cmd_intf.commandLine
        # if the commandline exists, add it
        if not command_dock is None:
            self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, command_dock)
        return    
    
    def closeEvent(self, event):
        """
            manage close event
        """
        self.mdiArea.closeAllSubWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
            
    def subWindowActivatedEvent(self):
        """
            Sub windows activation
        """
        if self.mdiArea.activeSubWindow():
            self.resetCommand()
            self.__application.setActiveDocument(self.mdiArea.activeSubWindow().document)   
        self.updateMenus()
        
    def resetCommand(self):    
        """
            Resect the active command
        """
        self.__cmd_intf.resetCommand()
        self.statusBar().showMessage("Ready")
        
    def updateMenus(self):
        """
            update menu status
        """
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
        self.__cmd_intf.setVisible('rotate', hasMdiChild)
        #Draw
        self.__cmd_intf.setVisible('point', hasMdiChild)
        self.__cmd_intf.setVisible('segment', hasMdiChild)
        self.__cmd_intf.setVisible('rectangle', hasMdiChild)
        self.__cmd_intf.setVisible('polyline', hasMdiChild)
        self.__cmd_intf.setVisible('arc', hasMdiChild)
        self.__cmd_intf.setVisible('ellipse', hasMdiChild)
        self.__cmd_intf.setVisible('polygon', hasMdiChild)
        self.__cmd_intf.setVisible('fillet', hasMdiChild)
        self.__cmd_intf.setVisible('chamfer', hasMdiChild)
        self.__cmd_intf.setVisible('bisect', hasMdiChild)
        self.__cmd_intf.setVisible('text', hasMdiChild)
        #View
        self.__cmd_intf.setVisible('fit', hasMdiChild)
        self.__cmd_intf.setVisible('zoomwindow', hasMdiChild)
        self.__cmd_intf.setVisible('zoomitem', hasMdiChild)
        #snap
        self.__cmd_intf.setVisible('autosnap', hasMdiChild)
        self.__cmd_intf.setVisible('endsnap', hasMdiChild)
        self.__cmd_intf.setVisible('middlesnap', hasMdiChild)
        self.__cmd_intf.setVisible('centersnap', hasMdiChild)
        self.__cmd_intf.setVisible('ortosnap', hasMdiChild)
        self.__cmd_intf.setVisible('tangentsnap', hasMdiChild)
        self.__cmd_intf.setVisible('quadrantsnap', hasMdiChild)
        self.__cmd_intf.setVisible('originsnap', hasMdiChild)
        #window
        self.__cmd_intf.setVisible('tile', hasMdiChild)
        self.__cmd_intf.setVisible('cascade', hasMdiChild)
        self.__cmd_intf.setVisible('next', hasMdiChild)
        self.__cmd_intf.setVisible('previous', hasMdiChild)
        #hasSelection = (self.activeMdiChild() is not None and
        #                self.activeMdiChild().textCursor().hasSelection())
        #self.cutAct.setEnabled(hasSelection)
        #self.copyAct.setEnabled(hasSelection)
        
    def createMdiChild(self, file=None):
        """
            Create new IDocument 
        """
        if file:
            newDoc=self.__application.openDocument(file)
        else:
            newDoc=self.__application.newDocument()
        for mdiwind in self.mdiArea.subWindowList():
            if mdiwind._IDocument__document.dbPath==file:
                child=mdiwind
                break
        else:
            child = IDocument(newDoc,self.__cmd_intf, self)
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
        #
        # Create recentFile structure
        #
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, '-')
        
        i=0
        for file in self.Application.getRecentFiles:
            fileName=self.strippedName(file)
            self.__cmd_intf.registerCommand(self.__cmd_intf.Category.File, 'file_'+str(i), fileName, self._onOpenRecent)    
            i+=1
        #
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
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Edit, 'rotate', '&Rotare', self._onRotate)
        # Draw
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'point', '&Point', self._onPoint)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'segment', '&Segment', self._onSegment)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'rectangle', '&Rectangle', self._onRectangle)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'polyline', '&Polyline', self._onPolyline)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'arc', '&Arc', self._onArc)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'ellipse', '&Ellipse', self._onEllipse)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'polygon', '&polygon', self._onPolygon)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'fillet', '&Fillet', self._onFillet)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'chamfer', '&Chamfer', self._onChamfer)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'bisect', '&Bisect', self._onBisect)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, '-')
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Draw, 'text', '&Text', self._onText)
        # View
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.View, 'fit', '&Fit', self._onFit)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.View, 'zoomwindow', 'Zoom&Window', self._onZoomWindow)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.View, 'zoomitem', 'Zoom&Item',self._onCenterItem)
        # Snap
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'autosnap', 'Automatic Snap', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'endsnap', 'End', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'middlesnap', 'Middle', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'centersnap', 'Center', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'ortosnap', 'Ortogonal', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'tangentsnap', 'Tangent', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'quadrantsnap', 'Quadrant', self._onSnapCommand)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Snap, 'originsnap', 'Origin', self._onSnapCommand)
        # window
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'tile', '&Tile', self.mdiArea.tileSubWindows)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'cascade', '&Cascade', self.mdiArea.cascadeSubWindows)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'next', 'Ne&xt', self.mdiArea.activateNextSubWindow)
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Windows, 'previous', 'Pre&vious', self.mdiArea.activatePreviousSubWindow)
        # Help
        self.__cmd_intf.registerCommand(self.__cmd_intf.Category.Help, 'about', '&About PyCAD', self._onAbout)
        return
        
    def updateRecentFileList(self):
        """
            update the menu recent file list
        """
        i=0
        for file in self.Application.getRecentFiles:
            fileName=self.strippedName(file)
            self.__cmd_intf.updateText('file_'+str(i), fileName)
            i+=1
            
    def strippedName(self, fullFileName):
        """
            get only the name of the filePath
        """
        return QtCore.QFileInfo(fullFileName).fileName()    
        
    def _onNewDrawing(self):
        '''
            Create a new drawing 
        '''
        child = self.createMdiChild()
        child.show()
        self.updateRecentFileList()
        return
        
    def _onOpenDrawing(self):
        # ask the user to select an existing drawing
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Open Drawing", "/home", "Drawings (*.pdr)");
        # open a document and load the drawing
        if len(drawing)>0:
            child = self.createMdiChild(drawing)
            child.show() 
            self.updateRecentFileList()           
        return
    
    def _onImportDrawing(self):
        drawing = QtGui.QFileDialog.getOpenFileName(self, "Import Drawing", "/home", "Dxf (*.dxf)");
        # open a document and load the drawing
        if len(drawing)>0:
            self.mdiArea.activeSubWindow().importExternalFormat(drawing)
        return
        
    def _onOpenRecent(self):
        """
            on open recent file
        """
        #FIXME: if in the command line we insert file_1 or file_2
        #here we get en error action dose not have command attributes
        # action is en edit command not an action and have an empty value
        action = self.sender()
        if action:
            spool, index=action.command.split('_')
            fileName=self.Application.getRecentFiles[int(index)]
            if len(fileName)>0:
                child = self.createMdiChild(fileName)
                child.show() 
                self.updateRecentFileList()
        return
        
    def _onSaveAsDrawing(self):
        drawing = QtGui.QFileDialog.getSaveFileName(self, "Save As Drawing", "/home", "Drawings (*.pdr)");
        if len(drawing)>0:
            self.__application.saveAs(drawing)
            
    def _onCloseDrawing(self):
        path=self.mdiArea.activeSubWindow().fileName
        self.__application.closeDocument(path)
        self.mdiArea.closeActiveSubWindow()
        return
    
    def _onPoint(self):
        self.statusBar().showMessage("CMD:Point")
        self.callDocumentCommand('POINT')
        return    
    def _onSegment(self):
        self.statusBar().showMessage("CMD:Segment")
        self.callDocumentCommand('SEGMENT')
        return
    def _onArc(self):
        self.statusBar().showMessage("CMD:Arc")
        self.callDocumentCommand('ARC')
        return
    def _onEllipse(self):
        self.statusBar().showMessage("CMD:Ellipse")
        self.callDocumentCommand('ELLIPSE')
        return
    def _onRectangle(self):
        self.statusBar().showMessage("CMD:Rectangle")
        self.callDocumentCommand('RECTANGLE')
        return
    def _onPolygon(self):
        self.statusBar().showMessage("CMD:Polygon")
        self.callDocumentCommand('POLYGON')
        return
    def _onPolyline(self):
        self.statusBar().showMessage("CMD:Polyline")
        self.callDocumentCommand('POLYLINE')
        return
    
    def _onFillet(self):
        self.statusBar().showMessage("CMD:Fillet")
        self.callDocumentCommand('FILLET')
        return
        
    def _onChamfer(self):
        self.statusBar().showMessage("CMD:Chamfer")
        self.callDocumentCommand('CHAMFER')
        return
            
    def _onBisect(self):
        self.statusBar().showMessage("CMD:Bisect")
        self.callDocumentCommand('BISECTOR')
        return
    def _onText(self):
        self.statusBar().showMessage("CMD:Bisect")
        self.callDocumentCommand('TEXT')
        return      
    # Edit
    def _onMove(self):
        self.statusBar().showMessage("CMD:Move")
        self.callDocumentCommand('MOVE')
        return
    def _onDelete(self):
        self.statusBar().showMessage("CMD:Delete")
        self.callDocumentCommand('DELETE')
        self.statusBar().showMessage("Ready")
        return
    def _onMirror(self):
        self.statusBar().showMessage("CMD:Mirror")
        self.callDocumentCommand('MIRROR')
        return
    def _onRotate(self):
        self.statusBar().showMessage("CMD:Rotate")
        self.callDocumentCommand('ROTATE')
        return
    # View
    def _onFit(self):
        self.view.fit()
        
    def _onZoomWindow(self):
        self.statusBar().showMessage("CMD:ZoomWindow")
        self.scene._cmdZoomWindow=True
    
    def _onCenterItem(self):
        self.view.centerOnSelection()
    # Snap
    def _onSnapCommand(self):
        """
            On snep Command action
        """
        action = self.sender()
        if action:
            if action.command=="autosnap":
                self.scene.forceSnap= SNAP_POINT_ARRAY["ALL"] 
            elif action.command=="endsnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["END"] 
            elif action.command=="middlesnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["MID"] 
            elif action.command=="centersnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["CENTER"] 
            elif action.command=="ortosnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["ORTO"] 
            elif action.command=="tangentsnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["TANGENT"] 
            elif action.command=="quadrantsnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["QUADRANT"] 
            elif action.command=="originsnap":
                self.scene.forceSnap=SNAP_POINT_ARRAY["ORIG"] 
            else:
                self.scene.forceSnap=SNAP_POINT_ARRAY["ALL"] 
                
        
    def _onPrint(self):
#       printer.setPaperSize(QPrinter.A4);
        printer=QtGui.QPrinter()
        printDialog=QtGui.QPrintDialog(printer)
        if (printDialog.exec_() == QtGui.QDialog.Accepted): 
            painter=QtGui.QPainter()
            painter.begin(printer)
            painter.setRenderHint(QtGui.QPainter.Antialiasing);
            #self.mdiArea.activeSubWindow().scene.render(painter)
            self.mdiArea.activeSubWindow().view.render(painter)
            painter.end()
        self.statusBar().showMessage("Ready")
        return
        
    def _onUndo(self):
        try:
           self.mdiArea.activeSubWindow().unDo() 
        except UndoDbExc:
            self.critical("Unable To Perform Undo")
        self.statusBar().showMessage("Ready")
        return
        
    def _onRedo(self):
        try:
            self.mdiArea.activeSubWindow().reDo()
        except UndoDbExc:
            self.critical("Unable To Perform Redo")
        self.statusBar().showMessage("Ready")
        
    def _onAbout(self):
        QtGui.QMessageBox.about(self, "About PythonCAD",
                """<b>PythonCAD</b> is a CAD package written, surprisingly enough, in Python using the PyQt4 interface.<p>
                   The PythonCAD project aims to produce a scriptable, open-source,
                   easy to use CAD package for any Python/PyQt supported Platforms
                   <p>
                   This is an Alfa Release For The new R38 Vesion <b>(R38.0.0.2)<b><P>
                   <p>
                   <a href="http://sourceforge.net/projects/pythoncad/">PythonCAD Web Site On Sourceforge</a>""")
        return
        
    def callDocumentCommand(self, commandName):
        try:
            self.scene.activeKernelCommand=self.__application.getCommand(commandName)
            self.scene.activeICommand=ICommand(self.scene)
            self.scene.activeICommand.updateInput+=self.updateInput
            self.updateInput(self.scene.activeKernelCommand.activeMessage)
        except EntityMissing:
            self.critical("You need to have an active document to perform this command")

    def updateInput(self, message):
            self.__cmd_intf.commandLine.printMsg(message)
            self.statusBar().showMessage(message)

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
        #settings = QtCore.QSettings('PythonCAD', 'MDI Settings')
        #pos = settings.value('pos', QtCore.QPoint(200, 200))
        #size = settings.value('size', QtCore.QSize(400, 400))
        #self.move(pos)
        #self.resize(size)
        pass

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


    def _getIcon(self, cmd):
        '''
        Create an QIcon object based on the command name.
        The name of the icon is ':/images/' + cmd + '.png'.
        If the cmd = 'Open', the name of the icon is ':/images/Open.png'.
        '''
        icon_name = cmd + '.png'
        icon_path = os.path.join(os.path.join(os.getcwd(), 'icons'), icon_name)
        # check if icon exist
        if os.path.exists(icon_path):
            icon = QtGui.QIcon(icon_path)
            return icon
        # icon not found, don't use an icon, return None
        return None

    def keyPressEvent(self, event):
        if event.key()==QtCore.Qt.Key_Escape:
            self.resetCommand()
            
        super(CadWindowMdi, self).keyPressEvent(event)
