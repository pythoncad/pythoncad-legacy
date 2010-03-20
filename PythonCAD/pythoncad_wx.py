
import wx
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
    print "Unable to load R*Tree sqlite extention"


from Interface.Wx.cadwindow import CadWindow

app = wx.App(False)
frame = CadWindow(None, "PythonCAD Wx")
app.MainLoop()
