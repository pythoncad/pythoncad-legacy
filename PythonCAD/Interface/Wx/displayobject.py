
#from Interface.Wx.view import View



class DisplayObject(object):
    """
    Represents a display-able object.
    All entities are translated to a display-able object.
    This display-able object is drawn to screen
    """
    def __init__(self, id):
        # object id
        self._id = id
        # list of points in world coordinates
        self._points = []

    def _GetId(self):
        return self._id
    
    Id = property(_GetId, None, None, "gets the entity id")


    def _GetPoints(self):
        return self._points
    
    Points = property(_GetPoints, None, None, "gets the list of point")
        

    def Display(self, view):
        """
        Display the object in the view
        """
        if len(self._points) > 1:
            pt1 = None
            # traverse trough all points
            for point in self._points:
                # transformation world to view port
                #pt2 = view.MapToView(point)
                pt2 = point
                # draw line if two points are translated
                if (pt1 is not None) and (pt2 is not None):
                    # draw in view port coordinates
                    # color and style are set in the layer display
                    view.dc.DrawLine(pt1.X, pt1.Y, pt2.X, pt2.Y)
                # end point is start of next segment
                pt1 = pt2

    
            