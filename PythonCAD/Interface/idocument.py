from PyQt4 import QtCore, QtGui
from Generic.Kernel.document import *
from Interface.LayerIntf.layerdock  import LayerDock
from Interface.cadscene             import CadScene
from Interface.cadview              import CadView
from Interface.LayerIntf.layertreeobject import LayerModel

class IDocument(QtGui.QMdiSubWindow):
    sequenceNumber = 1
    def __init__(self, document, cmdInf, parent):
        super(IDocument, self).__init__(parent)
        IDocument.sequenceNumber += 1
        self.__document=document
        self.__document.handledErrorEvent+=self._errorEvent
        self.__cmdInf=cmdInf
        self.__cadwindow=parent
        self.setWindowTitle(document.dbPath + '[*]')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        # Layer model used in dock and quick switcher
        self.__layer_model = LayerModel(self)
        # layer list
        self.__layer_dock = LayerDock(self,self.__document, self.__layer_model)
        self._scene = CadScene(document, parent=self)
        self.__cmdInf.commandLine.evaluatePressed+=self.scene.textInput
        self.__view = CadView(self._scene, self)
        # the graphics view is the main/central component
        innerWindows = QtGui.QMainWindow()
        innerWindows.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__layer_dock)
        innerWindows.setCentralWidget(self.__view)
        self.setWidget(innerWindows)
        #Inizialize scene
        self._scene.initDocumentEvents()
        self._scene.populateScene(document)
        self._scene.zoomWindows+=self.__view.zoomWindows
        self._scene.fireCommandlineFocus+=self.__cmdInf.commandLine.setFocus
        self._scene.fireKeyShortcut+=self.keyShortcut
        self._scene.fireKeyEvent+=self.keyEvent
        self._scene.fireWarning+=self.popUpWarning
        self._scene.fireCoords+=self.setStatusbarCoords
    @property
    def document(self):
        return self.__document
    @property
    def cmdInf(self):
        return self.__cmdInf
    @property
    def view(self):
        return self.__view
    @property
    def scene(self):
        return self._scene
    @property
    def application(self):
        """
        get the kernel application object
        """
        return self.__application
    @property
    def layerDock(self):
        """
        get the layer tree dockable window
        """
        return self.__layer_dock
    @property
    def fileName(self):
        """
            get the current file name
        """
        return self.document.dbPath
    def unDo(self):
        """
            perform undo on the active document
        """
        self.document.unDo()
        self.__layer_dock.RefreshStructure()

    def reDo(self):
        """
            perform redo on the active document
        """
        self.document.reDo()
        self.__layer_dock.RefreshStructure()

    def importExternalFormat(self, file):
        """
            import an external document
        """
        self.document.importExternalFormat(file)
    def renderCurrentScene(self, painter):
        """
            render the current scene for the printer
        """
        self.view.render(painter)


    def wWellEWvent(self, event):
        self.__view.scaleFactor=math.pow(2.0, -event.delta() / 240.0)
        self.__view.scaleView(self.__view.scaleFactor)

    def popUpWarning(self, msg):
        """
            popUp a warning mesage
        """
        ret = QtGui.QMessageBox.warning(self,"Warning",  msg)
        return

    def popUpInfo(self, msg):
        """
            popUp a Info mesage
        """
        ret = QtGui.QMessageBox.information(self,"Information",  msg)
        return

    def _errorEvent(self, err):
        """
            executed when the document rise an error
            the err is a dictionary like the one below
            _err={'object':, 'error':}
        """
        msgBox=QtGui.QMessageBox(self)
        msgBox.setIcon(QtGui.QMessageBox.Critical)
        msg="Error came from object %s"%(str(err['error']))
        dmsg=msg
        for _e in err['object'].getErrorList():
            dmsg=dmsg+"\n"+str(_e)
        msgBox.setWindowTitle("Error !!")
        msgBox.setText(msg)
        msgBox.setDetailedText(dmsg)
        msgBox.exec_()
        return

    def closeEvent(self, event):
        super(IDocument, self).closeEvent(event)
        # TODO: Verify if document is being closed (self.__application.closeDocument(path))
        self.__cadwindow.updateOpenFileList()

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------------------------------------MANAGE SCENE EVENTS
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    def setStatusbarCoords(self, x, y, status):
        #set statusbar coordinates when mouse move on the scene
        if status=="abs":
            self.__cadwindow.coordLabel.setText("X="+str("%.3f" % x)+"\n"+"Y="+str("%.3f" % y)) # "%.3f" %  sets the precision decimals to 3
        elif status=="rel":
            self.__cadwindow.coordLabel.setText("dx="+str("%.3f" % x)+"\n"+"dy="+str("%.3f" % y)) # "%.3f" %  sets the precision decimals to 3

    def keyEvent(self, event): #fire the key event in the scene to the commandline
        self.__cmdInf.commandLine._keyPress(event)


    def keyShortcut(self, command):
        self.__cadwindow.statusBar().showMessage(str(command))
        self.__cadwindow.callCommand(command)
