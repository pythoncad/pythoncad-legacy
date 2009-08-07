#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PythonCAD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PythonCAD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#
# class stuff for circles
#


from __future__ import generators

import math

from PythonCAD.Generic import tolerance
from PythonCAD.Generic import point
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import quadtree
from PythonCAD.Generic import util
from PythonCAD.Generic import tangent
from PythonCAD.Generic.pyGeoLib import Vector

class Circle(graphicobject.GraphicObject):
    """A base-class for Circles and Arcs

A Circle has two attributes:

center: A Point object
radius: The Circle's radius

A Circle has the following methods:

{get/set}Center(): Get/Set the center Point of a Circle.
{get/set}Radius(): Get/Set the radius of a Circle.
move(): Move the Circle.
circumference(): Get the Circle's circumference.
area(): Get the Circle's area.
mapCoords(): Find the nearest Point on the Circle to a coordinate pair.
inRegion(): Returns whether or not a Circle can be seen in a bounded area.
clone(): Return an indentical copy of a Circle.
    """

    __defstyle = None

    __messages = {
        'moved' : True,
        'center_changed' : True,
        'radius_changed' : True,
        }

    def __init__(self, center, radius, st=None, lt=None, col=None, th=None, **kw):
        """Initialize a Circle.

Circle(center, radius[, st, lt, col, th])

The center should be a Point, or a two-entry tuple of floats,
and the radius should be a float greater than 0.
        """
        _cp = center
        if not isinstance(_cp, point.Point):
            _cp = point.Point(center)
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        super(Circle, self).__init__(_st, lt, col, th, **kw)
        self.__radius = _r
        self.__center = _cp
        _cp.connect('moved', self.__movePoint)
        _cp.connect('change_pending', self.__pointChangePending)
        _cp.connect('change_complete', self.__pointChangeComplete)
        _cp.storeUser(self)

    def __eq__(self, obj):
        """Compare a Circle to another for equality.
        """
        if not isinstance(obj, Circle):
            return False
        if obj is self:
            return True
        return (self.__center == obj.getCenter() and
                abs(self.__radius - obj.getRadius()) < 1e-10)

    def __ne__(self, obj):
        """Compare a Circle to another for inequality.
        """
        if not isinstance(obj, Circle):
            return True
        if obj is self:
            return False
        return (self.__center != obj.getCenter() or
                abs(self.__radius - obj.getRadius()) > 1e-10)

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Default Circle Style',
                             linetype.Linetype(u'Solid', None),
                             color.Color(0xffffff),
                             1.0)
            cls.__defstyle = _s
        return cls.__defstyle

    getDefaultStyle = classmethod(getDefaultStyle)

    def setDefaultStyle(cls, s):
        if not isinstance(s, style.Style):
            raise TypeError, "Invalid style: " + `type(s)`
        cls.__defstyle = s

    setDefaultStyle = classmethod(setDefaultStyle)

    def finish(self):
        self.__center.disconnect(self)
        self.__center.freeUser(self)
        self.__center = self.__radius = None
        super(Circle, self).finish()

    def setStyle(self, s):
        """Set the Style of the Circle.

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(Circle, self).setStyle(_s)

    def getValues(self):
        """Return values comprising the Circle.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(Circle, self).getValues()
        _data.setValue('type', 'circle')
        _data.setValue('center', self.__center.getID())
        _data.setValue('radius', self.__radius)
        return _data

    def getCenter(self):
        """Return the center Point of the Circle.

getCenter()
        """
        return self.__center

    def setCenter(self, c):
        """Set the center Point of the Circle.

setCenter(c)

The argument must be a Point or a tuple containing
two float values.
        """
        if self.isLocked():
            raise RuntimeError, "Setting center not allowed - object locked."
        _cp = self.__center
        if not isinstance(c, point.Point):
            raise TypeError, "Invalid center point: " + `type(c)`
        if _cp is not c:
            _cp.disconnect(self)
            _cp.freeUser(self)
            self.startChange('center_changed')
            self.__center = c
            self.endChange('center_changed')
            self.sendMessage('center_changed', _cp)
            c.connect('moved', self.__movePoint)
            c.connect('change_pending', self.__pointChangePending)
            c.connect('change_complete', self.__pointChangeComplete)
            c.storeUser(self)
            if abs(_cp.x - c.x) > 1e-10 or abs(_cp.y - c.y) > 1e-10:
                self.sendMessage('moved', _cp.x, _cp.y, self.__radius)
            self.modified()

    center = property(getCenter, setCenter, None, "Circle center")

    def getRadius(self):
        """Return the radius of the the Circle.

getRadius()
        """
        return self.__radius

    def setRadius(self, radius):
        """Set the radius of the Circle.

setRadius(radius)

The argument must be float value greater than 0.
        """
        if self.isLocked():
            raise RuntimeError, "Setting radius not allowed - object locked."
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        _cr = self.__radius
        if abs(_cr - _r) > 1e-10:
            self.startChange('radius_changed')
            self.__radius = _r
            self.endChange('radius_changed')
            self.sendMessage('radius_changed', _cr)
            _cx, _cy = self.__center.getCoords()
            self.sendMessage('moved', _cx, _cy, _cr)
            self.modified()

    radius = property(getRadius, setRadius, None, "Circle radius")

    def move(self, dx, dy):
        """Move a Circle.

move(dx, dy)

The first argument gives the x-coordinate displacement,
and the second gives the y-coordinate displacement. Both
values should be floats.
        """
        if self.isLocked():
            raise RuntimeError, "Setting radius not allowed - object locked."
        _dx = util.get_float(dx)
        _dy = util.get_float(dy)
        if abs(_dx) > 1e-10 or abs(_dy) > 1e-10:
            _x, _y = self.__center.getCoords()
            self.ignore('moved')
            try:
                self.__center.move(_dx, _dy)
            finally:
                self.receive('moved')
            self.sendMessage('moved', _x, _y, self.__radius)

    def circumference(self):
        """Return the circumference of the Circle.

circumference()
        """
        return 2.0 * math.pi * self.__radius

    def area(self):
        """Return the area enclosed by the Circle.

area()
        """
        return math.pi * pow(self.__radius, 2)
    def GetTangentPoint(self,x,y,outx,outy):
        """
            Get the tangent from an axternal point
            args:
                x,y is a point near the circle
                xout,yout is a point far from the circle
            return:
                a tuple(x,y,x1,xy) that define the tangent line
        """
        fromPoint=point.Point(outx,outy)
        twoPointDistance=self.__center.Dist(fromPoint)
        if(twoPointDistance<self.__radius):
            return None,None
        originPoint=point.Point(0.0,0.0)        
        tanMod=math.sqrt(pow(twoPointDistance,2)-pow(self.__radius,2))
        print("Radius R: %s Module %s"%(self.__radius,tanMod))
        tgAngle=math.asin(self.__radius/twoPointDistance)
        print("ang: %s"%str(tgAngle))
        #Compute the x versor
        xPoint=point.Point(1.0,0.0)
        xVector=Vector(originPoint,xPoint)
        twoPointVector=Vector(fromPoint,self.__center)
        rightAngle=twoPointVector.Ang(xVector)        
        print("Right Angle: %s"%str(rightAngle))
        tgAngle=tgAngle+rightAngle
        #Compute the tangent Vector
        xCord=math.cos(tgAngle)
        yCord=math.sin(tgAngle)
        dirPoint=point.Point(xCord,yCord) #Versor that point at the tangentPoint
        ver=Vector(originPoint,dirPoint)
        ver.Mult(tanMod)
        tangVectorPoint=ver.Point()
        return point.Point(tangVectorPoint+(outx,outy))
        
        
        
        #creare un vector che punta al punto con angolo tgAngle
        #una volta negativo una volta positivo le tangenti sono 2 nel caso di 
        #distanze maggiore del raggio
        #con due punti trovati ritornare quello piu vicino al maus
        
    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the Circle to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the x-coordinate
