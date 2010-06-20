from PyQt4 import QtCore, QtGui
from Generic.Kernel.document import *
from Interface.LayerIntf.layerdock  import LayerDock
from Interface.cadscene             import CadScene
from Interface.cadview              import CadView

class IDocument(QtGui.QMdiSubWindow):
    sequenceNumber = 1
    def __init__(self, document, cmdInf):
        super(IDocument, self).__init__()
        IDocument.sequenceNumber += 1
        self.__document=document
        self.__cmdInf=cmdInf
        self.setWindowTitle(document.dbPath + '[*]')
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.isUntitled = True
        # layer list
        self.__layer_dock = LayerDock(self)
        self.__scene = CadScene(document)
        self.__scene.pyCadScenePressEvent+=self.__cmdInf.evaluateMouseImput
        self.__scene.pyCadSceneApply+=self.__cmdInf.applyCommand
        self.__view = CadView(self.__scene, self)
        # the graphics view is the main/central component
        innerWindows = QtGui.QMainWindow()
        innerWindows.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.__layer_dock)
        innerWindows.setCentralWidget(self.__view)
        self.setWidget(innerWindows)
        #Inizialize scene
        self.__scene.initDocumentEvents()
        self.__scene.populateScene(document)

    @property
    def document(self):
        return self.__document
    @property    
    def view(self):    
        return self.__view
    @property    
    def scene(self):    
        return self.__scene        
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
        
    def unDo(self):
        """
            perform undo on the active document
        """
        self.document.unDo()
        
    def reDo(self):
        """
            perform redo on the active document
        """
        self.document.reDo()
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
    @property
    def fileName(self):
        """
            get the current file name 
        """
        return self.document.dbPath
        
        
    #dovrebbe memorizzare gli ultimi file aperti
    #def strippedName(self, fullFileName):
    #    return QtCore.QFileInfo(fullFileName).fileName()
