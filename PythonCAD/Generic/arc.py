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
# arc class
#

from __future__ import generators

import math

from PythonCAD.Generic import style
from PythonCAD.Generic import util
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import point
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import quadtree
from PythonCAD.Generic.pyGeoLib import Vector

_dtr = math.pi/180.0
_rtd = 180.0/math.pi

class Arc(graphicobject.GraphicObject):
    """A class for Arcs.

An Arc has four attributes:

center: A Point object
radius: The Arc's radius
start_angle: The start angle
end_angle: The end angle

An Arc has the following methods:

{get/set}Center(): Get/Set the center Point of an Arc.
{get/set}Radius(): Get/Set the radius of an Arc.
{get/set}StartAngle(): Get/Set the starting angle of an Arc.
{get/set}EndAngle(): Get/Set the end angle of an arc
move(): Move the Arc.
length(): Return the length of an Arc.
area(): Return the area of an Arc.
mapPoint(): Find the nearest Point on the Arc to some other Point.
mapCoords(): Find the nearest Point on the Arc to a coordinate pair.
inRegion(): Returns whether or not a Arc can be seen in a bounded area.
clone(): Return an indentical copy of a Arc.
    """

    __defstyle = None

    __messages = {
        'moved' : True,
        'center_changed' : True,
        'radius_changed' : True,
        'start_angle_changed' : True,
        'end_angle_changed' : True
        }

    def __init__(self, center, radius, start_angle, end_angle,
                 st=None, lt=None, col=None, th=None, **kw):
        """Initialize a Arc.

Arc(center, radius, start_angle, end_angle)

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
        _sa = util.make_c_angle(start_angle)
        _ea = util.make_c_angle(end_angle)
        if _st is None:
            _st = self.getDefaultStyle()
        super(Arc, self).__init__(_st, lt, col, th, **kw)
        self.__radius = _r
        self.__sa = _sa
        self.__ea = _ea
        self.__center = _cp
        _cp.connect('moved', self.__movePoint)
        _cp.connect('change_pending', self.__pointChangePending)
        _cp.connect('change_complete', self.__pointChangeComplete)
        _cp.storeUser(self)

    def __eq__(self, obj):
        """Compare a Arc to another for equality.
        """
        if not isinstance(obj, Arc):
            return False
        if obj is self:
            return True
        return ((self.__center == obj.getCenter()) and
                (abs(self.__radius - obj.getRadius()) < 1e-10) and
                (abs(self.__sa - obj.getStartAngle()) < 1e-10) and
                (abs(self.__ea - obj.getEndAngle()) < 1e-10))

    def __ne__(self, obj):
        """Compare a Arc to another for inequality.
        """
        if not isinstance(obj, Arc):
            return True
        if obj is self:
            return False
        return ((self.__center != obj.getCenter()) or
                (abs(self.__radius - obj.getRadius()) > 1e-10) or
                (abs(self.__sa - obj.getStartAngle()) > 1e-10) or
                (abs(self.__ea - obj.getEndAngle()) > 1e-10))

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Default Arc Style',
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
        self.__center = self.__radius = self.__sa = self.__ea = None
        super(Arc, self).finish()

    def setStyle(self, s):
        """Set the Style of the Arc.

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(Arc, self).setStyle(_s)

    def getValues(self):
        """Return values comprising the Arc.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(Arc, self).getValues()
        _data.setValue('type', 'arc')
        _data.setValue('center', self.__center.getID())
        _data.setValue('radius', self.__radius)
        _data.setValue('start_angle', self.__sa)
        _data.setValue('end_angle', self.__ea)
        return _data

    def getCenter(self):
        """Return the center Point of the Arc.

getCenter()
        """
        return self.__center

    def setCenter(self, c):
        """Set the center Point of the Arc.

setCenter(c)

The argument must be a Point or a tuple containing
two float values.
        """
        if self.isLocked():
            raise RuntimeError, "Setting center not allowed - object locked."
        _cp = self.__center
        if not isinstance(c, point.Point):
            raise TypeError, "Invalid center point: " + `c`
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
                self.sendMessage('moved', _cp.x, _cp.y, self.__radius,
                                 self.__sa, self.__ea)
            self.modified()

    center = property(getCenter, setCenter, None, "Arc center")

    def getRadius(self):
        """Return the radius of the the Arc.

