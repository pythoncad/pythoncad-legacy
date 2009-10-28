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
# code for chamfer and fillet objects
#

from math import hypot, pi, sin, cos, tan, atan2

from PythonCAD.Generic import baseobject
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import intersections
from PythonCAD.Generic import segment
from PythonCAD.Generic import style
from PythonCAD.Generic import linetype
from PythonCAD.Generic import color
from PythonCAD.Generic import util

_dtr = 180.0/pi

class SegJoint(graphicobject.GraphicObject):
    """A base class for chamfers and fillets

A SegJoint object has the following methods:

validate(): Check the two segments can intersect.
getSegments(): Get the two segments joined by the SegJoint object.
getMovingPoints(): Get the segment points used by the SegJoint object.
getFixedPoints(): Get the segment points not used by the SegJoint object.
update(): Recheck the SegJoint's validity.
getIntersection(): Get the intersection point of the joined segments.
inRegion(): Determine if a SegJoint is located in some area.
    """

    #
    # The default style for the Segjoint class
    #

    __defstyle = None
    
    def __init__(self, s1, s2, st=None, lt=None, col=None, t=None, **kw):
        if not isinstance(s1, segment.Segment):
            raise TypeError, "Invalid first Segment for SegJoint: " + `type(s1)`
        if not isinstance(s2, segment.Segment):
            raise TypeError, "Invalid second Segment for SegJoint: " + `type(s2)`
        _st = st
        if _st is None:
            _st = self.getDefaultStyle()
        super(SegJoint, self).__init__(_st, lt, col, t, **kw)
        self.__s1 = s1
        self.__s2 = s2
        self.__xi = None # segment intersection x-coordinate
        self.__yi = None # segment intersection y-coordinate
        self.__s1_float = None # s1 endpoint at joint
        self.__s1_fixed = None # s1 other endpoint
        self.__s2_float = None # s2 endpoint at joint
        self.__s2_fixed = None # s2 other endpoint
        SegJoint.validate(self)
        s1.storeUser(self)
        # s1.connect('moved', self._moveSegment)
        # s1.connect('change_pending', self._segmentChanging')
        s2.storeUser(self)
        # s2.connect('moved', self._moveSegment)
        # s2.connect('change_pending', self._segmentChanging')

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Segjoint Default Style',
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
        self.__s1.disconnect(self)
        self.__s1.freeUser(self)
        self.__s2.disconnect(self)
        self.__s2.freeUser(self)
        self.__s1 = self.__s2 = None
        super(SegJoint, self).finish()

    def setStyle(self, s):
        """Set the Style of the SegJoint.

setStyle(s)

This method extends GraphicObject::setStyle().
        """
        _s = s
        if _s is None:
            _s = self.getDefaultStyle()
        super(SegJoint, self).setStyle(_s)

    def validate(self):
        """
            Check that the two segments can intersect.
        """
        _p1, _p2 = self.__s1.getEndpoints()
        _p3, _p4 = self.__s2.getEndpoints()
        if _p1 is _p3 or _p2 is _p3 or _p1 is _p4 or _p2 is _p4:
            raise ValueError, "Shared segment endpoints in s1 and s2"
        _denom = intersections.denom(_p1, _p2, _p3, _p4)
        if abs(_denom) < 1e-10: # parallel
            raise ValueError, "Segments are parallel"
        _rn = intersections.rnum(_p1, _p2, _p3, _p4)
        # print "rn: %g" % _rn
        _sn = intersections.snum(_p1, _p2, _p3, _p4)
        # print "sn: %g" % _sn
        _r = _rn/_denom
        _s = _sn/_denom
        if 0.0 < _r < 1.0 or 0.0 < _s < 1.0:
            raise ValueError, "Invalid segment intersection point"
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        self.__xi = _x1 + _r * (_x2 - _x1) # intersection "x" coordinate
        self.__yi = _y1 + _r * (_y2 - _y1) # intersection "y" coordinate
        # print "xi: %g; yi: %g" % (self.__xi, self.__yi)
        if _r < 1e-10:
            self.__s1_fixed = _p2
            self.__s1_float = _p1
        else:
            self.__s1_fixed = _p1
            self.__s1_float = _p2
        if _s < 1e-10:
            self.__s2_fixed = _p4
            self.__s2_float = _p3
        else:
            self.__s2_fixed = _p3
            self.__s2_float = _p4

    def getSegments(self):
        """Return the two segments joined by the SegJoint.

getSegments()

This method returns a tuple holding the two segments joined
by the SegJoint.
        """
        return self.__s1, self.__s2

    def getMovingPoints(self):
        """Return the joined segment points used by the SegJoint.

getMovingPoints()

This method returns a tuple of two points, the first point is the
used point on the SegJoint initial segment, and the second point
is the used point on the SegJoint secondary segment.
        """
        return self.__s1_float, self.__s2_float

    def getFixedPoints(self):
        """Return the joined segment points not used by the SegJoint.

getFixedPoints()

This method returns a tuple of two points, the first point is the
unused point on the SegJoint initial segment, and the second point
is the unused point on the SegJoint secondary segment.
        """
        return self.__s1_fixed, self.__s2_fixed

    def update(self):
        """Revalidate the SegJoint if it is modified.

update()
        """
        if self.isModified():
            self.validate()
            self.reset()

    def getIntersection(self):
        """Return the intersection points of the SegJoint segments.

getIntersection()

This method returns a tuple of two floats; the first is the
intersection 'x' coordinate, and the second is the 'y' coordinate.
        """
        self.update()
        return self.__xi, self.__yi

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not a segjoint exists with a region.

