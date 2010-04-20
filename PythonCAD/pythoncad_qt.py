#!/usr/bin/env python

# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QString', 2)

from PyQt4 import QtCore, QtGui
import sys
import os
import platform

pysqlite_path = None

# OSX specific path
if sys.platform == 'darwin':
    # universal binary
    pysqlite_path = os.path.join(os.getcwd(), 'macosx')
# linux specific path
elif sys.platform == 'linux2':
    if platform.machine() == 'x86_64':
        # amd64
        pysqlite_path = os.path.join(os.getcwd(), 'linux2', 'lib64')
    else:
        # x86
        pysqlite_path = os.path.join(os.getcwd(), 'linux2', 'lib32')
# windows specific path
elif sys.platform == 'win32':
    if platform.machine() == 'x86_64':
        # amd64
        pysqlite_path = os.path.join(os.getcwd(), 'win32', 'lib64')
    else:
        # x86
        pysqlite_path = os.path.join(os.getcwd(), 'win32', 'lib32')

# add pysqlite to search path
if pysqlite_path != None:
    sys.path.append(pysqlite_path)

# this is needed for me to use unpickle objects
sys.path.append(os.path.join(os.getcwd(), 'Generic', 'Kernel'))

# check if it is possible to import pysqlite
try:
    from pysqlite2 import dbapi2 as sqlite
    print "R*Tree sqlite extention loaded"
except ImportError, e:
    raise Exception('StructuralError', 'Unable to load the R*Tree extention module')


from Interface.cadwindow import CadWindow

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    mainWin = CadWindow()
    mainWin.show()
    sys.exit(app.exec_())
    
    