y: A Float value giving the y-coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the Circle. If the distance between the actual
Point and the coordinates used as an argument is less than the tolerance,
the actual Point is returned. Otherwise, this function returns None.
        """
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _cx, _cy = self.__center.getCoords()
        _r = self.__radius
        _dist = math.hypot((_x - _cx), (_y - _cy))
        if abs(_dist - _r) < _t:
            _angle = math.atan2((_y - _cy),(_x - _cx))
            _xoff = _r * math.cos(_angle)
            _yoff = _r * math.sin(_angle)
            return (_cx + _xoff), (_cy + _yoff)
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not an Circle exists within a region.

inRegion(xmin, ymin, xmax, ymax[, fully])

The first four arguments define the boundary. The optional
fifth argument 'fully' indicates whether or not the Circle
must be completely contained within the region or just pass
through it.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        util.test_boolean(fully)
        _xc, _yc = self.__center.getCoords()
        _r = self.__radius
        #
        # cheap test to see if circle cannot be in region
        #
        if (((_xc - _r) > _xmax) or
            ((_yc - _r) > _ymax) or
            ((_xc + _r) < _xmin) or
            ((_yc + _r) < _ymin)):
            return False
        _val = False
        _bits = 0
        #
        # calculate distances from center to region boundary
        #
        if abs(_xc - _xmin) < _r: _bits = _bits | 1 # left edge
        if abs(_xc - _xmax) < _r: _bits = _bits | 2 # right edge
        if abs(_yc - _ymin) < _r: _bits = _bits | 4 # bottom edge
        if abs(_yc - _ymax) < _r: _bits = _bits | 8 # top edge
        if _bits == 0:
            #
            # circle must be visible - the center is in
            # the region and is more than the radius from
            # each edge
            #
            _val = True
        else:
            #
            # calculate distance to corners of region
            #
            if math.hypot((_xc - _xmin), (_yc - _ymax)) < _r:
                _bits = _bits | 0x10 # upper left
            if math.hypot((_xc - _xmax), (_yc - _ymin)) < _r:
                _bits = _bits | 0x20 # lower right
            if math.hypot((_xc - _xmin), (_yc - _ymin)) < _r:
                _bits = _bits | 0x40 # lower left
            if math.hypot((_xc - _xmax), (_yc - _ymax)) < _r:
                _bits = _bits | 0x80 # upper right
            #
            # if all bits are set then distance from circle center
            # to region endpoints is less than radius - circle
            # entirely outside the region
            #
            _val = not ((_bits == 0xff) or fully)
        return _val

    def __pointChangePending(self, p, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if args[0] == 'moved':
            self.startChange('moved')

    def __pointChangeComplete(self, p, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        if args[0] == 'moved':
            self.endChange('moved')

    def __movePoint(self, p, *args):
        _alen = len(args)
        if _alen < 2:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _cp = self.__center
        if p is not _cp:
            raise ValueError, "Point is not circle center: " + `p`
        _x, _y = _cp.getCoords()
        self.sendMessage('moved', _x, _y, self.__radius)

    def clone(self):
        """Create an identical copy of a Circle

clone()
        """
        _cp = self.__center.clone()
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Circle(_cp, self.__radius, _st, _lt, _col, _th)

    def sendsMessage(self, m):
        if m in Circle.__messages:
            return True
        return super(Circle, self).sendsMessage(m)

    def clipToRegion(self, xmin, ymin, xmax, ymax):
        """Return the portions of a circle visible in a region.

clipToRegion(xmin, ymin, xmax, ymax)