getRadius()
        """
        return self.__radius

    def setRadius(self, radius):
        """Set the radius of the Arc.

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
            self.sendMessage('moved', _cx, _cy, _cr, self.__sa, self.__ea)
            self.modified()

    radius = property(getRadius, setRadius, None, "Arc radius")

    def getStartAngle(self):
        """Return the start_angle for the Arc.

getStartAngle()
        """
        return self.__sa

    def setStartAngle(self, angle):
        """Set the start_angle for the Arc.

setStartAngle(angle)

The argument angle should be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Setting start angle not allowed - object locked."
        _sa = self.__sa
        _angle = util.make_c_angle(angle)
        if abs(_sa - _angle) > 1e-10:
            self.startChange('start_angle_changed')
            self.__sa = _angle
            self.endChange('start_angle_changed')
            self.sendMessage('start_angle_changed', _sa)
            _cx, _cy = self.__center.getCoords()
            self.sendMessage('moved', _cx, _cy, self.__radius, _sa, self.__ea)
            self.modified()

    start_angle = property(getStartAngle, setStartAngle, None,
                           "Start angle for the Arc.")

    def getEndAngle(self):
        """Return the end_angle for the Arc.

getEndAngle()
        """
        return self.__ea

    def setEndAngle(self, angle):
        """Set the end_angle for the Arc.

setEndAngle(angle)

The argument angle should be a float.
        """
        if self.isLocked():
            raise RuntimeError, "Setting end angle not allowed - object locked."
        _ea = self.__ea
        _angle = util.make_c_angle(angle)
        if abs(_ea - _angle) > 1e-10:
            self.startChange('end_angle_changed')
            self.__ea = _angle
            self.endChange('end_angle_changed')
            self.sendMessage('end_angle_changed', _ea)
            _cx, _cy = self.__center.getCoords()
            self.sendMessage('moved', _cx, _cy, self.__radius, self.__sa, _ea)
            self.modified()

    end_angle = property(getEndAngle, setEndAngle, None,
                         "End angle for the Arc.")

    def getAngle(self):
        """Return the angular sweep of the Arc.

getAngle()
        """
        _sa = self.__sa
        _ea = self.__ea
        if abs(_ea - _sa) < 1e-10:
            _angle = 360.0
        elif _ea > _sa:
            _angle = _ea - _sa
        else:
            _angle = 360.0 - _sa + _ea
        return _angle

    def throughAngle(self, angle):
        """Return True if an arc passes through some angle

throughAngle(angle)

The argument angle should be a float value. This method returns
True if the arc exists at that angle, otherwise the method returns False.
        """
        _angle = math.fmod(util.get_float(angle), 360.0)
        if _angle < 0.0:
            _angle = _angle + 360.0
        _sa = self.__sa
        _ea = self.__ea
        _val = True
        if abs(_sa - _ea) > 1e-10:
            if _sa > _ea:
                if _angle > _ea and _angle < _sa:
                    _val = False
            else:
                if _angle > _ea or _angle < _sa:
                    _val = False
        return _val

    def getEndpoints(self):
        """Return where the two endpoints for the arc-segment lie.

getEndpoints(self)

This function returns two tuples, each containing the x-y coordinates
of the arc endpoints. The first tuple corresponds to the endpoint at
the start_angle, the second to the endpoint at the end_angle.
        """
        _cx, _cy = self.__center.getCoords()
        _r = self.__radius
        _sa = self.__sa
        _sax = _cx + _r * math.cos(_sa * _dtr)
        _say = _cy + _r * math.sin(_sa * _dtr)
        _ea = self.__ea
        _eax = _cx + _r * math.cos(_ea * _dtr)
        _eay = _cy + _r * math.sin(_ea * _dtr)
        return (_sax, _say), (_eax, _eay)

    def length(self):
        """Return the length of the Arc.

length()
        """
        return 2.0 * math.pi * self.__radius * (self.getAngle()/360.0)

    def area(self):
        """Return the area enclosed by the Arc.

