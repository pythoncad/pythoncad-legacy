from PyQt4 import QtCore, QtGui
from Generic.Kernel.document     import *
from Generic.Kernel.exception    import *
from Generic.Kernel.Entity.point    import Point
from Generic.Kernel.Command.basecommand import BaseCommand

class testCmdLine(object):
    def __init__(self, dialog, scene):
        self.dialog=dialog
        self.scene=scene
        self._addCustomEvent()
        self._inizializeCommand()
        self.activeCommand=None

    def _inizializeCommand(self):    
        """
            inizialize all the command class
        """
        self.__command={}
        self.__applicationCommand={}
        self.__pyCadApplication=self.scene.getApplication()
        # Application Command
        self.__applicationCommand['Documents']=GetDocuments(self.__pyCadApplication.getDocuments(), self.outputMsg)
        self.__applicationCommand['CreateStyle']=CreateStyle(self.__pyCadApplication.getActiveDocument())
        self.__applicationCommand['SetActiveDoc']=SetActiveDoc(self.__pyCadApplication)
        self.__applicationCommand['GetActiveDoc']=GetActiveDoc(self.__pyCadApplication, self.outputMsg)
        self.__applicationCommand['GetEnts']=GetEnts(self.__pyCadApplication.getActiveDocument(), self.outputMsg)
        #self.__applicationCommand['Test']=self.featureTest
        #self.__applicationCommand['ETest']=self.easyTest
        # Document Commandf
        for command in self.__pyCadApplication.getCommandList():
            self.__applicationCommand[command]=self.__pyCadApplication.getCommand(command)
        self.__applicationCommand['?']=PrintHelp(self.__applicationCommand, self.outputMsg)    
    def _addCustomEvent(self):
        """
            add custom event at the user interface
        """
        QtCore.QObject.connect(self.dialog.ImputCmd, QtCore.SIGNAL("returnPressed()"),self.imputCommand)
        #QtCore.QObject.connect(self.dialog.uiTextEditor, QtCore.SIGNAL("textChanged()"),self.imputCommand)
        #QtCore.QObject.connect(self.uiTextEditor, QtCore.SIGNAL("textChanged()"), self.uiTextEditor.update)
        
    def imputCommand(self):
        """
            imput dialog
        """
        text=self.dialog.ImputCmd.text()
        if self.activeCommand:
            try:
                if not self.performCommand(self.activeCommand, text):
                    self.activeCommand=None
                    #self.scene.populateScene(self.__pyCadApplication.getActiveDocument())
                else:
                    self.outputMsg(self.activeCommand.getActiveMessage())
            except:
                self.outputMsg("Unable to perfor the command")
                self.activeCommand=None
        else:
            cmdObject=None
            if text in self.__applicationCommand:
                cmdObject=self.__applicationCommand[text]
                cmdObject.reset()
                self.outputMsg(cmdObject.getActiveMessage())
            else:
                self.outputMsg('Command not avaiable write ? for command list')
            self.activeCommand=cmdObject
        self.dialog.ImputCmd.setText("")
    
    def performCommand(self,cObject, text):
        """
            Perform a Command
            cObject is the command object
        """
        try:
            iv=cObject.next()
            exception,message=iv
            try:
                raise exception(None)
            except ExcPoint:
                cObject[iv]=self.convertToPoint(text)  
                return cObject
            except (ExcLenght, ExcAngle):
                cObject[iv]=self.convertToFloat(text)
                return cObject
            except (ExcText):
                cObject[iv]=text
                return cObject
            except (ExEntity):
                cObject[iv]=self.convertToInt(text)
                return cObject
            except:
                msg="Error on command imput"
                self.outputMsg(msg)
                raise CommandImputError, msg
            
        except (StopIteration):
            cObject.applyCommand()
            return None
        except PyCadWrongCommand:
            self.outputMsg("Wrong Command")
    
    def convertToInt(self, msg):   
        """
            return an int from user
        """        
        if msg:
            return int(msg)
        return None
        
    def convertToFloat(self, msg):
        """
            return a float number
        """
        if msg:
            return float(msg)
        return None
        
    def convertToPoint(self, msg):
        """
            ask at the user to imput a point 
        """
        if msg:
            coords=msg.split(',')
            x=float(coords[0])
            y=float(coords[1])
            return Point(x, y)
        return None

            
    def outputMsg(self, msg):   
        """
            print a message in to the self.dialog.uiTextEditor 
        """ 
        #self.dialog.uiTextEditor.moveCursor(QtGui.QTextCursor.Down)
        msg=u"\r<PythonCAD> : "+msg
        self.dialog.uiTextEditor.insertPlainText(msg)