This method returns a list of tuples. Each tuple contains two
float values representing arcs which are seen in the region. Each
tuple has the start angle and end angle.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _xc, _yc = self.__center.getCoords()
        _r = self.__radius
        _bits = 0
        _arcs = []
        #
        # calculate distances from center to region boundaries
        #
        if abs(_xc - _xmin) < _r: _bits = _bits | 1 # left edge
        if abs(_xc - _xmax) < _r: _bits = _bits | 2 # right edge
        if abs(_yc - _ymin) < _r: _bits = _bits | 4 # bottom edge
        if abs(_yc - _ymax) < _r: _bits = _bits | 8 # top edge
        #
        # test if the circle is entirely contained or entirely
        # outside the region
        #
        # print "bits: %#02x" % _bits
        if _bits == 0:
            #
            # if the circle center is in region then the entire
            # circle is visible since the distance from the center
            # to any edge is greater than the radius. If the center
            # is not in the region then the circle is not visible in
            # the region because the distance to any edge is greater
            # than the radius, and so one of the bits should have been
            # set
            #
            if ((_xmin < _xc <_xmax) and (_ymin < _yc < _ymax)):
                print "circle completely inside region"
                _arcs.append((0.0, 360.0)) # fully in region
        else:
            #
            # calculate distance to corners of region
            #
            if math.hypot((_xc - _xmin), (_yc - _ymax)) < _r:
                _bits = _bits | 0x10 # upper left, NW corner
            if math.hypot((_xc - _xmax), (_yc - _ymin)) < _r:
                _bits = _bits | 0x20 # lower right, SE corner
            if math.hypot((_xc - _xmin), (_yc - _ymin)) < _r:
                _bits = _bits | 0x40 # lower left, SW corner
            if math.hypot((_xc - _xmax), (_yc - _ymax)) < _r:
                _bits = _bits | 0x80 # upper right, NE corner
            #
            # based on the bit pattern the various possible intersections
            # can be determined
            #
            # there is much room for optimization in here - many
            # of the distances from the center point to the region
            # edges and corners are calculated numerous times, the
            # square of these values are also repeatedly calculated ...
            #
            _rsqr = _r * _r
            # _rtd = 180.0/math.pi
            print "bits: %#02x" % _bits
            if _bits == 0x01: # circle crosses left edge twice
                print "circle crosses left edge twice"
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _yt = _yc + _yd
                _yb = _yc - _yd
                print "yt: %g; yb: %g" % (_yt, _yb)
                assert _yt < _ymax, "ytop > ymax"
                assert _yb > _ymin, "ybot < ymin"
                if (_ymin < _yc < _ymax): # must be true
                    _at = _calc_angle((_yt - _yc), (_xmin - _xc))
                    _ab = _calc_angle((_yb - _yc), (_xmin - _xc))
                    _arcs.append((_ab, ((360.0 - _ab) + _at)))
                    if _xc > _xmin: # circle inside region
                        print "circle center inside region"
                    else:
                        print "circle center outside"
                else:
                    if _yc < _ymin:
                        print "yc < ymin (%g < %g)" % (_yc, _ymin)
                    elif _yc > _ymax:
                        print "yc > ymax (%g > %g)" % (_yc, _ymax)
                    else:
                        print "unexpected y: (%g, %g, %g)" % (_ymin, _yc, _ymax)
            elif _bits == 0x02: # circle crosses right edge twice
                print "circle crosses right edge twice"
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yt = _yc + _yd
                _yb = _yc - _yd
                print "yt: %g; yb: %g" % (_yt, _yb)
                assert _yt < _ymax, "ytop > ymax"
                assert _yb > _ymin, "ybot < ymin"
                if (_ymin < _yc < _ymax): # must be true
                    _at = _calc_angle((_yt - _yc), (_xmin - _xc))
                    _ab = _calc_angle((_yb - _yc), (_xmin - _xc))
                    _arcs.append((_at, (_ab - _at)))
                    if _xc < _xmax: # circle inside region
                        print "circle inside"
                    else:
                        print "circle outside"
                else:
                    if _yc < _ymin:
                        print "yc < ymin (%g < %g)" % (_yc, _ymin)
                    elif _yc > _ymax:
                        print "yc > ymax (%g > %g)" % (_yc, _ymax)
                    else:
                        print "unexpected y: (%g, %g, %g)" % (_ymin, _yc, _ymax)
            elif _bits == 0x04: # circle crosses bottom twice
                print "circle crosses bottom twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xr = _xc + _xd
                _xl = _xc - _xd
                print "xl: %g; xr: %g" % (_xl, _xr)
                assert _xr < _xmax, "xright > xmax"
                assert _xl > _xmin, "xeft < xmin"
                if (_xmin < _xc < _xmax): # must be true
                    _al = _calc_angle((_ymin - _yc), (_xl - _xc))
                    _ar = _calc_angle((_ymin - _yc), (_xr - _xc))
                    _arcs.append((_ar, (360.0 - _ar + _al)))
                    if _yc > _ymin: # circle inside region
                        print "circle inside"
                    else:
                        print "circle outside"
                else:
                    if _xc < _xmin:
                        print "xc < xmin (%g < %g)" % (_xc, _xmin)
                    elif _yc > _ymax:
                        print "xc > xmax (%g > %g)" % (_xc, _xmax)
                    else:
                        print "unexpected x: (%g, %g, %g)" % (_xmin, _xc, _xmax)
            elif _bits == 0x08: # circle crosses top twice
                print "circle crosses top twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xr = _xc + _xd
                _xl = _xc - _xd
                print "xl: %g; xr: %g" % (_xl, _xr)
                assert _xr < _xmax, "xright > xmax"
                assert _xl > _xmin, "xeft < xmin"
                if (_xmin < _xc < _xmax): # must be true
                    _al = _calc_angle((_ymax - _yc), (_xl - _xc))
                    _ar = _calc_angle((_ymax - _yc), (_xr - _xc))
                    _arcs.append((_al, (360.0 - _al + _ar)))
                    if _yc < _ymax: # circle inside region
                        print "circle inside"
                    else:
                        print "circle outside"
                else:
                    if _xc < _xmin:
                        print "xc < xmin (%g < %g)" % (_xc, _xmin)
                    elif _yc > _ymax:
                        print "xc > xmax (%g > %g)" % (_xc, _xmax)
                    else:
                        print "unexpected x: (%g, %g, %g)" % (_xmin, _xc, _xmax)
            elif _bits == 0x09: # circle crosses left and top twice
                print "circle crosses left and top twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xr = _xc + _xd
                _xl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _yt = _yc + _yd
                _yb = _yc - _yd
                # top -> left
                _a1 = _calc_angle((_ymax - _yc), (_xl - _xc))
                _a2 = _calc_angle((_yt - _yc), (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> top
                _a1 = _calc_angle((_yb - _yc), (_xmin - _xc))
                _a2 = _calc_angle((_ymax - _yc), (_xr - _xc))
                _arcs.append((_a1, (360.0 - _a1 + _a2)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside"
                else:
                    print "unexpected center for region: (%g, %g)" % (_xc, _yc)
            elif _bits == 0x0a: # circle crosses top and right twice
                print "circle crosses top and right twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xr = _xc + _xd
                _xl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yt = _yc + _yd
                _yb = _yc - _yd
                # top -> right
                _a1 = _calc_angle((_ymax - _yc), (_xl - _xc))
                _a2 = _calc_angle((_yb - _yc), (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> top
                _a1 = _calc_angle((_yt - _yc), (_xmax - _xc))
                _a2 = _calc_angle((_ymax - _yc), (_xr - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside"
                else:
                    print "unexpected center for region: (%g, %g)" % (_xc, _yc)
            elif _bits == 0x06: # circle crosses right and bottom twice
                print "circle crosses right and bottom twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xr = _xc + _xd
                _xl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yt = _yc + _yd
                _yb = _yc - _yd
                # right -> bottom
                _a1 = _calc_angle((_yt - _yc), (_xmax - _xc))
                _a2 = _calc_angle((_ymin - _yc), (_xl - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right
                _a1 = _calc_angle((_ymin - _yc), (_xr - _xc))
                _a2 = _calc_angle((_yb - _yc), (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside"
                else:
                    print "unexpected center for region: (%g, %g)" % (_xc, _yc)
            elif _bits == 0x05: # circle crosses bottom and left twice
                print "circle crosses bottom and left twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xr = _xc + _xd
                _xl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _yt = _yc + _yd
                _yb = _yc - _yd
                # left -> bottom
                _a1 = _calc_angle((_yb - _yc), (_xmin - _xc))
                _a2 = _calc_angle((_ymin - _yc), (_xl - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> left
                _a1 = _calc_angle((_ymin - _yc), (_xr - _xc))
                _a2 = _calc_angle((_yt - _xc), (_xmin - _xc))
                _arcs.append((_a1, (360.0 - _a1 + _a2)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside"
                else:
                    print "unexpected center for region: (%g, %g)" % (_xc, _yc)
            elif _bits == 0x0c: # circle crosses top and bottom twice
                print "circle crosses top and bottom twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xtr = _xc + _xd
                _xtl = _xc - _xd
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xbr = _xc + _xd
                _xbl = _xc - _xd
                # top -> bottom
                _a1 = _calc_angle((_ymax - _yc), (_xtl - _xc))
                _a2 = _calc_angle((_ymin - _yc), (_xbl - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> top
                _a1 = _calc_angle((_ymin - _yc), (_xbr - _xc))
                _a2 = _calc_angle((_ymax - _yc), (_xtr - _xc))
                _arcs.append((_a1, (360.0 - _a1 + _a2)))
                if (_ymin < _yc < _ymax): # needed?
                    print "circle inside region"
                elif _yc < _ymin:
                    print "circle below region"
                else:
                    print "circle above region"
            elif _bits == 0x03: # circle crosses left and right twice
                print "circle crosses left and right twice"
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _ylt = _yc + _yd
                _ylb = _yc - _yd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yrt = _yc + _yd
                _yrb = _yc - _yd
                # left -> right
                _a1 = _calc_angle((_ylb - _yc), (_xmin - _xc))
                _a2 = _calc_angle((_yrb - _yc), (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> left
                _a1 = _calc_angle((_yrt - _yc), (_xmax - _xc))
                _a2 = _calc_angle((_ylt - _yc), (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if (_xmin < _xc < _xmax):
                    print "circle inside region"
                elif _xc < _xmin:
                    print "circle left of region"
                else:
                    print "circle right of region"
            elif _bits == 0x0b: # circle through left, top, right twice
                print "circle through left & top & right twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xtr = _xc + _xd
                _xtl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _ylt = _yc + _yd
                _ylb = _yc - _yd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yrt = _yc + _yd
                _yrb = _yc - _yd
                # top -> left
                _a1 = _calc_angle((_ymax - _yc), (_xtl - _xc))
                _a2 = _calc_angle((_ylt - _yc), (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> right
                _a1 = _calc_angle((_ylb - _yc), (_xmin - _xc))
                _a2 = _calc_angle((_yrb - _yc), (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right > top
                _a1 = _calc_angle((_yrt - _yc), (_xmax - _xc))
                _a2 = _calc_angle((_ymax - _yc), (_xtr - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if (_xmin < _xc < _xmax):
                    print "circle inside region"
                elif _xc < _xmin:
                    print "xc < xmin (%g, %g)" % (_xc, _xmin)
                else:
                    print "xc > xmax (%g, %g)" % (_xc, _xmax)
                if _yc < _ymin:
                    print "yc < ymin (%g, %g)" % (_yc, _ymin)
                else:
                    if _yc > _ymax:
                        print "yc > ymax (%g, %g)" % (_yc, _ymax)
            elif _bits == 0x0e: # circle through top, right, bottom twice
                print "circle through top & right & bottom twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xtr = _xc + _xd
                _xtl = _xc - _xd
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xbr = _xc + _xd
                _xbl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yrt = _yc + _yd
                _yrb = _yc - _yd
                # top -> bottom
                _a1 = _calc_angle((_ymax - _yc), (_xtl - _xc))
                _a2 = _calc_angle((_ymin - _yc), (_xbl - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right
                _a1 = _calc_angle((_ymin - _yc), (_xbr - _xc))
                _a2 = _calc_angle((_yrb - _yc), (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> top
                _a1 = _calc_angle((_yrt - _yc), (_xmax - _xc))
                _a2 = _calc_angle((_ymax - _yc), (_xtr - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if (_ymin < _yc < _ymax):
                    print "circle inside region"
                elif _yc < _ymin:
                    print "yc < ymin (%g, %g)" % (_yc, _ymin)
                else:
                    print "yc > ymax (%g, %g)" % (_yc, _ymax)
                if _xc < _xmin:
                    print "xc < xmin (%g, %g)" % (_xc, _xmin)
                else:
                    if _xc > _xmax:
                        print "xc > xmax (%g, %g)" % (_xc, _xmax)
            elif _bits == 0x07: # circle though right, bottom, left twice
                print "circle through right & bottom & left twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xbr = _xc + _xd
                _xbl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _yrt = _yc + _yd
                _yrb = _yc - _yd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _ylt = _yc + _yd
                _ylb = _yc - _yd
                # right -> left
                _a1 = _calc_angle((_yrt - _yc), (_xmax - _xc))
                _a2 = _calc_angle((_ylt - _yc), (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom
                _a1 = _calc_angle((_ylb - _yc), (_xmin - _xc))
                _a2 = _calc_angle((_ymin - _yc), (_xbl - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right
                _a1 = _calc_angle((_ymin - _yc), (_xbr - _xc))
                _a2 = _calc_angle((_yrb - _yc), (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if (_xmin < _xc < _xmax):
                    print "circle inside region"
                elif _xc < _xmin:
                    print "xc < xmin (%g, %g)" % (_xc, _xmin)
                else:
                    print "xc > xmax (%g, %g)" % (_xc, _xmax)
                if _yc < _ymin:
                    print "yc < ymin (%g, %g)" % (_yc, _ymin)
                else:
                    if _yc > _ymax:
                        print "yc > ymax (%g, %g)" % (_yc, _ymax)
            elif _bits == 0x0d: # circle through bottom, left, top twice
                print "circle through bottom & left & top twice"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _xbr = _xc + _xd
                _xbl = _xc - _xd
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xtr = _xc + _xd
                _xtl = _xc - _xd
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _ylt = _yc + _yd
                _ylb = _yc - _yd
                # bottom -> top
                _a1 = _calc_angle((_ymin - _yc), (_xbr - _xc))
                _a2 = _calc_angle((_ymax - _yc), (_xtr - _xc))
                _arcs.append((_a1, (360.0 - _a1 + _a2)))
                # top -> left
                _a1 = _calc_angle((_ymax - _yc), (_xtl - _xc))
                _a2 = _calc_angle((_ylt - _yc), (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom
                _a1 = _calc_angle((_ylb - _yc), (_xmin - _xc))
                _a2 = _calc_angle((_ymin - _yc), (_xbl - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if (_ymin < _yc < _ymax):
                    print "circle inside region"
                elif _yc < _ymin:
                    print "yc < ymin (%g, %g)" % (_yc, _ymin)
                else:
                    print "yc > ymax (%g, %g)" % (_yc, _ymax)
                if _xc < _xmin:
                    print "xc < xmin (%g, %g)" % (_xc, _xmin)
                else:
                    if _xc > _xmax:
                        print "xc > xmax (%g, %g)" % (_xc, _xmax)
            elif _bits == 0x19: # circle through left, top, and NW corner
                print "circle through left and top with NW corner"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                if _xc > _xmax:
                    _arcs.append((_a1, (_a2 - _a1)))
                else:
                    _arcs.append((_a1, (360.0 - _a1 + _a2)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside region"
                else:
                    print "circle outside region"
            elif _bits == 0x8a: # circle through right, top, and NE corner
                print "circle through right and top with NE corner"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside region"
                else:
                    print "circle outside region"
            elif _bits == 0x26: # circle through right, bottom, and SE corner
                print "circle through right and bottom with SE corner"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside region"
                else:
                    print "circle outside region"
            elif _bits == 0x45: # circle through left, bottom, and SW corner
                print "circle through left and bottom with SW corner"
                _xd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                if _xc < _xmin:
                    _arcs.append((_a1, (_a2 - _a1)))
                else:
                    _arcs.append((_a1, (360.0 - _a1 + _a2)))
                if ((_xmin < _xc < _xmax) and
                    (_ymin < _yc < _ymax)):
                    print "circle inside region"
                else:
                    print "circle outside region"
            elif _bits == 0x9b: # circle through left, right, NE and NW corner
                print "circle through left and right with NE, NW corners"
                _yd = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _yd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc < _xmin:
                    print "x < xmin (%g < %g)" % (_xc, _xmin)
                elif _xc > _xmax:
                    print "x > xmax (%g > %g)" % (_xc, _xmax)
                else:
                    if _yc < _ymax:
                        print "circle center in region"
                    else:
                        print "circle center outside region"
            elif _bits == 0xae: # circle through top, botton, NE and SE corner
                print "circle through top and bottom with NE, SE corners"
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc < _ymin:
                    print "y < ymin (%g < %g)" % (_yc, _ymin)
                elif _yc > _ymax:
                    print "y > ymax (%g > %g)" % (_yc, _ymax)
                else:
                    if _xc < _xmax:
                        print "circle center in region"
                    else:
                        print "circle center outside region"
            elif _bits == 0x67: # circle through left, right, SE and SW corner
                print "circle through left and right with SE, SW corners"
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc < _xmin:
                    print "x < xmin (%g < %g)" % (_xc, _xmin)
                elif _xc > _xmax:
                    print "x > xmax (%g > %g)" % (_xc, _xmax)
                else:
                    if _yc > _ymin:
                        print "circle center inside region"
                    else:
                        print "circle center outside region"
            elif _bits == 0x5d: # circle through top, bottom, SW and NW corner
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                if _xc > _xmin:
                    _arcs.append((_a1, (_a2 - _a1)))
                else:
                    _arcs.append((_a1, (360.0 - _a1 + _a2)))
                print "circle through top and bottom with SW, NW corners"
                if _yc < _ymin:
                    print "y < ymin (%g < %g)" % (_yc, _ymin)
                elif _yc > _ymax:
                    print "y > ymax (%g > %g)" % (_yc, _ymax)
                else:
                    if _xc > _xmin:
                        print "circle center inside region"
                    else:
                        print "circle center outside region"
            elif _bits == 0xbf: # circle center NE, crosses left and bottom
                print "circle center NE of region, crosses left and bottom"
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
            elif _bits == 0xef: # circle center SE, crosses left and top
                print "circle center SE of region, crosses left and top"
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
            elif _bits == 0x7f: # circle center SW, crosses top and right
                print "circle center SW of region, crosses top and right"
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
            elif _bits == 0xdf: # circle center NW, crosses right and bottom
                print "circle center NW of region, crosses right and bottom"
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
            elif _bits == 0x9f: # circle center N, crosses left, right, bottom
                print "circle center N, crosses left, right, and twice bottom"
                # left -> bottom
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a1 = _calc_angle(-_yd, (xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right; _xd now positive
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc < _ymax:
                    print "yc < ymax (%g < %g)" % (_yc, _ymax)
                if ((_xc <  _xmin) or (_xc > _xmax)):
                    print "xc: %g; xmin: %g; xmax: %g" % (_xc, _xmin, _xmax)
            elif _bits == 0xaf: # circle center W, crosses bottom, left, top
                print "circle center W, crosses bottom, top, and twice left"
                # top -> left
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom; _yd now negative
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc < _xmax:
                    print "xc < xmax (%g < %g)" % (_xc, _xmax)
                if ((_yc < _ymin) or (_yc > _ymax)):
                    print "yc: %g; ymin: %g; ymax: %g" % (_yc, _ymin, _ymax)
            elif _bits == 0x6f: # circle center S, crosses left, top, right
                print "circle center S, crosses left, right, and twice top"
                # right -> top
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # top -> left; _xd now negative
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc > _ymin:
                    print "yc > ymin (%g > %g)" % (_yc, _ymin)
                if ((_xc <  _xmin) or (_xc > _xmax)):
                    print "xc: %g; xmin: %g; xmax: %g" % (_xc, _xmin, _xmax)
            elif _bits == 0x5f: # circle center E, crosses top, right, bottom
                print "circle center E, crosses top, bottom, and twice right"
                # bottom -> right
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> top, _yd now positive
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc > _xmin:
                    print "xc > xmin (%g > %g)" % (_xc, _xmin)
                if ((_yc < _ymin) or (_yc > _ymax)):
                    print "yc: %g; ymin: %g; ymax: %g" % (_yc, _ymin, _ymax)
            elif _bits == 0x1d:
                print "circle center N near NW, crosses T&L once, B twice"
                # left -> bottom
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # top -> bottom; _xd now positive
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                if _yc > _ymax:
                    _arcs.append((_a1, (_a2 - _a1)))
                else:
                    _arcs.append((_a1, (360.0 - _a1 + _a2)))
                if _xc < _xmin:
                    print "x < xmin (%g < %g)" % (_xc, _xmin)
                if _yc < _ymax:
                    print "y < ymax (%g < %g)" % (_yc, _ymax)
            elif _bits == 0x4d:
                print "circle center S near SW, crosses B&L once, T twice"
                # bottom -> top
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # top -> left, _xd now negative
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc < _xmin:
                    print "x < xmin (%g < %g)" % (_xc, _xmin)
                if _yc > _ymin:
                    print "y > ymin (%g > %g)" % (_yc, _ymin)
            elif _bits == 0x2e:
                print "circle center S near SE, crosses B&R once, T twice"
                # right -> top
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # top -> bottom; _xd now negative
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc > _xmax:
                    print "x > xmax (%g > %g)" % (_xc, _xmax)
                if _yc > _ymin:
                    print "y > ymin (%g > %g)" % (_yc, _ymin)
            elif _bits == 0x8e:
                print "circle center N near NE, crosses T&R once, B twice"
                # top -> bottom
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right, _xd now positive
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _xc > _xmax:
                    print "x > xmax (%g > %g)" % (_xc, _xmax)
                if _yc < _ymax:
                    print "y < ymax (%g < %g)" % (_yc, _ymax)
            elif _bits == 0x1b:
                print "circle center E near NW, crosses T&L once, R twice"
                # left -> right
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> top; _yd now positive
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc > _ymax:
                    print "y > ymax (%g > %g)" % (_yc, _ymax)
                if _xc > _xmin:
                    print "x > xmin (%g > %g)" % (_xc, _xmin)
            elif _bits == 0x8b:
                print "circle center W near NE, crosses T&R once, L twice"
                # top -> left
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> right; _yd now negative
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc > _ymax:
                    print "y > ymax (%g > %g)" % (_yc, _ymax)
                if _xc < _xmax:
                    print "x < xmax (%g < %g)" % (_xc, _xmax)
            elif _bits == 0x27:
                print "circle center W near SE, crosses B&R once, L twice"
                # right -> left
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                print "a1: %g; a2: %g" % (_a1, _a2)
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom; now _yd is negative
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                print "a1: %g; a2: %g" % (_a1, _a2)
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc < _ymin:
                    print "y < ymin (%g < %g)" % (_yc, _ymin)
                if _xc < _xmax:
                    print "x < xmax (%g < %g)" % (_xc, _xmax)
            elif _bits == 0x47:
                print "circle center E near SW, crosses B&L once, R twice"
                # bottom -> right
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> left; now _yd is positive
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if _yc < ymin:
                    print "y < ymin (%g < %g)" % (_yc, _ymin)
                if _xc > _xmin:
                    print "x > xmin (%g > %g)" % (_xc, _xmin)
            elif _bits == 0x1f:
                print "circle center NW, crosses L&T once, R&B twice"
                # right -> top
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right; _xd now positive
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and (_ymin < _yc < _ymax)):
                    print "circle center in region"
                else:
                    print "circle center out of region"
            elif _bits == 0x8f:
                print "circle center NE, crosses T&R once, B&L twice"
                # top -> left
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom; _yd now negative
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right; _xd now positive
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and (_ymin < _yc < _ymax)):
                    print "circle center in region"
                else:
                    print "circle center out of region"
            elif _bits == 0x2f:
                print "circle center SE, crosses L&T twice, R&B once"
                # top -> left
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom; _yd now negative
                _a1 = _calc_angle(-_yd, (_xmin - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a2 = _calc_angle((_ymin - _yc), -_xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> top
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and (_ymin < _yc < _ymax)):
                    print "circle center in region"
                else:
                    print "circle center out of region"
            elif _bits == 0x4f:
                print "circle center SW, crosses T&R twice, B&L once"
                # bottom -> right
                _xd = math.sqrt(_rsqr - pow((_ymin - _yc), 2))
                _a1 = _calc_angle((_ymin - _yc), _xd)
                _yd = math.sqrt(_rsqr - pow((_xmax - _xc), 2))
                _a2 = _calc_angle(-_yd, (_xmax - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # right -> top; _yd now positive
                _a1 = _calc_angle(_yd, (_xmax - _xc))
                _xd = math.sqrt(_rsqr - pow((_ymax - _yc), 2))
                _a2 = _calc_angle((_ymax - _yc), _xd)
                _arcs.append((_a1, (_a2 - _a1)))
                # top -> left; _xd now negative
                _a1 = _calc_angle((_ymax - _yc), -_xd)
                _yd = math.sqrt(_rsqr - pow((_xmin - _xc), 2))
                _a2 = _calc_angle(_yd, (_xmin - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                if ((_xmin < _xc < _xmax) and (_ymin < _yc < _ymax)):
                    print "circle center in region"
                else:
                    print "circle center out of region"
            elif _bits == 0x0f:
                print "circle crosses all edges twice"
                _yld = math.sqrt(_rsqr - pow((_xc - _xmin), 2))
                _yrd = math.sqrt(_rsqr - pow((_xc - _xmax), 2))
                _xtd = math.sqrt(_rsqr - pow((_yc - _ymax), 2))
                _xbd = math.sqrt(_rsqr - pow((_yc - _ymin), 2))
                # right -> top
                _x1 = _xmax
                _y1 = _yc + _yrd
                _x2 = _xc + _xtd
                _y2 = _ymax
                _a1 = _calc_angle((_y1 - _yc), (_x1 - _xc))
                _a2 = _calc_angle((_y2 - _yc), (_x2 - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # top -> left
                _x1 = _xc - _xtd
                _y1 = _ymax
                _x2 = _xmin
                _y2 = _yc + _yld
                _a1 = _calc_angle((_y1 - _yc), (_x1 - _xc))
                _a2 = _calc_angle((_y2 - _yc), (_x2 - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # left -> bottom
                _x1 = _xmin
                _y1 = _yc - _yld
                _x2 = _xc - _xbd
                _y2 = _ymin
                _a1 = _calc_angle((_y1 - _yc), (_x1 - _xc))
                _a2 = _calc_angle((_y2 - _yc), (_x2 - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
                # bottom -> right
                _x1 = _xc + _xbd
                _y1 = _ymin
                _x2 = _xmax
                _y2 = _yc - _yrd
                _a1 = _calc_angle((_y1 - _yc), (_x1 - _xc))
                _a2 = _calc_angle((_y2 - _yc), (_x2 - _xc))
                _arcs.append((_a1, (_a2 - _a1)))
            elif _bits == 0xff:
                print "circle outside region"
            else:
                print "Unexpected bit pattern: %#02x" % _bits
        return _arcs

def _calc_angle(dy, dx):
    _angle = math.atan2(dy, dx) * (180.0/math.pi)
    if _angle < 0.0:
        _angle = _angle + 360.0
    return _angle

#
# Quadtree Circle storage
#

class CircleQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(CircleQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 3:
            raise ValueError, "Expected 3 arguments, got %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        _cxmin = _x - _r
        _cxmax = _x + _r
        _cymin = _y - _r
        _cymax = _y + _r
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_cxmin > _xmax) or
                (_cxmax < _xmin) or
                (_cymin > _ymax) or
                (_cymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _cxmax < _xmid: # circle on left side
                    _ne = _se = False
                if _cxmin > _xmid: # circle on right side
                    _nw = _sw = False
                if _cymax < _ymid: # circle below
                    _nw = _ne = False
                if _cymin > _ymid: # circle above
                    _sw = _se = False
                if _ne:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.NENODE))
                if _nw:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.NWNODE))
                if _sw:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.SWNODE))
                if _se:
                    _nodes.append(_node.getSubnode(quadtree.QTreeNode.SENODE))
            else:
                yield _node

    def addObject(self, obj):
        if not isinstance(obj, Circle):
            raise TypeError, "Invalid Circle object: " + `type(obj)`
        if obj in self:
            return
        _x, _y = obj.getCenter().getCoords()
        _r = obj.getRadius()
        _bounds = self.getTreeRoot().getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _cxmin = _x - _r
        _cxmax = _x + _r
        _cymin = _y - _r
        _cymax = _y + _r
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _cxmin - 1.0
            _ymin = _cymin - 1.0
            _xmax = _cxmax + 1.0
            _ymax = _cymax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _cxmin < _xmin:
                _xmin = _cxmin - 1.0
                _resize = True
            if _cxmax > _xmax:
                _xmax = _cxmax + 1.0
                _resize = True
            if _cymin < _ymin:
                _ymin = _cymin - 1.0
                _resize = True
            if _cymax > _ymax:
                _ymax = _cymax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_x, _y, _r):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()            
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(CircleQuadtree, self).addObject(obj)
        obj.connect('moved', self._moveCircle)

    def delObject(self, obj):
        if obj not in self:
            return
        _x, _y = obj.getCenter().getCoords()
        _r = obj.getRadius()
        _pdict = {}
        for _node in self.getNodes(_x, _y, _r):
            _node.delObject(obj) # circle may not be in the node ...
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(CircleQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        _t = tolerance.TOL
        if _alen > 3:
            _t = tolerance.toltest(args[4])
        _xmin = _x - _r - _t
        _xmax = _x + _r + _t
        _ymin = _y - _r - _t
        _ymax = _y + _r + _t
        _circs = []
        for _circ in self.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _cx, _cy = _circ.getCenter().getCoords()
            if ((abs(_cx - _x) < _t) and
                (abs(_cy - _y) < _t) and
                (abs(_circ.getRadius() - _r) < _t)):
                _circs.append(_circ)
        return _circs

    def _moveCircle(self, obj, *args):
        if obj not in self:
            raise ValueError, "Circle not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 3:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        for _node in self.getNodes(_x, _y, _r):
            _node.delObject(obj) # circle may not be in node ...
        super(CircleQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _circ = _tsep = None
        _bailout = False
        _cdict = {}
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_x < (_xmin - _t)) or
                (_x > (_xmax + _t)) or
                (_y < (_ymin - _t)) or
                (_y > (_ymax + _t))):
                continue
            if _node.hasSubnodes():
                _nodes.extend(_node.getSubnodes())
            else:
                for _c in _node.getObjects():
                    _cid = id(_c)
                    if _cid not in _cdict:
                        _cp = _c.mapCoords(_x, _y, _t)
                        if _cp is not None:
                            _cx, _cy = _cp
                            _sep = math.hypot((_cx - _x), (_cy - _y))
                            if _tsep is None:
                                _tsep = _sep
                                _circ = _c
                            else:
                                if _sep < _tsep:
                                    _tsep = _sep
                                    _circ = _c
                            if _sep < 1e-10 and _circ is not None:
                                _bailout = True
                                break
            if _bailout:
                break
        return _circ

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _circs = []
        if not len(self):
            return _circs
        _nodes = [self.getTreeRoot()]
        _cdict = {}
        while len(_nodes):
            _node = _nodes.pop()
            if _node.hasSubnodes():
                for _subnode in _node.getSubnodes():
                    _sxmin, _symin, _sxmax, _symax = _subnode.getBoundary()
                    if ((_sxmin > _xmax) or
                        (_symin > _ymax) or
                        (_sxmax < _xmin) or
                        (_symax < _ymin)):
                        continue
                    _nodes.append(_subnode)
            else:
                for _circ in _node.getObjects():
                    _cid = id(_circ)
                    if _cid not in _cdict:
                        if _circ.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _circs.append(_circ)
                        _cdict[_cid] = True
        return _circs

#
# Circle history class
#

class CircleLog(graphicobject.GraphicObjectLog):
    def __init__(self, c):
        if not isinstance(c, Circle):
            raise TypeError, "Invalid circle: " + `type(c)`
        super(CircleLog, self).__init__(c)
        c.connect('center_changed', self.__centerChanged)
        c.connect('radius_changed', self.__radiusChanged)

    def __radiusChanged(self, c, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _r = args[0]
        if not isinstance(_r, float):
            raise TypeError, "Unxpected type for radius: " + `type(_r)`
        self.saveUndoData('radius_changed', _r)

    def __centerChanged(self, c, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old center point: " + `type(_old)`
        self.saveUndoData('center_changed', _old.getID())

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _c = self.getObject()
        _cp = _c.getCenter()        
        _op = args[0]
        if _op == 'radius_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _r = args[1]
            if not isinstance(_r, float):
                raise TypeError, "Unexpected type for radius: " + `type(_r)`
            _sdata = _c.getRadius()
            self.ignore(_op)
            try:
                if undo:
                    _c.startUndo()
                    try:
                        _c.setRadius(_r)
                    finally:
                        _c.endUndo()
                else:
                    _c.startRedo()
                    try:
                        _c.setRadius(_r)
                    finally:
                        _c.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'center_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _parent = _c.getParent()
            if _parent is None:
                raise ValueError, "Circle has no parent - cannot undo"
            _pt = _parent.getObject(_oid)
            if _pt is None or not isinstance(_pt, point.Point):
                raise ValueError, "Center point missing: id=%d" % _oid
            _sdata = _cp.getID()            
            self.ignore(_op)
            try:
                if undo:
                    _c.startUndo()
                    try:
                        _c.setCenter(_pt)
                    finally:
                        _c.endUndo()
                else:
                    _c.startRedo()
                    try:
                        _c.setCenter(_pt)
                    finally:
                        _c.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(CircleLog, self).execute(undo, *args)
