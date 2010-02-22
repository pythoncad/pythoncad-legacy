import wx
import os

from PythonCAD.Interface.Wx.cadwindow import CadWindow


app = wx.App(False)
frame = CadWindow(None, "PythonCAD Wx")
app.MainLoop()
