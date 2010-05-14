
# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui
from Interface.CmdIntf.functionhandler import FunctionHandler


class CmdlineDock(QtGui.QDockWidget):
    '''
    A dockable window containing a edit line object.
    The edit line is used to enter commands or expressions.
    '''
    
    def __init__(self, title, parent):
        '''
        Creates an edit line in which commands or expressions are evaluated.
        Evaluation of expressions is done by the FunctionHandler object.
        '''
        super(CmdlineDock, self).__init__(title, parent)
        # only dock at the bottom or top
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea | QtCore.Qt.TopDockWidgetArea)
        self.__edit_ctrl = QtGui.QLineEdit(self, returnPressed=self._returnPressed)
        self.setWidget(self.__edit_ctrl)
        # function handler to evaluate actions
        self.__function_handler = FunctionHandler(self.__edit_ctrl)


    #-------- properties -----------#
    
    def _getFunctionHandler(self):
        return self.__function_handler
    
    FunctionHandler = property(_getFunctionHandler, None, None, 'Get the function handle object')
    
    
    #-------- properties -----------#
    
    def _returnPressed(self):
        '''
        Text entered on the command line is accepted by the user by pressing the return button
        '''
        expression = self.__edit_ctrl.text()
        self.evaluate(expression)
        
    
    def evaluate(self, expression):
        '''
        Let the function handler evaluate the expression.
        * Commamds are executed.
        * Expressions are evaluated, the result is placed in the command line edit field.
        '''
        # evaluate the expression
        result = self.__function_handler.evaluate(expression)
        return result
    
    