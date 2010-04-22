
import wx
import types

from Generic.Kernel.Entity.segment import Segment
from Generic.Kernel.pycadent import PyCadEnt

from Interface.Wx.displayobject import DisplayObject

# draw methods
from Interface.Wx.segmentdraw import DrawSegment
from Interface.Wx.segmentdraw import EraseSegment


class LayerDisplay(object):
    """
    A display list contains all drawable entity data from a single layer.
    The list contains raw drawing data.
    This raw drawing data is multiplied with the display matrix to get viewport data.
    """
    def __init__(self):
        # the display list for this layer, list of DisplayObjects
        self.__displaylist = {}
        # layer entity properties
        self._id = 0
        self._visible = True
        self._color = wx.Colour(255, 0, 0, wx.ALPHA_OPAQUE)
        #self.__linestyle = wx.Solid
        self._linewidth = 1
        # initialize draw methods
        self._InitDrawMethods()
       
       
    def _GetDisplayList(self):
        return self.__displaylist
    
    DisplayList = property(_GetDisplayList, None, None, "gets the display list")


    def _InitDrawMethods(self):
        """
        Add draw methods to the entity classes
        """
        # segment draw
        _class = PyCadEnt
        _class.Draw = types.MethodType(DrawSegment, None, _class)
        _class.Erase = types.MethodType(EraseSegment, None, _class)
       
        
    def ClearDisplay(self):
        """
        Clears all the data from the layer.
        """
        # remove all elements from the display list
        self.__displaylist.clear()
        
        
    def AddEntity(self, entity):
        """
        Add an entity to the display
        """
        if entity is not None:
            entity.Draw(self)
        
            
    
    def RemoveEntity(self, entity):
        """
        Removes an entity from the display
        """
        if entity is not None:
            entity_class = entity.getConstructionElements()
            entity_class.Erase(entity.Id, self)
                
    
    def Display(self, view):
        """
        Shows the display list if the layer is visible
        """
        # is the layer visible
        if self._visible:
            # set layer display properties
            view.dc.SetPen(wx.Pen(self._color, 1))
            # display all objects
            for id, display_object in self.__displaylist.items():
                # display an object
                display_object.Display(view)

        
#    def GetBBox(self):
#        """
#        Gets the bounding box for all entities on this layer
#        """
#        pass
    
    
#    def __AddSegment(self, id, segment):
#        list_object = DisplayObject()
#        # create a display object in world coordinates
#        list_object.init_from_segment(segment)
#        # add display object to the list
#        self.__displaylist[id] = list_object
        
            