isRegion(xmin, ymin, xmax, ymax)

The four arguments define the boundary of an area, and the
function returns True if the joint lies within that area.
Otherwise, the function returns False.
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
        _mp1, _mp2 = self.getMovingPoints()
        _mx1, _my1 = _mp1.getCoords()
        _mx2, _my2 = _mp2.getCoords()
        _fxmin = min(_mx1, _mx2)
        _fymin = min(_my1, _my2)
        _fxmax = max(_mx1, _mx2)
        _fymax = max(_my1, _my2)
        if ((_fxmax < _xmin) or
            (_fymax < _ymin) or
            (_fxmin > _xmax) or
            (_fymin > _ymax)):
            return False
        if fully:
            if ((_fxmin > _xmin) and
                (_fymin > _ymin) and
                (_fxmax < _xmax) and
                (_fymax < _ymax)):
                return True
            return False
        return util.in_region(_mx1, _my1, _mx2, _my2,
                              _xmin, _ymin, _xmax, _ymax)

    def _moveSegment(self, s, *args):
        _alen = len(args)
        if _alen < 4:
            raise ValueError, "Invalid argument count: %d" % _alen
        _x1 = util.get_float(args[0])
        _y1 = util.get_float(args[1])
        _x2 = util.get_float(args[2])
        _y2 = util.get_float(args[3])
        #
        # would it be better to resize the joint or to remove it?
        # we pass for now ...
        #
        if s is self.__s1:
            pass
        elif s is self.__s2:
            pass
        else:
            raise ValueError, "Unexpected segment in moveSegment" + `s`

    def getValues(self):
        """Return values comprising the SegJoint.

getValues()

This method extends the GraphicObject::getValues() method.
        """
        _data = super(SegJoint, self).getValues()
        return _data

