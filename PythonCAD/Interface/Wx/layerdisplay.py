
import wx
import types

from Generic.Kernel.Entity.segment import Segment
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
        self.__id = 0
        self.__visible = True
        self.__color = wx.Colour(255, 0, 0, wx.ALPHA_OPAQUE)
        #self.__linestyle = wx.Solid
        self.__linewidth = 1
        # initialize draw methods
        self.__InitDrawMethods()
       
       
    def __GetDisplayList(self):
        return self.__displaylist
    
    DisplayList = property(__GetDisplayList, None, None, "gets the display list")


    def __InitDrawMethods(self):
        """
        Add draw methods to the entity classes
        """
        # segment draw
        _class = Segment
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
            id = entity.getId()
            mbr = entity.getBBox()
            
            
            
    
    
    def RemoveEntity(self, entity):
        """
        Removes an entity from the display
        """
        if entity is not None:
            id = entity.getId()
            # is the entity in the list
            if self.__displaylist.haskey(id):
                del(self.__displaylist, id)
                
    
    def Display(self):
        """
        Shows the displaylist if the layer is visible
        """
        if self.__visible:
            self.__displaylist.Execute()
        
    def GetBBox(self):
        """
        Gets the bounding box for all entities on this layer
        """
        pass
    
    
    def __AddSegment(self, id, segment):
        list_object = DisplayObject()
        # create a display object in world coordinates
        list_object.init_from_segment(segment)
        # add display object to the list
        self.__displaylist[id] = list_object
        
            