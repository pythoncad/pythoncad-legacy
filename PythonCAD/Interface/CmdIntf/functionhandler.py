

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
        # echo on the comand line
        self.printCommand(command)
        # is it a command from the command table?
        self.__edit_ctrl.clear()
        if self._command_table.has_key(command):
            # call function
            self._value = self._command_table[command]()
        elif self.evaluateInner:
            self.performCommand(self.evaluateInner, command)
            if self.evaluateInner:
                self.printOutput(str(self.evaluateInner.getActiveMessage()))
        else:
            try:
                # let python evaluate expression
                self._value =eval(expression)
            except:
                self._value ="*error*"
            finally:
                self.__edit_ctrl.clear()
        # show result
        if self._value :
            self.printOutput(str(self._value))
        return self._value
    
    def evaluateInnerCommand(self, cObject):
        """
            evaluate an inner command
        """
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
        except:
            self.evaluateInner=None
        if self.evaluateInner:
            self.printOutput(str(self.evaluateInner.getActiveMessage()))
    
    
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
            except (ExcLenght, ExcAngle, ExcInt):
                cObject[iv]=self.convertToFloat(text)
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
        
    def printCommand(self, msg):
        """
            print message
        """
        if len(msg)>0:
            msg=u"\r>>> "+msg
            self.__edit_output.insertPlainText(msg)
            self.scrollToBottom(self.__edit_output)
        
    def printOutput(self, msg):
        """
            print a message in the output message windows
        """
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
        from Kernel.GeoEntity.point import Point
        if msg:
            coords=msg.split(',')
            x=float(coords[0])
            y=float(coords[1])
            return Point(x, y)
        return None
