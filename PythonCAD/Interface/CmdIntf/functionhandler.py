from Interface.unitparser   import decodePoint, convertLengh, convertAngle
from Kernel.pycadevent      import PyCadEvent
from Interface.evaluator    import Evaluator

class FunctionHandler(object):
    '''
    This object contains all known commands.
    Commands are registered by "registerCommand" before the are available.
    Evaluation of commands or expressions is done by "evaluate"
    '''
    def __init__(self, edit_ctrl, edit_output):
        '''
        Defines an dictionary containing all known commands.
        Member 'registerCommand' add's a command to the table.
        Member 'evaluate' execute a command by call its call-back or evaluates an expression.
        '''
        # Input control
        self.__edit_ctrl = edit_ctrl
        # Output Control
        self.__edit_output=edit_output
        # current value
        self._value = None
        # command table
        self._command_table = {}
        # Global inner command evaluation
        self.evaluateInner=None
        self.commandExecuted=PyCadEvent()
        #Evaluator
        self._eval=Evaluator(self.printCommand)
        
    def registerCommand(self, name, callback):
        '''
        Register a command with it's callback in the command table.
        Commands are executed by a call to the evaluate function.
        '''
        # a command is at least one character
        if len(name) > 0:
            # the callback is not None
            if not callback is None:
                # commands are always defined in upper case
                self._command_table[name.upper()] = callback

    def evaluate(self, expression):
        '''
        Looks up the expression from the command table.
        If a command is found, it's callback function is called.
        If it is not a command the expression is evaluated.
        Return: command exit, the evaluated expression or "*error*"
        '''
        # commands are always defined in upper case
        command = expression.upper()
        # is it a command from the command table?
        self.__edit_ctrl.clear()
        if self._command_table.has_key(command):
            # call function
            # echo on the comand line
            self.printCommand(command)
            self._value = self._command_table[command]()
        elif self.evaluateInner:
            self.printCommand(command)
            # echo on the comand line
            self.performCommand(self.evaluateInner, command)
            if self.evaluateInner:
                self.printOutput(self.evaluateInner.getActiveMessage())
        else:
            try:
                # let python evaluate expression
                self.printCommand(expression)
                self._value=self._eval.evaluate(expression)
            except:
                self._value ="*error*"
            finally:
                self.__edit_ctrl.clear()
        # show result
        if self._value :
            self.printOutput(self._value)
        return self._value
    
    def evaluateInnerCommand(self, cObject,selectedItems=None):
        """
            evaluate an inner command
        """
        from Kernel.exception import ExcEntity
        if len(selectedItems):
            try:
                raise cObject.exception[0](None)
            except ExcEntity:
                text=None
                for ent in selectedItems:
                    if not text:
                        text=''
                        text+=str(ent.ID)
                    else:
                        text+=","+str(ent.ID)
                cObject.value.append(text)
                cObject.next()
            except:
                pass
        self.evaluateInner=cObject
        self.printOutput(str(self.evaluateInner.getActiveMessage()))
    
    def evaluateMouseImput(self, eventItem):
        """
            evaluate the mouse click
        """
        from Kernel.exception import ExcPoint, ExcEntity, ExcEntityPoint
        try:
            if self.evaluateInner:
                value=None
                point, entity=eventItem
                exception=self.evaluateInner.exception[self.evaluateInner.index+1]
                try:
                    raise exception(None)
                except ExcPoint:
                    value="%s,%s"%(point)
                except ExcEntity:
                    if entity:
                        value=str(entity.ID)
                except (ExcEntityPoint):
                    if entity:
                        sPoint="%s,%s"%(point)
                        id=str(entity.ID)
                        value="%s@%s"%(str(id), str(sPoint))
                except:
                    pass
                if value:
                    self.performCommand(self.evaluateInner, value)
                    if self.evaluateInner.index==len(self.evaluateInner.exception)-1:
                        self.evaluateInner.applyCommand()
                        self.evaluateInner=None
                        self.commandExecuted()
        except:
            self.evaluateInner=None
        if self.evaluateInner:
            self.printOutput(self.evaluateInner.getActiveMessage())
    
    
    def performCommand(self,cObject, text):
        """
            Perform a Command
            cObject is the command object
        """
        self.printOutput(text) 
        from Kernel.exception import ExcPoint, ExcLenght, ExcAngle, ExcInt, ExcBool, ExcText, ExcEntity,ExcEntityPoint,PyCadWrongCommand
        try:
            iv=cObject.next()
            exception,message=iv
            try:
                raise exception(None)
            except ExcPoint:
                cObject[iv]=self.convertToPoint(text)  
                return cObject
            except (ExcLenght, ExcInt):
                cObject[iv]=self.convertToFloat(text)
                return cObject
            except (ExcAngle):
                cObject[iv]=self.convertToAngle(text)
                return cObject                
            except (ExcBool):
                cObject[iv]=self.convertToBool(text)
                return cObject
            except (ExcText):
                cObject[iv]=text
                return cObject
            except (ExcEntity):
                cObject[iv]=str(text)
                return cObject
            except (ExcEntityPoint):
                cObject[iv]=str(text)
                return cObject
            except:
                msg="Error on command imput"
                self.printOutput(msg)
                self.evaluateInner=None
                raise CommandImputError, msg
        except (StopIteration):
            cObject.applyCommand()
            self.evaluateInner=None
        except PyCadWrongCommand:
            self.printOutput("Wrong Command")
            self.evaluateInner=None
            
    def resetCommand(self):
        """
            reset the command if eny are set
        """
        self.evaluateInner=None
        self.printOutput("Command Ended from the user")
        
    def printCommand(self, msg):
        """
            print message
        """
        msg=str(msg)
        if len(msg)>0:
            msg=u"\r>>> "+msg
            self.__edit_output.insertPlainText(msg)
            self.scrollToBottom(self.__edit_output)
        
    def printOutput(self, msg):
        """
            print a message in the output message windows
        """
        msg=str(msg)
        if len(msg)>0:
            msg=u"\r<PythonCAD> : "+msg
            self.__edit_output.insertPlainText(msg)
            self.scrollToBottom(self.__edit_output)
            
    def scrollToBottom(self, editText):    
        """
            scroll the qttext to the end
        """
        sb = editText.verticalScrollBar()
        sb.setValue(sb.maximum())

    def convertToBool(self, msg):   
        """
            return an int from user
        """        
        if msg=="Yes":
            return True
        else:
            return False

    def convertToInt(self, msg):   
        """
            return an int from user
        """        
        if msg:
            return int(convertLengh(msg))
        return None
        
    def convertToFloat(self, msg):
        """
            return a float number
        """
        if msg:
            return convertLengh(msg)
        return None
        
    def convertToAngle(self, msg):
        """
            convert the angle using sympy
        """
        if msg:
            p=convertAngle(msg)
            return p
        return None
        
    def convertToPoint(self, msg):
        """
            ask at the user to imput a point 
        """
        if msg:
            p=decodePoint(msg)
            return p
        return None
