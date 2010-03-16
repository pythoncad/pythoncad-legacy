
from Interface.Wx.displayobject import DisplayObject


class DisplayList(object):
    """
    A display list contains all drawable entity data from a single layer.
    The list contains raw drawing data.
    This raw drawing data is multiplied with the display matrix to get viewport data.
    """

    def __init__(self):
        self.__list_objects = []


    def Execute(self, dc):
        pass

    def Clear(self):
        self.__list_objects = []
        
    
    def AddSegment(self, segment):
        list_object = DisplayObject()
        list_object.init_from_segment(segment)
        
    
    