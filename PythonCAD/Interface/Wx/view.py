
from Generic.Kernel.Entity.point import Point



class View(object):
    """
    Defines a view.
    An example of a view is the screen rectangle or a world rectangle.
    The views are mapped to get the world->screen and screen->world transformations
    Or world->paper transformations
    """
    def __init__(self):
        # device context used for drawing
        self._dc = None
        # view dimensions
        self._x = 0.0
        self._y = 0.0
        self._width = 0.0
        self._height = 0.0
        # transformation
        self._trans_x = 0.0
        self._trans_y = 0.0
        self._scale_x = 1.0
        self._scale_y = 1.0
        # vertical exaggeration (not used)
        self._vertical_exaggeration = 1.0


    def _GetDc(self):
        return self._dc
    
    def _SetDc(self, dc):
        self._dc = dc
    
    dc = property(_GetDc, _SetDc, None, "gets/sets the device context")
    
    
    def Set(self, x, y, width, height):
        """
        Set the view dimension
        """
        self._x = x
        self._y = y
        self._width = width
        self._height = height


 
    def _GetX(self):
        """
        Left side of the view
        """
        return self._x
    
    def _SetX(self, x):
        """
        Left side of the view
        """
        self._x = x

    X = property(_GetX, _SetX, None, "gets/sets X value")


    def _GetY(self):
        """
        Left side of the view
        """
        return self._y
    
    def _SetY(self, y):
        """
        Left side of the view
        """
        self._y = y

    Y = property(_GetY, _SetY, None, "gets/sets Y value")
    

    def _GetWidth(self):
        """
        Width of the view
        """
        return self._width
    
    def _SetWidth(self, width):
        """
        Width of the view
        """
        self._width = width
    
    Width = property(_GetWidth, _SetWidth, None, "gets/sets width value")


    def _GetHeight(self):
        """
        Height of the view
        """
        return self._height
    
    def _SetHeight(self, height):
        """
        Height of the view
        """
        self._height = height
    
    Height = property(_GetHeight, _SetHeight, None, "gets/sets height value")


    def _GetTransX(self):
        """
        View translation in X direction
        """
        return self._trans_x
    
    TransX = property(_GetTransX, None, None, "Gets the X transformation")


    def _GetTransY(self):
        """
        View translation in Y direction
        """
        return self._trans_x
    
    TransY = property(_GetTransY, None, None, "Gets the Y transformation")


    def _GetScaleX(self):
        """
        View scale in X direction
        """
        return self._scale_x
    
    ScaleX = property(_GetScaleX, None, None, "Gets the X scale")


    def _GetScaleY(self):
        """
        View scale in Y direction
        """
        return self._scale_y
    
    ScaleY = property(_GetScaleY, None, None, "Gets the Y scale")



    def SetMapping(self, view):
        """
        Set the mapping between 2 views.
        Normal this is a world to screen or screen to world transformation. 
        """
        # calculate scale factors
        scale_x = 1.0 * self.Width / view.Width
        scale_y = 1.0 * self.Height / view.Height
        self._scale_x = min(scale_x, scale_y)
        self._scale_y = self._scale_x * self._vertical_exaggeration
        # calculate translation
        self._trans_x = view.X
        self._trans_y = view.Y


    def MapToView(self, point):
        """
        Map a point to this view.
        Mapping is done between two view (world and screen).
        The mapping value is set by SetMapping.
        """
        # create new transformed point
        tpoint = Point(point.X, point.Y)
        # 
        tpoint.X = (point.X - self._trans_x) * self._scale_x
        tpoint.Y = self.Height - (point.Y - self._trans_y) * self._scale_y
        # result is translated point
        return tpoint


        