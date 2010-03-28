

import wx
import colorsys
from math import cos, sin, radians

from Interface.Wx.layerdisplay import LayerDisplay
from Interface.Wx.view import View


class ViewPort(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=-1)
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
        # draw buffer
        self._draw_buffer = None

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
        rect = event.EventObject.GetRect()
        # set the new size of the display view
        self._display_view.Set(rect.GetX(), rect.GetY(), rect.GetWidth(), rect.GetHeight())
        # create new draw buffer
        self._draw_buffer = wx.EmptyBitmap(rect.GetWidth(), rect.GetHeight(), -1)
        self._memory_dc = wx.MemoryDC()
        self._memory_dc.SelectObject(self._draw_buffer)
        # redraw
        self.Redraw()


    def OnPaint(self, event):
        paintdc = wx.PaintDC(self)
        paintdc.Blit(0, 0, self._display_view.Width, self._display_view.Height, self._memory_dc, 0, 0, wx.COPY, useMask=False)
        event.Skip()

        
    def Clear(self):
        # clear buffer
        self._memory_dc.SetBackground(wx.Brush("black"))
        self._memory_dc.Clear()
        self.Refresh()

        
    def Redraw(self):
        # clear buffer
        self._memory_dc.SetBackground(wx.Brush("black"))
        self._memory_dc.Clear()
        # draw layers
        self._display_view.dc = self._memory_dc
        # display the layers
        for layer_name, layer_display in self._layers_display.items():
            layer_display.Display(self._display_view)
        # let wx call OnPaint
        self.Refresh()


    def ZoomAll(self):
        # get the extents from the database
        extents = self._document.GetDrawingExtents()
        # update the view on the world
        for ext in extents: #Matteo Boscolo
            if not ext:     #en empty drawing cause an error here 
                return 0
        self._world_view.X = extents[0]
        self._world_view.Y = extents[1]
        self._world_view.Width = extents[2] - extents[0]
        self._world_view.Height = extents[3] - extents[1]
        # map the world on the display
        self._world_view.SetMapping(self._display_view)
        # map the display on the world
        self._display_view.SetMapping(self._world_view)
        # draw the display
        self.Redraw()


    def ZoomIn(self):
        pass


    def ZoomOut(self):
        pass