class Chamfer(SegJoint):
    """A Chamfer class

A chamfer is a small distance taken off a sharp
corner in a drawing. For the chamfer to be valid,
the chamfer length must be less than the length of
either segment, and the two segments must be extendable
so they could share a common endpoint.

A Chamfer is derived from a SegJoint, so it shares all
the methods and attributes of that class. A Chamfer has
the following additional methods:

{set/get}Length(): Set/Get the Chamfer length.

A Chamfer has the following attributes:

length: The Chamfer length.
    """

    __defstyle = None
    
    __messages = {
        'length_changed' : True,
        'moved' : True
        }
    
    def __init__(self, s1, s2, l, st=None, lt=None, col=None, t=None, **kw):
        super(Chamfer, self).__init__(s1, s2, st, lt, col, t, **kw)
        _len = util.get_float(l)
        if _len < 0.0:
            raise ValueError, "Invalid chamfer length: %g" % _len
        if _len > s1.length():
            raise ValueError, "Chamfer is longer than first Segment."
        if _len > s2.length():
            raise ValueError, "Chamfer is longer than second Segment."
        _xi, _yi = SegJoint.getIntersection(self)
        # print "xi: %g; yi: %g" % (_xi, _yi)
        _sp1, _sp2 = SegJoint.getMovingPoints(self)
        _xp, _yp = _sp1.getCoords()
        _sep = hypot((_yp - _yi), (_xp - _xi))
        if _sep > (_len + 1e-10):
            # print "sep: %g" % _sep
            # print "xp: %g; yp: %g" % (_xp, _yp)
            raise ValueError, "First segment too far from intersection point."
        _xp, _yp = _sp2.getCoords()
        _sep = hypot((_yp - _yi), (_xp - _xi))
        if _sep > (_len + 1e-10):
            # print "sep: %g" % _sep
            # print "xp: %g; yp: %g" % (_xp, _yp)
            raise ValueError, "Second segment too far from intersection point."
        self.__length = _len
        self.ignore('moved')
        try:
            self._moveSegmentPoints(_len)
        finally:
            self.receive('moved')

    def finish(self):
        self.__length = None
        super(Chamfer, self).finish()
        
    def __eq__(self, obj):
        if not isinstance(obj, Chamfer):
            return False
        if obj is self:
            return True
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 == _os1 and _s2 == _os2) or
                 (_s1 == _os2 and _s2 == _os1)) and
                abs(self.__length - obj.getLength()) < 1e-10)

    def __ne__(self, obj):
        if not isinstance(obj, Chamfer):
            return True
        if obj is self:
            return False
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 != _os1 or _s2 == _os2) and
                 (_s1 != _os2 or _s2 == _os1)) or
                abs(self.__length - obj.getLength()) > 1e-10)

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Chamfer Default Style',
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

    def getValues(self):
        """Return values comprising the Chamfer.

getValues()

This method extends the SegJoint::getValues() method.
        """
        _data = super(Chamfer, self).getValues()
        _data.setValue('type', 'chamfer')
        _s1, _s2 = self.getSegments()
        _data.setValue('s1', _s1.getID())
        _data.setValue('s2', _s2.getID())
        _data.setValue('length', self.__length)
        return _data

    def getLength(self):
        """Return the Chamfer length.

getLength()
        """
        return self.__length

    def setLength(self, l):
        """Set the Chamfer length.

setLength(l)

The length should be a positive float value.
        """
        _s1, _s2 = self.getSegments()        
        if (self.isLocked() or
            _s1.isLocked() or
            _s2.isLocked()):
            raise RuntimeError, "Setting length not allowed - object locked."
        _l = util.get_float(l)
        if _l < 0.0:
            raise ValueError, "Invalid chamfer length: %g" % _l
        if _l > _s1.length():
            raise ValueError, "Chamfer is larger than first Segment."
        if _l > _s2.length():
            raise ValueError, "Chamfer is larger than second Segment."
        _ol = self.__length
        if abs(_l - _ol) > 1e-10:
            self.startChange('length_changed')
            self.__length = _l
            self.endChange('length_changed')
            self.sendMessage('length_changed', _ol)
            self._moveSegmentPoints(_l)
            self.modified()

    length = property(getLength, setLength, None, "Chamfer length.")

    def _moveSegmentPoints(self, dist):
        """Set the Chamfer endpoints at the correct location

moveSegmentPoints(dist)

The argument 'dist' is the chamfer length. This method is private
the the Chamfer object.
        """
        _d = util.get_float(dist)
        #
        # process segment 1
        #
        _xi, _yi = self.getIntersection()
        # print "xi: %g; yi: %g" % (xi, yi)
        _mp1, _mp2 = self.getMovingPoints()
        _sp1, _sp2 = self.getFixedPoints()
        _sx, _sy = _sp1.getCoords()
        _slen = hypot((_yi - _sy), (_xi - _sx))
        # print "slen: %g" % slen
        _newlen = (_slen - _d)/_slen
        # print "newlen: %g" % _newlen
        _xs, _ys = _sp1.getCoords()
        _xm, _ym = _mp1.getCoords()
        _xn = _xs + _newlen * (_xi - _xs)
        _yn = _ys + _newlen * (_yi - _ys)
        # print "xn: %g; yn: %g" % (_xn, _yn)
        _mp1.setCoords(_xn, _yn)
        #
        # process segment 2
        #
        _sx, _sy = _sp2.getCoords()
        _slen = hypot((_yi - _sy), (_xi - _sx))
        # print "slen: %g" % _slen
        _newlen = (_slen - _d)/_slen
        # print "newlen: %g" % _newlen
        _xs, _ys = _sp2.getCoords()
        _xm, _ym = _mp2.getCoords()
        _xn = _xs + _newlen * (_xi - _xs)
        _yn = _ys + _newlen * (_yi - _ys)
        # print "xn: %g; yn: %g" % (_xn, _yn)
        _mp2.setCoords(_xn, _yn)

    def clone(self):
        _s1, _s2 = self.getSegments()
        _l = self.__length
        _s = self.getStyle()
        _ch = Chamfer(_s1, _s2, _l, _s)
        _ch.setColor(self.getColor())
        _ch.setLinetype(self.getLinetype())
        _ch.setThickness(self.getThickness())
        return _ch

    def sendsMessage(self, m):
        if m in Chamfer.__messages:
            return True
        return super(Chamfer, self).sendsMessage(m)