def printEntity(ents, msgFucntion):
        """
            print a query result
        """
        i=0
        for e in ents:
            msgFucntion("Entity Type %s id %s "%(str(e.eType),str(e.getId())))
            if i > 100:
                msgFucntion("There are more then 100 entitys in the select so i stop printing")
                break
            i+=1
            
class GetEnts(BaseCommand):
    def __init__(self, document, msgFucntion):
        BaseCommand.__init__(self, document)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.outputMsg=msgFucntion
        self.exception=[ExcText]
        self.message=["Give Me the Document Type Enter for All"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        docName=self.value[0]
        startTime=time.clock()
        if not docName:
            docName="ALL"
        ents=self.document.getEntityFromType(type)
        endTime=time.clock()-startTime       
        printEntity(ents,msgFucntion )
        self.outputMsg("Exec query get %s ent in %s s"%(str(len(ents)), str(endTime)))
        self.outputMsg("********************************")

class GetActiveDoc(BaseCommand):
    def __init__(self, application, msgFunction):
        BaseCommand.__init__(self, None)
        self.__application=application
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.message=["Press enter to perform the command"]
        self.outputMsg=msgFunction
    def applyCommand(self):
        if len(self.value)!=0:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        docName=self.value[0]
        self.__application.setActiveDocument(docName)
        doc=self.__application.getActiveDocument()
        self.outputMsg("Active Document is %s"%str(doc.dbPath))
        
        
class SetActiveDoc(BaseCommand):
    def __init__(self, application):
        BaseCommand.__init__(self, None)
        self.__application=application
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcText]
        self.message=["Give Me the Document Name"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        docName=self.value[0]
        self.__application.setActiveDocument(docName)
        
class GetDocuments(BaseCommand):
    def __init__(self, documents, msgFunction):
        BaseCommand.__init__(self, None)
        self.__docuemnts=documents
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.message=["Press enter to perform the command"]
        self.outputMsg=msgFunction
    def applyCommand(self):
        if len(self.value)!=0:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        self.showDocuments()
        
    def showDocuments(self):
        """
            show The list of documents
        """
        try:
            self.outputMsg("Documents in the curret application")
            i=0
            for key in self.__docuemnts:
                self.outputMsg("%s File %s"%(str(i), str(key)))
                i+=1
            self.outputMsg("***********************************")
        except:
            self.outputMsg("Unable To Perform the GetDocuments") 
            
class CreateStyle(BaseCommand):
    def __init__(self, document):
        BaseCommand.__init__(self, document)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[ExcText]
        self.message=["Give Me the Style Name"]
    def applyCommand(self):
        if len(self.value)!=1:
            raise PyCadWrongImputData("Wrong number of imput parameter")
        styleName=self.value[0]
        #self.inputMsg("Write style name")
        stl=Style(styleName)
        self.document.saveEntity(stl);


class PrintHelp(BaseCommand):
    def __init__(self, commandArray, msgFunction):
        BaseCommand.__init__(self, None)
        #PyCadBaseCommand.__exception=[ExcPoint, ExcPoint]
        self.exception=[]
        self.outputMsg=msgFunction
        self.message=["Print the help Press enter to ally the command "]
        self.commandNames=commandArray.keys()

    def next(self):    
        raise StopIteration

    def applyCommand(self):
        self.outputMsg("***********Command List******************")
        for s in   self.commandNames:
            self.outputMsg(s)
            
