#
# Copyright (c) 2009 Matteo Boscolo
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
# class stuff for all circle entitys 
#
from __future__ import generators

import math

from PythonCAD.Generic import tolerance
from PythonCAD.Generic.point import Point
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import util
from PythonCAD.Generic import tangent
from PythonCAD.Generic.pyGeoLib import Vector

class StrCircle(object):
    """
        This Class manage the default abstract circle entitys
    """
    def __init__(self, c, r):
        print "Debug: Init StrCircle"
        self.center=c
        self.radius=r

    def __eq__(self, obj):
        """
            Compare a Circle to another for equality.
        """
        if not isinstance(obj, StrCircle):
            return False
        if obj is self:
            return True
        return (self.center == obj.getCenter() and
                abs(self.radius - obj.getRadius()) < 1e-10)

    def __ne__(self, obj):
        """
            Compare a Circle to another for inequality.
        """
        if not isinstance(obj, StrCircle):
            return True
        if obj is self:
            return False
        return (self.center != obj.getCenter() or
                abs(self.radius - obj.getRadius()) > 1e-10)
    
    def getCenter(self):
        """
            Return the center Point of the Circle.
        """
        print "Debug: GetCenter"
        return self._center
    def setCenter(self,p):
        """
            set the radius center
        """
        print "Debug: setCenetr"
        if not isinstance(p, Point):
            if isinstance(p,tuple):
                p=Point(p)
            else:            
                raise TypeError, "Invalid center point: " + `type(p)`
        self._center=p

    def getRadius(self):
        """
            Return the radius of the the Circle.
        """
        print "Debug: getRadius"
        return self._radius 

    def setRadius(self, radius):
        """
            Set the radius of the Circle.
            The argument must be float value greater than 0.
        """
        print "Debug: setRadius"
        _r = util.get_float(radius)
        if not _r > 0.0:
            raise ValueError, "Invalid radius: %g" % _r
        self._radius=_r

    def circumference(self):
        """
            Return the circumference of the Circle.
        """
        return 2.0 * math.pi * self._radius

    def area(self):
        """
            Return the area enclosed by the Circle.
        """
        return math.pi * pow(self._radius, 2)

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
        twoPointDistance=self._center.Dist(fromPoint)
        if(twoPointDistance<self._radius):
            return None,None
        originPoint=point.Point(0.0,0.0)        
        tanMod=math.sqrt(pow(twoPointDistance,2)-pow(self._radius,2))
        tgAngle=math.asin(self._radius/twoPointDistance)
        #Compute the x versor
        xPoint=Point(1.0,0.0)
        xVector=Vector(originPoint,xPoint)
        twoPointVector=Vector(fromPoint,self._center)
        rightAngle=twoPointVector.Ang(xVector)                
        cx,cy=self._center.getCoords()        
        if(outy>cy): #stupid situation 
            rightAngle=-rightAngle
        posAngle=rightAngle+tgAngle
        negAngle=rightAngle-tgAngle
        #Compute the Positive Tangent
        xCord=math.cos(posAngle)
        yCord=math.sin(posAngle)
        dirPoint=Point(xCord,yCord)#Versor that point at the tangentPoint
        ver=Vector(originPoint,dirPoint)
        ver.Mult(tanMod)
        tangVectorPoint=ver.Point()
        posPoint=Point(tangVectorPoint+(outx,outy))
        #Compute the Negative Tangent
        xCord=math.cos(negAngle)
        yCord=math.sin(negAngle)
        dirPoint=Point(xCord,yCord)#Versor that point at the tangentPoint
        ver=Vector(originPoint,dirPoint)
        ver.Mult(tanMod)
        tangVectorPoint=ver.Point()
        negPoint=Point(tangVectorPoint+(outx,outy))
        if(firstPoint.Dist(posPoint)<firstPoint.Dist(negPoint)):
            return posPoint.getCoords()     
        else:
            return negPoint.getCoords()        

    def GetRadiusPointFromExt(self,x,y):
        """
            get The intersecrion point from the line(x,y,cx,cy) and the circle
        """
        _cx, _cy = self._center.getCoords()
        _r = self._radius
        centerPoint=Point(_cx,_cy)
        outPoint=Point(x,y)
        vector=Vector(outPoint,centerPoint)
        vNorm=vector.Norm()
        newNorm=abs(vNorm-_r)
        magVector=vector.Mag()
        magVector.Mult(newNorm)
        newPoint=magVector.Point()
        intPoint=Point(outPoint+newPoint)
        return intPoint.getCoords()        
    
    def mapCoords(self, x, y, tol=tolerance.TOL):
        """
            Return the nearest Point on the Circle to a coordinate pair.
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
        _cx, _cy = self._center.getCoords()
        _r = self._radius
        _dist = math.hypot((_x - _cx), (_y - _cy))
        if abs(_dist - _r) < _t:
            _angle = math.atan2((_y - _cy),(_x - _cx))
            _xoff = _r * math.cos(_angle)
            _yoff = _r * math.sin(_angle)
            return (_cx + _xoff), (_cy + _yoff)
        return None

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return whether or not an Circle exists within a region.
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
        _xc, _yc = self._center.getCoords()
        _r = self._radius
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
    #
    # Properties
    #
    center = property(getCenter, setCenter, None, "Circle center")
    radius = property(getRadius, setRadius, None, "Circle radius")