area()
        """
        return math.pi * pow(self.__radius, 2) * (self.getAngle()/360.0)

    def move(self, dx, dy):
        """Move a Arc.

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
            self.sendMessage('moved', _x, _y, self.__radius,
                             self.__sa, self.__ea)

    def mapCoords(self, x, y, tol=tolerance.TOL):
        """Return the nearest Point on the Arc to a coordinate pair.

mapCoords(x, y[, tol])

The function has two required arguments:

x: A Float value giving the x-coordinate
y: A Float value giving the y-coordinate

There is a single optional argument:

tol: A float value equal or greater than 0.0

This function is used to map a possibly near-by coordinate pair to
an actual Point on the Arc. If the distance between the actual
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
            _ra = math.atan2((_y - _cy), (_x - _cx))
            _da = _ra * _rtd
            if _da < 0.0:
                _da = _da + 360.0
            if self.throughAngle(_da):
                _xoff = _r * math.cos(_ra)
                _yoff = _r * math.sin(_ra)
                return (_cx + _xoff), (_cy + _yoff)
        return None
    
    def GetTangentPoint(self,x,y,outx,outy):
        """
            Get the tangent from an axternal point
            args:
                x,y is a point near the circle
                xout,yout is a point far from the circle
            return:
                a tuple(x,y,x1,xy) that define the tangent line
        """
        firstPoint=point.Point(x,y)
        fromPoint=point.Point(outx,outy)
        twoPointDistance=self.__center.Dist(fromPoint)
        if(twoPointDistance<self.__radius):
            return None,None
        originPoint=point.Point(0.0,0.0)        
        tanMod=math.sqrt(pow(twoPointDistance,2)-pow(self.__radius,2))
        tgAngle=math.asin(self.__radius/twoPointDistance)
        #Compute the x versor
        xPoint=point.Point(1.0,0.0)
        xVector=Vector(originPoint,xPoint)
        twoPointVector=Vector(fromPoint,self.__center)
        rightAngle=twoPointVector.Ang(xVector)                
        cx,cy=self.__center.getCoords()        
        if(outy>cy): #stupid situation 
            rightAngle=-rightAngle
        posAngle=rightAngle+tgAngle
        negAngle=rightAngle-tgAngle
        #Compute the Positive Tangent
        xCord=math.cos(posAngle)
        yCord=math.sin(posAngle)
        dirPoint=point.Point(xCord,yCord)#Versor that point at the tangentPoint
        ver=Vector(originPoint,dirPoint)
        ver.Mult(tanMod)
        tangVectorPoint=ver.Point()
        posPoint=point.Point(tangVectorPoint+(outx,outy))
        #Compute the Negative Tangent
        xCord=math.cos(negAngle)
        yCord=math.sin(negAngle)
        dirPoint=point.Point(xCord,yCord)#Versor that point at the tangentPoint
        ver=Vector(originPoint,dirPoint)
        ver.Mult(tanMod)
        tangVectorPoint=ver.Point()
        negPoint=point.Point(tangVectorPoint+(outx,outy))
        if(firstPoint.Dist(posPoint)<firstPoint.Dist(negPoint)):
            return posPoint.getCoords()     
        else:
            return negPoint.getCoords()    
    def GetRadiusPointFromExt(self,x,y):
        """
            get The intersecrion point from the line(x,y,cx,cy) and the circle
        """
        _cx, _cy = self.__center.getCoords()
        _r = self.__radius
        centerPoint=point.Point(_cx,_cy)
        outPoint=point.Point(x,y)
        vector=Vector(outPoint,centerPoint)
        vNorm=vector.Norm()
        newNorm=abs(vNorm-_r)
        magVector=vector.Mag()
        magVector.Mult(newNorm)
        newPoint=magVector.Point()
        intPoint=point.Point(outPoint+newPoint)
        return intPoint.getCoords()     
    
    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not an Arc exists within a region.

inRegion(xmin, ymin, xmax, ymax[, fully])

The first four arguments define the boundary. The optional
fifth argument fully indicates whether or not the Arc
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
        # cheap test to see if arc cannot be in region
        #
        _axmin, _aymin, _axmax, _aymax = self.getBounds()
        if ((_axmin > _xmax) or
            (_aymin > _ymax) or
            (_axmax < _xmin) or
            (_aymax < _ymin)):
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
            # arc must be visible - the center is in
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
            # if all bits are set then distance from arc center
            # to region endpoints is less than radius - arc
            # entirely outside the region
            #
            _val = not ((_bits == 0xff) or fully)
            #
            # if the test value is still true, check that the
            # arc boundary can overlap with the region
            #
            if _val:
                _ep1, _ep2 = self.getEndpoints()
                _axmin = min(_xc, _ep1[0], _ep2[0])
                if self.throughAngle(180.0):
                    _axmin = _xc - _r
                if _axmin > _xmax:
                    return False
                _aymin = min(_yc, _ep1[1], _ep2[1])
                if self.throughAngle(270.0):
                    _aymin = _yc - _r
                if _aymin > _ymax:
                    return False
                _axmax = max(_xc, _ep1[0], _ep2[0])
                if self.throughAngle(0.0):
                    _axmax = _xc + _r
                if _axmax < _xmin:
                    return False
                _aymax = max(_yc, _ep1[1], _ep2[1])
                if self.throughAngle(90.0):
                    _aymax = _yc + _r
                if _aymax < _ymin:
                    return False
        return _val

    def getBounds(self):
        _ep1, _ep2 = self.getEndpoints()
        _xc, _yc = self.__center.getCoords()
        _r = self.__radius
        _xmin = min(_xc, _ep1[0], _ep2[0])
        _ymin = min(_yc, _ep1[1], _ep2[1])
        _xmax = max(_xc, _ep1[0], _ep2[0])
        _ymax = max(_yc, _ep1[1], _ep2[1])
        if self.throughAngle(0.0):
            _xmax = _xc + _r
        if self.throughAngle(90.0):
            _ymax = _yc + _r
        if self.throughAngle(180.0):
            _xmin = _xc - _r
        if self.throughAngle(270.0):
            _ymin = _yc - _r
        return _xmin, _ymin, _xmax, _ymax

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
            raise ValueError, "Point is not arc center: " + `p`
        _x, _y = _cp.getCoords()
        self.sendMessage('moved', _x, _y, self.__radius, self.__sa, self.__ea)

    def clone(self):
        """Create an identical copy of a Arc