#
# Chamfer history class
#

class ChamferLog(graphicobject.GraphicObjectLog):
    def __init__(self, c):
        if not isinstance(c, Chamfer):
            raise TypeError, "Invalid chamfer: " + `type(c)`
        super(ChamferLog, self).__init__(c)
        c.connect('length_changed', self._lengthChange)

    def _lengthChange(self, c, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _l = args[0]
        if not isinstance(_l, float):
            raise TypeError, "Unexpected type for length: " + `type(_l)`
        self.saveUndoData('length_changed', _l)

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _c = self.getObject()
        _op = args[0]
        if _op == 'length_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _l = args[1]
            if not isinstance(_l, float):
                raise TypeError, "Unexpected type for length: " + `type(_l)`
            _sdata = _c.getLength()
            self.ignore(_op)
            try:
                if undo:
                    _c.startUndo()
                    try:
                        _c.setLength(_l)
                    finally:
                        _c.endUndo()
                else:
                    _c.startRedo()
                    try:
                        _c.setLength(_l)
                    finally:
                        _c.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(ChamferLog, self).execute(undo, *args)

class Fillet(SegJoint):
    """
        A fillet is a curved joining of two segments. For a filleted
        joint to be valid, the radius must fall within some distance
        determined by the segment endpoints and segment intersection
        point, and the two segments must be extendable so they can
        share a common endpoint.
        A Fillet is derived from a SegJoint, so it shares the methods
        and attributes of that class. 
    """
    __defstyle = None
    __messages = {'radius_changed' : True,'moved' : True}
    
    def __init__(self, s1, s2, r, st=None, lt=None, col=None, t=None, **kw):
        super(Fillet, self).__init__(s1, s2, st, lt, col, t, **kw)
        _r = util.get_float(r)
        if _r < 0.0:
            raise ValueError, "Invalid fillet radius: %g" % _r
        self._calculateLimits()
        _rmin, _rmax = self.getRadialLimits()
        if _r < _rmin or _r > _rmax:
            raise ValueError, "Invalid radius: %g" % _r
        self.__radius = _r
        self.__center = (0.0, 0.0)
        self._calculateCenter()
        self.ignore('moved')
        try:
            self._moveSegmentPoints()
        finally:
            self.receive('moved')

    def finish(self):
        self.__radius = self.__center = None
        super(Fillet, self).finish()

    def __eq__(self, obj):
        if not isinstance(obj, Fillet):
            return False
        if obj is self:
            return True
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 == _os1 and _s2 == _os2) or
                 (_s1 == _os2 and _s2 == _os1)) and
                abs(self.__radius - obj.getRadius()) < 1e-10)

    def __ne__(self, obj):
        if not isinstance(obj, Fillet):
            return True
        if obj is self:
            return False
        _s1, _s2 = self.getSegments()
        _os1, _os2 = obj.getSegments()
        return (((_s1 != _os1 or _s2 != _os2) and
                 (_s1 != _os2 or _s2 != _os1)) or
                abs(self.__radius - obj.getRadius()) > 1e-10)

    def getDefaultStyle(cls):
        if cls.__defstyle is None:
            _s = style.Style(u'Fillet Default Style',
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

    def getValues(self):
        """Return values comprising the Fillet.

getValues()

This method extends the SegJoint::getValues() method.
        """
        _data = super(Fillet, self).getValues()
        _data.setValue('type', 'fillet')
        _s1, _s2 = self.getSegments()
        _data.setValue('s1', _s1.getID())
        _data.setValue('s2', _s2.getID())
        _data.setValue('radius', self.__radius)
        return _data

    def getRadius(self):
        """Return the Fillet radius.

getRadius()
        """
        return self.__radius

    def setRadius(self, r):
        """Set the Fillet radius.

setRadius(r)

The radius should be a positive float value.
        """
        _s1, _s2 = self.getSegments()        
        if (self.isLocked() or
            _s1.isLocked() or
            _s2.isLocked()):
            raise RuntimeError, "Setting length not allowed - object locked."
        _r = util.get_float(r)
        if _r < 0.0:
            raise ValueError, "Invalid fillet radius: %g" % _r
        self._calculateLimits()
        _rmin, _rmax = self.getRadialLimits()
        if _r < _rmin or _r > _rmax:
            raise ValueError, "Invalid radius: %g" % _r
        _or = self.__radius
        if abs(_r - _or) > 1e-10:
            self.startChange('radius_changed')
            self.__radius = _r
            self.endChange('radius_changed')
            self._calculateCenter()
            self._moveSegmentPoints()
            self.sendMessage('radius_changed', _or)
            self.modified()

    radius = property(getRadius, setRadius, None, "Chamfer radius.")

    def _calculateCenter(self):
        """Find the center point of the radius

_calculateCenter()

This method is private to the Fillet object.
        """
        _r = self.__radius
        _p1, _p3 = self.getMovingPoints()
        _p2, _p4 = self.getFixedPoints()
        _as1 = atan2((_p2.y - _p1.y), (_p2.x - _p1.x)) # _as1 in radians
        _as2 = atan2((_p4.y - _p3.y), (_p4.x - _p3.x)) # _as2 in radians
        if abs(abs(_as1) - pi) < 1e-10:
            if _as1 > 0.0 and _as2 < 0.0:
                _as1 = -pi
            if _as1 < 0.0 and _as2 > 0.0:
                _as1 = pi
        if abs(abs(_as2) - pi) < 1e-10:
            if _as2 > 0.0 and _as2 < 0.0:
                _as2 = -pi
            if _as2 < 0.0 and _as1 > 0.0:
                _as2 = pi
        _acl = (_as1 + _as2)/2.0
        _acc = abs(_as1 - _as2)/2.0
        if (_as1 > 0.0 and _as2 < 0.0) or (_as1 < 0.0 and _as2 > 0.0):
            _amin = min(_as1, _as2)
            _amax = max(_as1, _as2)
            #print "_amax: %g" % _amax
            #print "_amin: %g" % _amin
            if _amax - _amin > pi: # radians
                if _acl < 0.0:
                    _acl = _acl + pi
                else:
                    _acl = _acl - pi
                _acc = ((pi - _amax) + (_amin + pi))/2.0
        #print "_acl: %g" % (_acl * _dtr)
        #print "_acc: %g" % (_acc * _dtr)
        _rc = hypot((_r/tan(_acc)), _r)
        #print "_rc: %g" % _rc
        _xi, _yi = self.getIntersection()
        _xc = _xi + _rc * cos(_acl)
        _yc = _yi + _rc * sin(_acl)
        self.__center = (_xc, _yc)
        #print "center: %s" % str(self.__center)

    def getCenter(self):
        """Return the center location of the Fillet.

getCenter()

This method returns a tuple of two floats; the first is the
center 'x' coordinate, the second is the 'y' coordinate.
        """
        return self.__center

    def _calculateLimits(self):
        """Determine the radial limits of the fillet.

_calculateLimits()

This method is private to the Fillet.
        """
        _p1, _p3 = self.getMovingPoints()
        _p2, _p4 = self.getFixedPoints()
        _as1 = atan2((_p2.y - _p1.y), (_p2.x - _p1.x)) # radians
        _as2 = atan2((_p4.y - _p3.y), (_p4.x - _p3.x)) # radians
        if abs(abs(_as1) - pi) < 1e-10:
            if _as1 > 0.0 and _as2 < 0.0:
                _as1 = -pi
            if _as1 < 0.0 and _as2 > 0.0:
                _as1 = pi
        if abs(abs(_as2) - pi) < 1e-10:
            if _as2 > 0.0 and _as2 < 0.0:
                _as2 = -pi
            if _as2 < 0.0 and _as1 > 0.0:
                _as2 = pi
        #print "_as1: %g" % (_as1 * _dtr)
        #print "_as2: %g" % (_as2 * _dtr)
        _acl = (_as1 + _as2)/2.0
        _acc = abs(_as1 - _as2)/2.0
        if (_as1 > 0.0 and _as2 < 0.0) or (_as1 < 0.0 and _as2 > 0.0):
            _amin = min(_as1, _as2)
            _amax = max(_as1, _as2)
            #print "_amax: %g" % _amax
            #print "_amin: %g" % _amin
            if _amax - _amin > pi: # radians
                if _acl < 0.0:
                    _acl = _acl + pi
                else:
                    _acl = _acl - pi
                _acc = ((pi - _amax) + (_amin + pi))/2.0
        #print "_acl: %g" % (_acl * _dtr)
        #print "_acc: %g" % (_acc * _dtr)
        _xi, _yi = self.getIntersection()
        _pf1, _pf2 = self.getFixedPoints()
        _d1 = hypot((_xi - _pf1.x), (_yi - _pf1.y))
        _d2 = hypot((_xi - _pf2.x), (_yi - _pf2.y))
        _c4 = min(_d1, _d2)
        self.__rmax = _c4 * tan(_acc) + 1e-10
        #print "rmax: %g" % self.__rmax
        _pm1, _pm2 = self.getMovingPoints()
        _d1 = hypot((_xi - _pm1.x), (_yi - _pm1.y))
        _d2 = hypot((_xi - _pm2.x), (_yi - _pm2.y))
        _c4 = max(_d1, _d2)
        self.__rmin = _c4 * tan(_acc) - 1e-10
        #print "rmin: %g" % self.__rmin

    def getRadialLimits(self):
        """Return the radial limits of the fillet.

getRadialLimits()

This method returns a tuple of two floats; the first is
the minimal radius for the fillet between two segments,
and the second is the maximum radius.
        """
        return self.__rmin, self.__rmax

    def _moveSegmentPoints(self):
        """Position the segment endpoints used in the Fillet.

_moveSegmentPoints()

This method is private to the Fillet.
        """
        _p1, _p3 = self.getMovingPoints()
        _p2, _p4 = self.getFixedPoints()
        _xc, _yc = self.__center
        #
        # segment 1
        #
        _l = _p2 - _p1
        _x1, _y1 = _p1.getCoords()
        _x2, _y2 = _p2.getCoords()
        _r = ((_xc - _x1)*(_x2 - _x1) + (_yc - _y1)*(_y2 - _y1))/pow(_l, 2)
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        _p1.setCoords(_px, _py)
        #
        # segment 2
        #
        _l = _p4 - _p3
        _x1, _y1 = _p3.getCoords()
        _x2, _y2 = _p4.getCoords()
        _r = ((_xc - _x1)*(_x2 - _x1) + (_yc - _y1)*(_y2 - _y1))/pow(_l, 2)
        _px = _x1 + _r * (_x2 - _x1)
        _py = _y1 + _r * (_y2 - _y1)
        _p3.setCoords(_px, _py)

    def getAngles(self):
        """Return the angles that the fillet sweeps through.

getAngles()

This method returns a tuple of two floats, the first is the
start angle of the fillet, and the second is the end angle.
        """
        _ms1, _ms2 = self.getMovingPoints()
        _xc, _yc = self.__center
        _x, _y = _ms1.getCoords()
        _as1 = _dtr * atan2((_y - _yc), (_x - _xc))
        if _as1 < 0.0:
            _as1 = _as1 + 360.0
        _x, _y = _ms2.getCoords()
        _as2 = _dtr * atan2((_y - _yc), (_x - _xc))
        if _as2 < 0.0:
            _as2 = _as2 + 360.0
        return _as1, _as2

    def inRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """Return whether or not a fillet exists with a region.

isRegion(xmin, ymin, xmax, ymax)

The four arguments define the boundary of an area, and the
function returns True if the joint lies within that area.
Otherwise, the function returns False.
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
        _mp1, _mp2 = self.getMovingPoints()
        _mx1, _my1 = _mp1.getCoords()
        _mx2, _my2 = _mp2.getCoords()
        _r = self.__radius
        _xc, _yc = self.__center
        _a1, _a2 = self.getAngles()
        _xl = [_mx1, _mx2, _xc]
        _yl = [_my1, _my2, _yc]
        if fully:
            if ((min(_xl) > _xmin) and
                (min(_yl) > _ymin) and
                (max(_xl) < _xmax) and
                (max(_yl) < _ymax)):
                return True
            return False
        #
        # fixme - need to use the arc and endpoints and not
        # a line connecting the endpoints ...
        #
        return util.in_region(_mx1, _my1, _mx2, _my2,
                              _xmin, _ymin, _xmax, _ymax)

    def clone(self):
        _s1, _s2 = self.getSegments()
        _r = self.__radius
        _s = self.getStyle()
        _f = Fillet(_s1, _s2, _r, _s)
        _f.setColor(self.getColor())
        _f.setLinetype(self.getLinetype())
        _f.setThickness(self.getThickness())
        return _f

    def sendsMessage(self, m):
        if m in Fillet.__messages:
            return True
        return super(Fillet, self).sendsMessage(m)

#
# Fillet history class
#

class FilletLog(graphicobject.GraphicObjectLog):
    def __init__(self, f):
        if not isinstance(f, Fillet):
            raise TypeError, "Invalid fillet: " + `type(f)`
        super(FilletLog, self).__init__(f)
        f.connect('radius_changed', self._radiusChange)

    def _radiusChange(self, f, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _r = args[0]
        if not isinstance(_r, float):
            raise TypeError, "Unexpected type for radius: " + `type(_r)`
        self.saveUndoData('radius_changed', _r)

    def execute(self, undo, *args):
        util.test_boolean(undo)
        _alen = len(args)
        if _alen == 0:
            raise ValueError, "No arguments to execute()"
        _f = self.getObject()
        _op = args[0]
        if _op == 'radius_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _r = args[1]
            if not isinstance(_r, float):
                raise TypeError, "Unexpected type for radius: " + `type(_r)`
            _sdata = _f.getRadius()
            self.ignore(_op)
            try:
                if undo:
                    _f.startUndo()
                    try:
                        _f.setRadius(_r)
                    finally:
                        _f.endUndo()
                else:
                    _f.startRedo()
                    try:
                        _f.setRadius(_r)
                    finally:
                        _f.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        else:
            super(FilletLog, self).execute(undo, *args)
