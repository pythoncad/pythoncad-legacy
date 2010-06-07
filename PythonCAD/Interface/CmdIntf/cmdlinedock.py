
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
        self.setMinimumHeight(100)
        # only dock at the bottom or top
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea | QtCore.Qt.TopDockWidgetArea)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textEditOutput = QtGui.QTextEdit(self.dockWidgetContents)
        self.textEditOutput.setObjectName("textEditOutput") 
        self.textEditOutput.setReadOnly(True) 
        self.textEditOutput.ensureCursorVisible()
        self.verticalLayout_2.addWidget(self.textEditOutput)
        self.__edit_ctrl = QtGui.QLineEdit(self, returnPressed=self._returnPressed)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEditOutput.sizePolicy().hasHeightForWidth())
        self.__edit_ctrl.setSizePolicy(sizePolicy)
        self.verticalLayout_2.addWidget(self.__edit_ctrl)
        self.setWidget(self.dockWidgetContents)
        self.__function_handler = FunctionHandler(self.__edit_ctrl,self.textEditOutput )
        #QtCore.QObject.connect(self.__edit_ctrl, QtCore.SIGNAL("returnPressed()"), self.textEditOutput.centerCursor)

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
    
    
