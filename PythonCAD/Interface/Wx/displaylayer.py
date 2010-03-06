

from Interface.Wx.displaylist import DisplayList
from Interface.Wx.quadtree import Quadtree



class DisplayLayer(object):
    
    def __init__(self):
        # the displaylist for this layer
        self.__displaylist = DisplayList()
        # the quadtree for this layer
        self.__quadtree = Quadtree()
        # layer entity properties
        self.__id = 0
        self.__visible = True
        self.__color = wx.Colour(255, 0, 0, wx.ALPHA_OPAQUE)
        self.__linestyle = wx.Solid
        self.__linewidth = 1
        
        
    def ClearDisplay(self):
        """
        Clears all the data from the layer.
        """
        # remove all elements from the displaylist
        self.__displaylist.Clear()
        # remove all elements from the quadtree
        self.__quadtree.delObjects()
        
        
    def AddEntity(self, entity):
        """
        Add an entity to the display
        """
        pass
    
    
    def RemoveEntity(self, entity):
        """
        Removes an entity from the display
        """
        pass
    
    
    def ShowEntitties(self):
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
    
    
    