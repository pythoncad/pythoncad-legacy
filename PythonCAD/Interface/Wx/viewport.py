

import wx
import colorsys
from math import cos, sin, radians

from Interface.Wx.displaylayer import DisplayLayer
from Interface.Wx.view import View


class ViewPort(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        # parent
        self.__cadwindow = parent
        # document
        self.__document = None
        # adjust view on resize event
        self.Bind(wx.EVT_SIZE, self.OnResize)
        # draw on paint event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # display layers
        self.__display_layers = {}
        # visible view on screen
        self.__screen_view = View()
        # world view
        self.__world_view = View()

    def __GetView(self):
        return self.__view
    View = property(__GetView, None, None, "Get the view area")

    def __GetDocument(self):
        return self.__dDocument;

    def __SetDocument(self, document):
        self.__dDocument = document;

        Document = property(__GetDocument, __SetDocument, None, "Get/Set the document used by the view")


    def GetDisplayLayer(self, layer_name):
        """
        Get the display layer corresponding to this layer name
        """
        # is the layer already in the table
        if not self.__display_layers.has_key(layer_name):
            self.__display_layers[layer_name] = DisplayLayer()
        return self.__display_layers[layer_name]
    

    def OnResize(self, event):
        pass
        # set the new size
#        self.__screen_view.Set(event.GetClientRect())
        # map new screen size to world


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

