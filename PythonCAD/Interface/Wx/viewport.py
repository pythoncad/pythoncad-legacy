

import wx
import colorsys
from math import cos, sin, radians

from Interface.Wx.layerdisplay import LayerDisplay
from Interface.Wx.view import View


class ViewPort(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        # draw state TODO
        self._draw_state = 1
        # parent
        self._cadwindow = parent
        # document
        self._document = None
        # adjust view on resize event
        self.Bind(wx.EVT_SIZE, self.OnResize)
        # draw on paint event
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # display layers
        self._layers_display = {}
        # visible view on screen
        self._display_view = View()
        # world view
        self._world_view = View()

#    def __GetView(self):
#        return self.__view
#    View = property(__GetView, None, None, "Get the view area")

    def _GetDocument(self):
        return self._document;

    def _SetDocument(self, document):
        self._document = document;

    Document = property(_GetDocument, _SetDocument, None, "Get/Set the document used by the view")


    def AddEntity(self, entity):
        # layer name
        # TODO: get real layer name from entity
        layer_name = "Standard"
        # get the layer display object
        layer_display = self.GetLayerDisplay(layer_name)
        # add entity
        layer_display.AddEntity(entity)
      
        

    def GetLayerDisplay(self, layer_name):
        """
        Get the display layer corresponding to this layer name
        """
        layer_display = None
        # is the layer already in the table
        if self._layers_display.has_key(layer_name):
            layer_display = self._layers_display[layer_name]
        else:
            # create new
            layer_display = LayerDisplay()
            # add to the table
            self._layers_display[layer_name] = layer_display
        # result should not be None
        return layer_display
    

    def OnResize(self, event):
        # new size + margin of 5 px
        rect = event.EventObject.GetRect().Inflate(5, 5)
        # set the new size of the display view
        self._display_view.Set(rect.GetX(), rect.GetY(), rect.GetWidth(), rect.GetHeight())


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        # black background
        dc.Background = wx.Brush("black")
        dc.Clear()
        
        if self._draw_state != 0:
            self._display_view.dc = dc
            # display the layers
            for layer_name, layer_display in self._layers_display.items():
                layer_display.Display(self._display_view)
        # reset drawstate
        self._draw_state = 1

    def Clear(self):
        self._draw_state = 0
        self.Refresh()
            
    def Redraw(self):
        # let wx call OnPaint
        self.Refresh()


    def ZoomAll(self):
        # get the extents from the database
        extents = self._document.GetDrawingExtents()
        # update the view on the world
        self._world_view.X = extents[0]
        self._world_view.Y = extents[1]
        self._world_view.Width = extents[2] - extents[0]
        self._world_view.Height = extents[3] - extents[1]
        # map the world on the display
        self._world_view.SetMapping(self._display_view)
        # map the display on the world
        self._display_view.SetMapping(self._world_view)
        # draw the display
        self.Refresh()


    def ZoomIn(self):
        pass


    def ZoomOut(self):
        pass

