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

from point import Point
#from PythonCAD.Generic.pyGeoLib import Vector

_dtr = math.pi/180.0
_rtd = 180.0/math.pi

class Arc(object):
    """
        A class for Arcs.
        An Arc has four attributes:
        center: A Point object
        radius: The Arc's radius
        start_angle: The start angle
        end_angle: The end angle

        An Arc has the following methods:
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
        if not isinstance(_cp, Point):
            _cp = Point(center)
        #_r = util.get_float(radius)
        _r = float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        _st = st
        _sa = util.make_c_angle(start_angle)
        _ea = util.make_c_angle(end_angle)
        self.__radius = _r
        self.__sa = _sa
        self.__ea = _ea
        self.__center = _cp
        #_cp.connect('moved', self.__movePoint)
        #_cp.connect('change_pending', self.__pointChangePending)
        #_cp.connect('change_complete', self.__pointChangeComplete)
        #_cp.storeUser(self)
        self.isLocked=False

    def getConstructionElements(self):
        """
            Get the endpoints of the Arc.
            This function returns a tuple containing the Point objects
            that for inizializing the arc
        """
        return self._cp, self._r,self._sa,self._ea

    def __eq__(self, obj):
        """
            Compare a Arc to another for equality.
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
        """
            Compare a Arc to another for inequality.
        """
        if not isinstance(obj, Arc):
            return True
        if obj is self:
            return False
        return ((self.__center != obj.getCenter()) or
                (abs(self.__radius - obj.getRadius()) > 1e-10) or
                (abs(self.__sa - obj.getStartAngle()) > 1e-10) or
                (abs(self.__ea - obj.getEndAngle()) > 1e-10))

    def finish(self):
        self.__center.disconnect(self)
        self.__center.freeUser(self)
        self.__center = self.__radius = self.__sa = self.__ea = None

    def getValues(self):
        """
            Return values comprising the Arc.
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
        """
            Return the center Point of the Arc.
        """
        return self.__center

    def setCenter(self, c):
        """
            Set the center Point of the Arc.
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
        """
            Return the radius of the the Arc.
        """
        return self.__radius

    def setRadius(self, radius):
        """
            Set the radius of the Arc.
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
        """
            Return the start_angle for the Arc.
        """
        return self.__sa

    def setStartAngle(self, angle):
        """
            Set the start_angle for the Arc.
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
        """
            Return the end_angle for the Arc.
        """
        return self.__ea

    def setEndAngle(self, angle):
        """
            Set the end_angle for the Arc.
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
        """
            Return the angular sweep of the Arc.

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
        """
            Return True if an arc passes through some angle
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
        """
            Return where the two endpoints for the arc-segment lie.
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
        """
            Return the length of the Arc.
        """
        return 2.0 * math.pi * self.__radius * (self.getAngle()/360.0)

    def area(self):
        """
            Return the area enclosed by the Arc.
        """
        return math.pi * pow(self.__radius, 2) * (self.getAngle()/360.0)

    def move(self, dx, dy):
        """
            Move a Arc.
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

    def GetTangentPoint(self,x,y,outx,outy):
        """
            Get the tangent from an axternal point
            args:
                x,y is a point near the circle
                xout,yout is a point far from the circle
            return:
                a tuple(x,y,x1,xy) that define the tangent line
        """
        firstPoint=Point(x,y)
        fromPoint=Point(outx,outy)
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
        """
            Return whether or not an Arc exists within a region.

            inRegion(xmin, ymin, xmax, ymax[, fully])

            The first four arguments define the boundary. The optional
            fifth argument fully indicates whether or not the Arc
            must be completely contained within the region or just pass
            through it.
        """
        #TODO : May be we need to delete this ...
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
        """
            Create an identical copy of a Arc
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

#    def sendsMessage(self, m):
#        if m in Arc.__messages:
#            return True
#        return super(Arc, self).sendsMessage(m)


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

