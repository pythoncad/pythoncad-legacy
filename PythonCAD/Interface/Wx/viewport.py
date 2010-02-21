

import wx
import colorsys
from math import cos, sin, radians

from Interface.Wx.displaylist import DisplayList


class ViewPort(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        # draw on paint event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # displaylist
        self.__displaylist = DisplayList()



    def OnPaint(self, evt):
        dc = wx.PaintDC(self)
        # black background
        dc.Background = wx.Brush("black")
        dc.Clear()
        # execute the displaylist
        self.__displaylist.Execute(dc)


    def ZoomAll(self):
        pass


    def ZoomIn(self):
        pass


    def ZoomOut(self):
        pass

