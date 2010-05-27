#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui
import sys
import os
import sqlite3 as sqlite

# this is needed for me to use unpickle objects
sys.path.append(os.path.join(os.getcwd(), 'Generic'))

from Generic.Kernel.application import Application
from Interface.globals import *
from Interface.cadwindow import *


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    # global_cad_window is from globals
    global_application = Application()
    # global_cad_window is from globals
    global_cad_window = CadWindow()
    # show the main window and enter event loop
    global_cad_window.show()
    sys.exit(app.exec_())
    
    
