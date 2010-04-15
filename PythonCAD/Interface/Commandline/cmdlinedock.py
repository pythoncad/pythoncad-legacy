
# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui


class CmdlineDock(QtGui.QDockWidget):
    
    def __init__(self, title, parent):
        super(CmdlineDock, self).__init__(title, parent)
        # only dock at the bottom or top
        self.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea | QtCore.Qt.TopDockWidgetArea)
        self.__cmdline = QtGui.QLineEdit(self)
        self.setWidget(self.__cmdline)