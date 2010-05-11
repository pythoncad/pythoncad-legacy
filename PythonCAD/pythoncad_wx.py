
import wx
import sys
import os

import  sqlite3 as  sqlite
sys.path.append(os.path.join(os.getcwd(), 'Generic', 'Kernel'))

from Interface.Wx.cadwindow import CadWindow

app = wx.App(False)
frame = CadWindow()
app.MainLoop()
