
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
        self.__dc = None
        # view dimensions
        self.__x_min = 0.0
        self.__y_min = 0.0
        self.__x_max = 0.0
        self.__y_max = 0.0
        # transformation
        self.__trans_x = 0.0
        self.__trans_y = 0.0
        self.__scale_x = 1.0
        self.__scale_y = 1.0
        # vertical exaggeration (not used)
        self.__vertical_exaggeration = 1.0


    def _GetDc(self):
        return self.__dc
    
    def _SetDc(self, dc):
        self.__dc = dc
    
    dc = property(_GetDc, _SetDc, None, "gets/sets the device context")
    
    
    def Set(self, x_min, y_min, x_max, y_max):
        """
        Set the view dimension
        """
        self.__x_min = x_min
        self.__y_min = y_min
        self.__x_max = x_max
        self.__y_max = y_max


 
    def __GetXMin(self):
        """
        Left side of the view
        """
        return self.__x_min
    
    XMin = property(__GetXMin, None, None, "Gets minimum X value")


    def __GetXMax(self):
        """
        Right side of the view
        """
        return self.__x_max
    
    XMax = property(__GetXMax, None, None, "Gets maximum X value")


    def __GetYMin(self):
        """
        Bottom of the view
        """
        return self.__y_min
    
    YMin = property(__GetYMin, None, None, "Gets minimum Y value")


    def __GetYMax(self):
        """
        Top of the view
        """
        return self.__y_max
    
    YMax = property(__GetYMax, None, None, "Gets maximum Y value")


    def __GetWidth(self):
        """
        Width of the view
        """
        return self.__x_max - self.__x_min
    
    Width = property(__GetWidth, None, None, "Gets the width")


    def __GetHeight(self):
        """
        Height of the view
        """
        return self.__y_max - self.__y_min
    
    Height = property(__GetHeight, None, None, "Gets the height")


    def __GetTransX(self):
        """
        View translation in X direction
        """
        return self.__trans_x
    
    TransX = property(__GetTransX, None, None, "Gets the X transformation")


    def __GetTransY(self):
        """
        View translation in Y direction
        """
        return self.__trans_x
    
    TransY = property(__GetTransY, None, None, "Gets the Y transformation")


    def __GetScaleX(self):
        """
        View scale in X direction
        """
        return self.__scale_x
    
    ScaleX = property(__GetScaleX, None, None, "Gets the X scale")


    def __GetScaleY(self):
        """
        View scale in Y direction
        """
        return self.__scale_y
    
    ScaleY = property(__GetScaleY, None, None, "Gets the Y scale")



    def SetMapping(self, view):
        """
        Set the mapping between 2 views.
        Normal this is a world to screen or screen to world transformation. 
        """
        # calculate scale factors
        scale_x = 1.0 * self.Width / view.Width
        scale_y = 1.0 * self.Height / view.Height
        self.__scale_x = min(scale_x, scale_y)
        self.__scale_y = self.__scale_x * self.__vertical_exaggeration
        # calculate translation
        self.__trans_x = view.XMin    
        self.__trans_y = view.YMin    


    def MapToView(self, point):
        """
        Map a point to this view.
        Mapping is done between two view (world and screen).
        The mapping value is set by SetMapping.
        """
        # create new transformed point
        tpoint = Point()
        # 
        tpoint.X = (point.X - self.__trans_x) * self.__scale_x
        tpoint.Y = (point.Y - self.__trans_y) * self.__scale_y
        # result is translated point
        return tpoint
        
        