clone()
        """
        _cp = self.__center.clone()
        _r = self.__radius
        _sa = self.__sa
        _ea = self.__ea
        _st = self.getStyle()
        _lt = self.getLinetype()
        _col = self.getColor()
        _th = self.getThickness()
        return Arc(_cp, _r, _sa, _ea, _st, _lt, _col, _th)

    def sendsMessage(self, m):
        if m in Arc.__messages:
            return True
        return super(Arc, self).sendsMessage(m)


#
# static functions for Arc class
#

    def test_angle(s, e, a):
        """Returns if an angle lies between the start and end angle of an arc.

test_angle(s, e, a)

The arguments are:

s: arc start angle
e: arc end angle
a: angle being tested
        """
        _val = False
        if ((abs(e - s) < 1e-10) or
            ((s > e) and
             ((s <= a <= 360.0) or (0.0 <= a <= e))) or
            (s <= a <= e)):
            _val = True
        return _val

    test_angle = staticmethod(test_angle)

#
# Quadtree Arc storage
#

class ArcQuadtree(quadtree.Quadtree):
    def __init__(self):
        super(ArcQuadtree, self).__init__()

    def getNodes(self, *args):
        _alen = len(args)
        if _alen != 4:
            raise ValueError, "Expected 4 arguments, got %d" % _alen
        _axmin = util.get_float(args[0])
        _aymin = util.get_float(args[1])
        _axmax = util.get_float(args[2])
        if not _axmax > _axmin:
            raise ValueError, "xmax not greater than xmin"
        _aymax = util.get_float(args[3])
        if not _aymax > _aymin:
            raise ValueError, "ymax not greater than ymin"
        _nodes = [self.getTreeRoot()]
        while len(_nodes):
            _node = _nodes.pop()
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if ((_axmin > _xmax) or
                (_axmax < _xmin) or
                (_aymin > _ymax) or
                (_aymax < _ymin)):
                continue
            if _node.hasSubnodes():
                _xmid = (_xmin + _xmax)/2.0
                _ymid = (_ymin + _ymax)/2.0
                _ne = _nw = _sw = _se = True
                if _axmax < _xmid: # arc on left side
                    _ne = _se = False
                if _axmin > _xmid: # arc on right side
                    _nw = _sw = False
                if _aymax < _ymid: # arc below
                    _nw = _ne = False
                if _aymin > _ymid: # arc above
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
        if not isinstance(obj, Arc):
            raise TypeError, "Invalid Arc object: " + `obj`
        if obj in self:
            return
        _bounds = self.getTreeRoot().getBoundary()
        _xmin = _ymin = _xmax = _ymax = None
        _axmin, _aymin, _axmax, _aymax = obj.getBounds()
        _resize = False
        if _bounds is None: # first node in tree
            _resize = True
            _xmin = _axmin - 1.0
            _ymin = _aymin - 1.0
            _xmax = _axmax + 1.0
            _ymax = _aymax + 1.0
        else:
            _xmin, _ymin, _xmax, _ymax = _bounds
            if _axmin < _xmin:
                _xmin = _axmin - 1.0
                _resize = True
            if _axmax > _xmax:
                _xmax = _axmax + 1.0
                _resize = True
            if _aymin < _ymin:
                _ymin = _aymin - 1.0
                _resize = True
            if _aymax > _ymax:
                _ymax = _aymax + 1.0
                _resize = True
        if _resize:
            self.resize(_xmin, _ymin, _xmax, _ymax)
        for _node in self.getNodes(_axmin, _aymin, _axmax, _aymax):
            _xmin, _ymin, _xmax, _ymax = _node.getBoundary()
            if obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _node.addObject(obj)
        super(ArcQuadtree, self).addObject(obj)        
        obj.connect('moved', self._moveArc)

    def delObject(self, obj):
        if obj not in self:
            return
        _axmin, _aymin, _axmax, _aymax = obj.getBounds()
        _pdict = {}
        for _node in self.getNodes(_axmin, _aymin, _axmax, _aymax):
            _node.delObject(obj) # arc may not be in the node ...
            _parent = _node.getParent()
            if _parent is not None:
                _pid = id(_parent)
                if _pid not in _pdict:
                    _pdict[_pid] = _parent
        super(ArcQuadtree, self).delObject(obj)
        obj.disconnect(self)
        for _parent in _pdict.values():
            self.purgeSubnodes(_parent)

    def find(self, *args):
        _alen = len(args)
        if _alen < 5:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        _sa = util.get_float(args[3])
        _ea = util.get_float(args[4])
        _t = tolerance.TOL
        if _alen > 5:
            _t = tolerance.toltest(args[5])
        _axmin = _x - _r - _t
        _axmax = _x + _r + _t
        _aymin = _y - _r - _t
        _aymax = _y + _r + _t
        _arcs = []
        for _arc in self.getInRegion(_axmin, _aymin, _axmax, _aymax):
            _cx, _cy = _arc.getCenter().getCoords()
            if ((abs(_cx - _x) < _t) and
                (abs(_cy - _y) < _t) and
                (abs(_arc.getRadius() - _r) < _t) and
                (abs(_arc.getStartAngle() - _sa) < 1e-10) and
                (abs(_arc.getEndAngle() - _ea) < 1e-10)):
                _arcs.append(_arc)
        return _arcs

    def _moveArc(self, obj, *args):
        if obj not in self:
            raise ValueError, "Arc not stored in Quadtree: " + `obj`
        _alen = len(args)
        if _alen < 5:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x = util.get_float(args[0])
        _y = util.get_float(args[1])
        _r = util.get_float(args[2])
        _sa = util.get_float(args[3])
        _ea = util.get_float(args[4])
        _sax = _x + _r * math.cos(_sa * _dtr)
        _say = _y + _r * math.sin(_sa * _dtr)
        _eax = _x + _r * math.cos(_ea * _dtr)
        _eay = _y + _r * math.sin(_ea * _dtr)
        _axmin = min(_x, _sax, _eax)
        if ((abs(_sa - 180.0) < 1e-10) or
            (abs(_ea - 180.0) < 1e-10) or
            ((_sa < _ea) and (_sa < 180.0 < _ea)) or
            ((_ea < _sa) and (_sa < 180.0))):
            _axmin = _x - _r
        _axmax = max(_x, _sax, _eax)
        if ((abs(_sa) < 1e-10) or
            (abs(_ea) < 1e-10) or
            ((_sa > _ea) and (_ea > 0.0))):
            _axmax = _x + _r
        _aymin = min(_y, _say, _eay)
        if ((abs(_sa - 270.0) < 1e-10) or
            (abs(_ea - 270.0) < 1e-10) or
            ((_sa < _ea) and (_sa < 270.0 < _ea)) or
            ((_ea < _sa) and (_sa < 270.0))):
            _aymin = _y - _r
        _aymax = max(_y, _say, _eay)
        if ((abs(_sa - 90.0) < 1e-10) or
            (abs(_ea - 90.0) < 1e-10) or
            ((_sa < _ea) and (_sa < 90.0 < _ea)) or
            ((_ea < _sa) and (_sa < 90.0))):
            _aymax = _y + _r
        for _node in self.getNodes(_axmin, _aymin, _axmax, _aymax):
            _node.delObject(obj) # arc may not be in node ...
        super(ArcQuadtree, self).delObject(obj)
        obj.disconnect(self)
        self.addObject(obj)

    def getClosest(self, x, y, tol=tolerance.TOL):
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = tolerance.toltest(tol)
        _arc = _tsep = None
        _bailout = False
        _adict = {}
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
                for _a in _node.getObjects():
                    _aid = id(_a)
                    if _aid not in _adict:
                        _ap = _a.mapCoords(_x, _y, _t)
                        if _ap is not None:
                            _ax, _ay = _ap
                            _sep = math.hypot((_ax - _x), (_ay - _y))
                            if _tsep is None:
                                _tsep = _sep
                                _arc = _a
                            else:
                                if _sep < _tsep:
                                    _tsep = _sep
                                    _arc = _a
                            if _sep < 1e-10 and _arc is not None:
                                _bailout = True
                                break
            if _bailout:
                break
        return _arc

    def getInRegion(self, xmin, ymin, xmax, ymax):
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if _xmax < _xmin:
            raise ValueError, "Illegal values: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Illegal values: ymax < ymin"
        _arcs = []
        if not len(self):
            return _arcs
        _nodes = [self.getTreeRoot()]
        _adict = {}
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
                for _arc in _node.getObjects():
                    _aid = id(_arc)
                    if _aid not in _adict:
                        if _arc.inRegion(_xmin, _ymin, _xmax, _ymax):
                            _arcs.append(_arc)
                        _adict[_aid] = True
        return _arcs

#
# Arc history class
#

class ArcLog(graphicobject.GraphicObjectLog):
    def __init__(self, a):
        if not isinstance(a, Arc):
            raise TypeError, "Invalid arc: " + `a`
        super(ArcLog, self).__init__(a)
        a.connect('center_changed' ,self.__centerChanged)
        a.connect('radius_changed', self.__radiusChanged)
        a.connect('start_angle_changed', self.__saChanged)
        a.connect('end_angle_changed', self.__eaChanged)

    def __radiusChanged(self, a, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _r = args[0]
        if not isinstance(_r, float):
            raise TypeError, "Unexpecte type for radius: " + `type(_r)`
        self.saveUndoData('radius_changed', _r)

    def __centerChanged(self, a, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _old = args[0]
        if not isinstance(_old, point.Point):
            raise TypeError, "Invalid old center point: " + `_old`
        self.saveUndoData('center_changed', _old.getID())

    def __saChanged(self, a, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _sa = args[0]
        if not isinstance(_sa, float):
            raise TypeError, "Unexpected type for angle: " + `type(_sa)`
        self.saveUndoData('start_angle_changed', _sa)

    def __eaChanged(self, a, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _ea = args[0]
        if not isinstance(_ea, float):
            raise TypeError, "Unexpected type for angle: " + `type(_ea)`
        self.saveUndoData('end_angle_changed', _ea)

    def execute(self, undo, *args):
        #
        # fixme - deal with the endpoints ...
        #
        def _used_by(obj, plist):
            _objpt = None
            for _pt in plist:
                for _user in _pt.getUsers():
                    if _user is obj:
                        _objpt = _pt
                        break
                if _objpt is not None:
                    break
            return _objpt
        def _most_used(plist):
            _pmax = plist.pop()
            _max = _pmax.countUsers()
            for _pt in plist:
                _count = _pt.countUsers()
                if _count > _max:
                    _max = _count
                    _pmax = _pt
            return _pmax
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _a = self.getObject()
        _cp = _a.getCenter()
        _op = args[0]
        if _op == 'center_changed':
            if _alen < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _oid = args[1]
            _parent = _a.getParent()
            if _parent is None:
                raise ValueError, "Arc has no parent - cannot undo"
            _pt = _parent.getObject(_oid)
            if _pt is None or not isinstance(_pt, point.Point):
                raise ValueError, "Center point missing: id=%d" % _oid
            _ep1, _ep2 = _a.getEndpoints()
            _pts = _parent.find('point', _ep1[0], _ep1[1])
            _ep = _used_by(_a, _pts)
            assert _ep is not None, "Arc endpoint not found in layer"
            _ep.freeUser(_a)
            _pts = _parent.find('point', _ep2[0], _ep2[1])
            _ep = _used_by(_a, _pts)
            assert _ep is not None, "Arc endpoint not found in layer"
            _ep.freeUser(_a)
            _sdata = _cp.getID()
            self.ignore(_op)
            try:
                if undo:
                    _a.startUndo()
                    try:
                        _a.setCenter(_pt)
                    finally:
                        _a.endUndo()
                else:
                    _a.startRedo()
                    try:
                        _a.setCenter(_pt)
                    finally:
                        _a.endRedo()
            finally:
                self.receive(_op)
            _ep1, _ep2 = _a.getEndpoints()
            _pts = _parent.find('point', _ep1[0], _ep1[1])
            _ep = _most_used(_pts)
            _ep.storeUser(_a)
            _pts = _parent.find('point', _ep2[0], _ep2[1])
            _ep = _most_used(_pts)
            _ep.storeUser(_a)
            self.saveData(undo, _op, _sdata)
        elif _op == 'radius_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _r = args[1]
            if not isinstance(_r, float):
                raise TypeError, "Unexpected type for radius: " + `type(_r)`
            _sdata = _a.getRadius()
            self.ignore(_op)
            try:
                if undo:
                    _a.startUndo()
                    try:
                        _a.setRadius(_r)
                    finally:
                        _a.endUndo()
                else:
                    _a.startRedo()
                    try:
                        _a.setRadius(_r)
                    finally:
                        _a.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'start_angle_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sa = args[1]
            if not isinstance(_sa, float):
                raise TypeError, "Unexpected type for angle: " + `type(_sa)`
            _sdata = _a.getStartAngle()
            self.ignore(_op)
            try:
                if undo:
                    _a.startUndo()
                    try:
                        _a.setStartAngle(_sa)
                    finally:
                        _a.endUndo()
                else:
                    _a.startRedo()
                    try:
                        _a.setStartAngle(_sa)
                    finally:
                        _a.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'end_angle_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _ea = args[1]
            if not isinstance(_ea, float):
                raise TypeError, "Unexpected type for angle: " + `type(_ea)`
            _sdata = _a.getEndAngle()
            self.ignore(_op)
            try:
                if undo:
                    _a.startUndo()
                    try:
                        _a.setEndAngle(_ea)
                    finally:
                        _a.endUndo()
                else:
                    _a.startRedo()
                    try:
                        _a.setEndAngle(_ea)
                    finally:
                        _a.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(ArcLog, self).execute(undo, *args)
