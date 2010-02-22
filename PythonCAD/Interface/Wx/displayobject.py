


class DisplayObject(object):

    def __init__(self):
        # list of points that draw the entity
        self._points = []
        # color
        self._color = None
        # linestyle
        self._style = None


    def init_from_segment(self, segment):
        self._points.append(segment.beginpoint)
        self._points.append(segment.endpoint)
        self._color = segment.color
        self._style = segment.style


    def Draw(self, canvas):
        if len(self._points) > 1:
            #canvas.newpath()
            canvas.moveto(self._points[0].X, self._points[0].Y)
            canvas.lineto(self._points[1].X, self._points[1].Y)
            #canvas.stroke()