

import wx
import colorsys
from math import cos, sin, radians

from Interface.Wx.displaylist import DisplayList


class ViewPort(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        # parent
        self.__cadwindow = parent
        # adjust view on resize event
        self.Bind(wx.EVT_SIZE, self.OnResize)
        # draw on paint event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # displaylist
        self.__displaylist = DisplayList()
        # visible view
        self.__view = View()

    def __GetView(self):
        return self.__view
    View = property(__GetView, None, None, "Get the view area")

    def __GetDocument(self):
        return self.__cadwindow.Document;

    
    def OnResize(self, event):
        event.GetSize()
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        # black background
        dc.Background = wx.Brush("black")
        dc.Clear()
        # execute the displaylist
        self.__displaylist.Execute(dc)


    def BuildDisplayList(self):
        pass
    
        
    def ZoomAll(self):
        # clear current displaylist
        self.__displaylist.Clear()
        # build new displaylist
        self.BuildDisplayList()
        # draw the displaylist
        self.Refresh()


    def ZoomIn(self):
        pass


    def ZoomOut(self):
        pass

