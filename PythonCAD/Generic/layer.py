#
# Copyright (c) 2002, 2003, 2004, 2005, 2006 Art Haas
#
#               2009 Matteo Boscolo
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
# The Layer class
#

import sys
import types
from math import pi, atan2

from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import segjoint
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic import dimtrees
from PythonCAD.Generic import tolerance
from PythonCAD.Generic import entity
from PythonCAD.Generic import logger
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import units
from PythonCAD.Generic import util

class Layer(entity.Entity):
    """
        The Layer class.
        A Layer object holds all the various entities that can be
        in a drawing. Each layer can have sublayers, and there is
        no limit to the depth of the sublayering.
        A Layer object has several attributes:
        name: The Layer's name
        parent: The parent Layer of the Layer
        scale: The scale factor for object contained in the Layer
        A Layer object has the following methods:
        {get/set}Name(): Get/Set the Layer's name.
        {get/set}ParentLayer(): Get/Set the Layer's parent.
        {add/del}Sublayer(): Add/Remove a sublayer to this Layer.
        hasSublayers(): Test if this Layer has sublayers.
        getSublayers(): Return any sublayers of this Layer.
        {add/del}Object(): Store/Remove a Point, Segment, etc. in the Layer.
        {get/set}Autosplit(): Get/Set the autosplitting state of the Layer.
        findObject(): Return an object in the layer equivalent to a test object.
        find(): Search for an object within the Layer.
        getObject(): Return an object with a specified ID
        mapPoint(): See if a non-Point object in the layer crosses some location.
        hasEntities(): Test if the Layer contains any entities
        hasEntityType(): Test if the Layer contains a particular entity type.
        getLayerEntities(): Return all the instances of an entity within the Layer.
        getBoundary(): Find the maximum and minimum coordinates of the Layer.
        objsInRegion(): Return all the objects in the Layer that can be seen
        within some view.
        {get/set}DeletedEntityData(): Get/Set the deleted entity values in the Layer
    """

    __messages = {
        'name_changed' : True,
        'scale_changed' : True,
        'added_sublayer' : True,
        'deleted_sublayer' : True,
        }
    
    def __init__(self, name=None, **kw):
        """
            Initializee a Layer.
            Layer([name)
            Argument name is optional. The name should be a unicode string
            if specified, otherwise a default name of 'Layer' is given.
        """
        _n = name
        if _n is None:
            _n = u'Layer'
        if not isinstance(_n, types.StringTypes):
            raise TypeError, "Invalid layer name type: " + `type(name)`
        if isinstance(name, str):
            _n = unicode(name)
        super(Layer, self).__init__(**kw)
        self.__name = _n
        self.__points = point.PointQuadtree()
        self.__segments = segment.SegmentQuadtree()
        self.__circles = circle.CircleQuadtree()
        self.__arcs = arc.ArcQuadtree()
        self.__hclines = hcline.HCLineQuadtree()
        self.__vclines = vcline.VCLineQuadtree()
        self.__aclines = acline.ACLineQuadtree()
        self.__clines = cline.CLineQuadtree()
        self.__ccircles = ccircle.CCircleQuadtree()
        self.__chamfers = [] # should be Quadtree
        self.__fillets = [] # should be Quadtree
        self.__leaders = leader.LeaderQuadtree()
        self.__polylines = polyline.PolylineQuadtree()
        self.__textblocks = [] # should be Quadtree
        self.__ldims = dimtrees.LDimQuadtree()
        self.__hdims = dimtrees.HDimQuadtree()
        self.__vdims = dimtrees.VDimQuadtree()
        self.__rdims = dimtrees.RDimQuadtree()
        self.__adims = dimtrees.ADimQuadtree()
        self.__scale = 1.0
        self.__parent_layer = None
        self.__sublayers = None
        self.__asplit = True
        #
        # self.__objects keeps a reference to all objects stored in the layer
        #
        self.__objects = {}
        self.__objids = {}
        self.__logs = {}

    def __str__(self):
        _p = self.__parent_layer
        if _p is None:
            _s = "Layer: %s [No Parent Layer]" % self.__name
        else:
            _s = "Layer: %s; Parent Layer: %s" % (self.__name, _p.getName())
        return _s

    def __contains__(self, obj):
        """
            Find an object in the Layer.
            This method permits the use of 'in' for test conditions.
            if obj in layer:
            ....
            This function tests for Point, Segment, Circle, etc. It returns
            True if there is an equivalent object held in the Layer. Otherwise
            the function returns False.
        """
        _seen = False
        if id(obj) in self.__objects:
            _seen = True
        if not _seen:
            if isinstance(obj, point.Point):
                _x, _y = obj.getCoords()
                _seen = (len((self.__points.find(_x, _y))) > 0)
            elif isinstance(obj, segment.Segment):
                _p1, _p2 = obj.getEndpoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                _seen = (len(self.__segments.find(_x1, _y1, _x2, _y2)) > 0)
            elif isinstance(obj, arc.Arc):
                _x, _y = obj.getCenter().getCoords()
                _r = obj.getRadius()
                _sa = obj.getStartAngle()
                _ea = obj.getEndAngle()
                _seen = (len(self.__arcs.find(_x, _y, _r, _sa, _ea)) > 0)
            elif isinstance(obj, circle.Circle):
                _x, _y = obj.getCenter().getCoords()
                _r = obj.getRadius()
                _seen = (len(self.__circles.find(_x, _y, _r)) > 0)
            elif isinstance(obj, hcline.HCLine):
                _y = obj.getLocation().y
                _seen = (len(self.__hclines.find(_y)) > 0)
            elif isinstance(obj, vcline.VCLine):
                _x = obj.getLocation().x
                _seen = (len(self.__vclines.find(_x)) > 0)
            elif isinstance(obj, acline.ACLine):
                _x, _y = obj.getLocation().getCoords()
                _angle = obj.getAngle()
                _seen = (len(self.__aclines.find(_x, _y, _angle)) > 0)
            elif isinstance(obj, cline.CLine):
                _p1, _p2 = obj.getKeypoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                _seen = (len(self.__clines.find(_x1, _y1, _x2, _y2)) > 0)
            elif isinstance(obj, ccircle.CCircle):
                _x, _y = obj.getCenter().getCoords()
                _r = obj.getRadius()
                _seen = (len(self.__ccircles.find(_x, _y, _r)) > 0)
            elif isinstance(obj, segjoint.Fillet):
                _seen = obj in self.__fillets
            elif isinstance(obj, segjoint.Chamfer):
                _seen = obj in self.__chamfers
            elif isinstance(obj, leader.Leader):
                _p1, _p2, _p3 = obj.getPoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                _x3, _y3 = _p3.getCoords()
                _seen = (len(self.__leaders.find(_x1, _y1, _x2, _y2,
                                                 _x3, _y3)) > 0)
            elif isinstance(obj, polyline.Polyline):
                _coords = []
                for _pt in obj.getPoints():
                    _coords.extend(_pt.getCoords())
                _seen = (len(self.__polylines.find(_coords)) > 0)
            elif isinstance(obj, text.TextBlock):
                _seen = obj in self.__textblocks
            elif isinstance(obj, dimension.HorizontalDimension):
                _p1, _p2 = obj.getDimPoints()
                _seen = (len(self.__hdims.find(_p1, _p2)) > 0)
            elif isinstance(obj, dimension.VerticalDimension):
                _p1, _p2 = obj.getDimPoints()
                _seen = (len(self.__vdims.find(_p1, _p2)) > 0)
            elif isinstance(obj, dimension.LinearDimension):
                _p1, _p2 = obj.getDimPoints()
                _seen = (len(self.__ldims.find(_p1, _p2)) > 0)
            elif isinstance(obj, dimension.RadialDimension):
                _c1 = obj.getDimCircle()
                _seen = (len(self.__rdims.find(_c1)) > 0)
            elif isinstance(obj, dimension.AngularDimension):
                _vp, _p1, _p2 = obj.getDimPoints()
                _dims = self.__adims.find(_vp, _p1, _p2)
                _seen = len(_dims) > 0
            else:
                raise TypeError, "Invalid type for in operation: " + `type(obj)`
        return _seen

    def finish(self):
        self.__name = None
        self.__points = None
        self.__segments = None
        self.__circles = None
        self.__arcs = None
        self.__hclines = None
        self.__vclines = None
        self.__aclines = None
        self.__clines = None
        self.__ccircles = None
        self.__chamfers = None
        self.__fillets = None
        self.__leaders = None
        self.__polylines = None
        self.__textblocks = None
        self.__ldims = None
        self.__hdims = None
        self.__vdims = None
        self.__rdims = None
        self.__adims = None
        super(Layer, self).finish()
        
    def clear(self):
        """
            Remove all the entities stored in this layer
        """
        if self.isLocked():
            raise RuntimeError, "Clearing layer not allowed - layer locked."
        for _obj in self.__adims.getObjects():
            self.delObject(_obj)
        for _obj in self.__rdims.getObjects():
            self.delObject(_obj)
        for _obj in self.__vdims.getObjects():
            self.delObject(_obj)
        for _obj in self.__hdims.getObjects():
            self.delObject(_obj)
        for _obj in self.__ldims.getObjects():
            self.delObject(_obj)
        for _obj in self.__textblocks:
            self.delObject(_obj)
        for _obj in self.__polylines.getObjects():
            self.delObject(_obj)
        for _obj in self.__leaders.getObjects():
            self.delObject(_obj)
        for _obj in self.__chamfers:
            self.delObject(_obj)
        for _obj in self.__fillets:
            self.delObject(_obj)
        for _obj in self.__ccircles.getObjects():
            self.delObject(_obj)
        for _obj in self.__clines.getObjects():
            self.delObject(_obj)
        for _obj in self.__aclines.getObjects():
            self.delObject(_obj)
        for _obj in self.__vclines.getObjects():
            self.delObject(_obj)
        for _obj in self.__hclines.getObjects():
            self.delObject(_obj)
        for _obj in self.__arcs.getObjects():
            self.delObject(_obj)
        for _obj in self.__circles.getObjects():
            self.delObject(_obj)
        for _obj in self.__segments.getObjects():
            self.delObject(_obj)
        for _obj in self.__points.getObjects():
            self.delObject(_obj)
        self.setScale(1.0)

    def getName(self):
        """
            Return the name of the Layer.
        """
        return self.__name

    def setName(self, name):
        """
            Set the name of the Layer.
            The name must be a string, and cannot be None.
        """
        _n = name
        if _n is None:
            raise ValueError, "Layers must have a name."
        if not isinstance(_n, types.StringTypes):
            raise TypeError, "Invalid name type: " + `type(_n)`
        if isinstance(_n, str):
            _n = unicode(_n)
        _on = self.__name
        if _on != _n:
            self.startChange('name_changed')
            self.__name = _n
            self.endChange('name_changed')
            self.sendMessage('name_changed', _on)
            self.modified()

    name = property(getName, setName, None, "Layer name.")

    def getValues(self):
        """
            Return values comprising the Layer.
            This method extends the Entity::getValues() method.
        """
        _data = super(Layer, self).getValues()
        _data.setValue('type', 'layer')        
        _pid = None
        if self.__parent_layer is not None:
            _pid = self.__parent_layer.getID()
        _data.setValue('parent_layer', _pid)
        _data.setValue('name', self.__name)
        _data.setValue('scale', self.__scale)
        return _data

    def setDeletedEntityData(self, data):
        """
            Fill in the deleted entity data.
            Argument 'data' must be a dictionary with the keys being
            entity id values (integers) and the dictionary values as Logger
            instances.
        """
        if not isinstance(data, dict):
            raise TypeError, "Invalid dictionary type: " + `type(data)`
        if len(self.__logs) != 0:
            raise ValueError, "Deleted data already stored"
        for _key in data:
            if not isinstance(_key, int):
                raise TypeError, "Invalid entity id type: " + `type(_key)`
            _val = data[_key]
            if not isinstance(_val, logger.Logger):
                raise TypeError, "Invalid entity log type: " + `type(_val)`
            self.__logs[_key] = _val
        
    def getDeletedEntityData(self):
        """
            Return the stored log data for deleted entities.
            This method returns a dictionary.
        """
        return self.__logs.copy()

    def __splitObject(self, obj, pt):
        """
            Split a Segment/Circle/Arc/Polyline on a Point in the Layer.
            Argument 'obj' must be a Segment, Circle, Arc, or Polyline, and argument
            'pt' must be Point. Both arguments must be in stored in the Layer, and
            the point must lie on the entity to be split.
            This method is private to the Layer.
        """
        if self.isLocked():
            raise RuntimeError, "Splitting entity not allowed - layer locked."
        if not isinstance(obj, (segment.Segment, circle.Circle,
                                arc.Arc, polyline.Polyline)):
            raise TypeError, "Invalid object: " + `type(obj)`
        if obj.getParent() is not self:
            raise ValueError, "Object not in layer: " + `obj`
        if not isinstance(pt, point.Point):
            raise TypeError, "Invalid point: " + `type(pt)`
        if pt.getParent() is not self:
            raise ValueError, "Point not in layer: " + `pt`
        _x, _y = pt.getCoords()
        _mp = obj.mapCoords(_x, _y)
        if _mp is None:
            raise RuntimeError, "Point not on object: " + `pt`
        _split = False
        _objs = []
        if isinstance(obj, segment.Segment):
            _p1, _p2 = obj.getEndpoints()
            if _p1 != pt and _p2 != pt:
                _split = True
                _s = obj.getStyle()
                _l = obj.getLinetype()
                _c = obj.getColor()
                _t = obj.getThickness()
                _seg = segment.Segment(_p1, pt, _s, _l, _c, _t)
                self.addObject(_seg)
                _objs.append(_seg)
                _seg = segment.Segment(pt, _p2, _s, _l, _c, _t)
                self.addObject(_seg)
                _objs.append(_seg)
        elif isinstance(obj, (circle.Circle, arc.Arc)):
            _cp = obj.getCenter()
            _r = obj.getRadius()
            _s = obj.getStyle()
            _l = obj.getLinetype()
            _c = obj.getColor()
            _t = obj.getThickness()
            _angle = (180.0/pi) * atan2((_y - _cp.y),(_x - _cp.x))
            if _angle < 0.0:
                _angle = _angle + 360.0
            if isinstance(obj, circle.Circle):
                _split = True
                _arc = arc.Arc(_cp, _r, _angle, _angle, _s, _l, _c, _t)
                self.addObject(_arc)
                _objs.append(_arc)
            else:
                _ep1, _ep2 = obj.getEndpoints()
                if pt != _ep1 and pt != _ep2:
                    _split = True
                    _sa = obj.getStartAngle()
                    _ea = obj.getEndAngle()
                    _arc = arc.Arc(_cp, _r, _sa, _angle, _s, _l, _c, _t)
                    self.addObject(_arc)
                    _objs.append(_arc)
                    _arc = arc.Arc(_cp, _r, _angle, _ea, _s, _l, _c, _t)
                    self.addObject(_arc)
                    _objs.append(_arc)
        elif isinstance(obj, polyline.Polyline):
            _pts = obj.getPoints()
            for _i in range(len(_pts) - 1):
                _p1x, _p1y = _pts[_i].getCoords()
                _p2x, _p2y = _pts[_i + 1].getCoords()
                _p = util.map_coords(_x, _y, _p1x, _p1y, _p2x, _p2y)
                if _p is None:
                    continue
                _px, _py = _p
                if ((abs(_px - _p1x) < 1e-10 and abs(_py - _p1y) < 1e-10) or
                    (abs(_px - _p2x) < 1e-10 and abs(_py - _p2y) < 1e-10)):
                    continue
                _split = True
                obj.addPoint((_i + 1), pt)
                break
        else:
            raise TypeError, "Unexpected type: " + `type(obj)`
        return (_split, _objs)

    def setAutosplit(self, autoSplit):
        """
            Set the autosplit state of the Layer.
            Argument 'autoSplit' must be a Boolean.
        """
        util.test_boolean(autoSplit)
        self.__asplit = autoSplit

    def getAutosplit(self):
        """
            Retrieve the autosplit state of the Layer.
            This method returns a Boolean.
        """
        return self.__asplit

    def addObject(self, obj):
        """
            Add an object to this Layer.
            The object should be a Point, Segment, Arc, Circle,
            HCLine, VCLine, ACLine, CLine, CCircle, TextBlock, Chamfer,
            Fillet, Leader, Polyline, or Dimension. Anything else raises
            a TypeError exception.
        """
        if self.isLocked():
            raise RuntimeError, "Adding entity not allowed - layer locked."
        if id(obj) in self.__objects:
            return
        if isinstance(obj, point.Point):
            _res = self.__addPoint(obj)
        elif isinstance(obj, segment.Segment):
            _res = self.__addSegment(obj)
        elif isinstance(obj, arc.Arc):
            _res = self.__addArc(obj)
        elif isinstance(obj, circle.Circle):
            _res = self.__addCircle(obj)
        elif isinstance(obj, hcline.HCLine):
            _res = self.__addHCLine(obj)
        elif isinstance(obj, vcline.VCLine):
            _res = self.__addVCLine(obj)
        elif isinstance(obj, acline.ACLine):
            _res = self.__addACLine(obj)
        elif isinstance(obj, ccircle.CCircle):
            _res = self.__addCCircle(obj)
        elif isinstance(obj, cline.CLine):
            _res = self.__addCLine(obj)
        elif isinstance(obj, segjoint.Chamfer):
            _res = self.__addChamfer(obj)
        elif isinstance(obj, segjoint.Fillet):
            _res = self.__addFillet(obj)
        elif isinstance(obj, leader.Leader):
            _res = self.__addLeader(obj)
        elif isinstance(obj, polyline.Polyline):
            _res = self.__addPolyline(obj)
        elif isinstance(obj, text.TextBlock):
            _res = self.__addTextBlock(obj)
        elif isinstance(obj, dimension.AngularDimension):
            _res = self.__addAngularDimension(obj)
        elif isinstance(obj, dimension.RadialDimension):
            _res = self.__addRadialDimension(obj)
        elif isinstance(obj, dimension.HorizontalDimension):
            _res = self.__addHorizontalDimension(obj)
        elif isinstance(obj, dimension.VerticalDimension):
            _res = self.__addVerticalDimension(obj)
        elif isinstance(obj, dimension.LinearDimension):
            _res = self.__addLinearDimension(obj)
        else:
            raise TypeError, "Invalid object type for storage: " + `type(obj)`
        if _res:
            #
            # call setParent() before connecting to layer log (if
            # it exists) so that the log will not recieve a 'modified'
            # message ...
            #
            self.__objects[id(obj)] = obj
            _oid = obj.getID()
            self.__objids[_oid] = obj
            obj.setParent(self)
            _log = obj.getLog()
            if _log is not None: # make this an error?
                _oldlog = self.__logs.get(_oid)
                if _oldlog is not None: # re-attach old log
                    _log.transferData(_oldlog)
                    del self.__logs[_oid]
            if isinstance(obj, dimension.Dimension):
                _ds1, _ds2 = obj.getDimstrings()
                _oid = _ds1.getID()
                _log = _ds1.getLog()
                if _log is not None:
                    _oldlog = self.__logs.get(_oid)
                    if _oldlog is not None:
                        _log.transferData(_oldlog)
                        del self.__logs[_oid]
                _oid = _ds2.getID()
                _log = _ds2.getLog()
                if _log is not None:
                    _oldlog = self.__logs.get(_oid)
                    if _oldlog is not None:
                        _log.transferData(_oldlog)
                        del self.__logs[_oid]
            #
            # Automatically split a segment, circle, arc, or
            # polyline if a point was added and the autosplit
            # flag is True
            #
            if (isinstance(obj, point.Point) and
                self.__asplit is True and
                not self.inUndo() and not self.inRedo()):
                _x, _y = obj.getCoords()
                _types = {'segment' : True,
                          'circle' : True,
                          'arc' : True,
                          'polyline' : True}
                _hits = self.mapCoords(_x, _y, types=_types)
                if len(_hits) > 0:
                    for _mobj, _mpt in _hits:
                        _split, _sobjs = self.__splitObject(_mobj, obj)
                        if _split and len(_sobjs):
                            self.delObject(_mobj)
        #
        # Reset the autosplit flag to True
        #
        self.__asplit = True

    def __addPoint(self, p):
        """
            Add a Point object to the Layer.
            This method is private to the Layer object.
        """
        self.__points.addObject(p)
        if p.getLog() is None:
            _log = point.PointLog(p)
            p.setLog(_log)
        return True

    def __addSegment(self, s):
        """
            Add a Segment object to the Layer.
            This method is private to the Layer object.
        """
        _p1, _p2 = s.getEndpoints()
        if id(_p1) not in self.__objects:
            raise ValueError, "Segment p1 Point not found in Layer."
        if id(_p2) not in self.__objects:
            raise ValueError, "Segment p2 Point not found in Layer."
        self.__segments.addObject(s)
        if s.getLog() is None:
            _log = segment.SegmentLog(s)
            s.setLog(_log)
        return True

    def __addCircle(self, c):
        """
            Add a Circle object to the Layer.
            This method is private to the layer object.
        """
        _cp = c.getCenter()
        if id(_cp) not in self.__objects:
            raise ValueError, "Circle center Point not found in Layer."
        self.__circles.addObject(c)
        if c.getLog() is None:
            _log = circle.CircleLog(c)
            c.setLog(_log)
        return True

    def __addArc(self, a):
        """
            Add an Arc object to the Layer.
            This method is private to the Layer object.
        """
        _cp = a.getCenter()
        if id(_cp) not in self.__objects:
            raise ValueError, "Arc center Point not found in Layer."
        self.__arcs.addObject(a)
        if a.getLog() is None:
            _log = arc.ArcLog(a)
            a.setLog(_log)
        for _ex, _ey in a.getEndpoints():
            _pts = self.__points.find(_ex, _ey)
            if len(_pts) == 0:
                _lp = point.Point(_ex, _ey)
                self.addObject(_lp)
            else:
                _lp = _pts.pop()
                _max = _lp.countUsers()
                for _pt in _pts:
                    _count = _pt.countUsers()
                    if _count > _max:
                        _max = _count
                        _lp = _pt
            _lp.storeUser(a)
            if abs(a.getStartAngle() - a.getEndAngle()) < 1e-10:
                break
        return True

    def __addHCLine(self, hcl):
        """
            Add an HCLine object to the Layer.
            This method is private to the Layer object.
        """
        _lp = hcl.getLocation()
        if id(_lp) not in self.__objects:
            raise ValueError, "HCLine location Point not found in Layer."
        self.__hclines.addObject(hcl)
        if hcl.getLog() is None:
            _log = hcline.HCLineLog(hcl)
            hcl.setLog(_log)
        return True

    def __addVCLine(self, vcl):
        """
            Add an VCLine object to the Layer.
            This method is private to the Layer object.
        """
        _lp = vcl.getLocation()
        if id(_lp) not in self.__objects:
            raise ValueError, "VCLine location Point not found in Layer."
        self.__vclines.addObject(vcl)
        if vcl.getLog() is None:
            _log = vcline.VCLineLog(vcl)
            vcl.setLog(_log)
        return True

    def __addACLine(self, acl):
        """
            Add an ACLine object to the Layer.
            This method is private to the Layer object.
        """
        _lp = acl.getLocation()
        if id(_lp) not in self.__objects:
            raise ValueError, "ACLine location Point not found in Layer."
        self.__aclines.addObject(acl)
        if acl.getLog() is None:
            _log = acline.ACLineLog(acl)
            acl.setLog(_log)
        return True

    def __addCCircle(self, cc):
        """
            Add an CCircle object to the Layer.
            This method is private to the Layer object.
        """
        _cp = cc.getCenter()
        if id(_cp) not in self.__objects:
            raise ValueError, "CCircle center Point not found in Layer."
        self.__ccircles.addObject(cc)
        if cc.getLog() is None:
            _log = ccircle.CCircleLog(cc)
            cc.setLog(_log)
        return True

    def __addCLine(self, cl):
        """Add an CLine object to the Layer.

_addCLine(cl)

This method is private to the Layer object.
        """
        _p1, _p2 = cl.getKeypoints()
        if id(_p1) not in self.__objects:
            raise ValueError, "CLine p1 Point not found in Layer."
        if id(_p2) not in self.__objects:
            raise ValueError, "CLine p2 Point not found in Layer."
        self.__clines.addObject(cl)
        if cl.getLog() is None:
            _log = cline.CLineLog(cl)
            cl.setLog(_log)
        return True

    def __addChamfer(self, ch):
        """Add a Chamfer object to the Layer.

_addChamfer(ch)

This method is private to the Layer object.
        """
        _s1, _s2 = ch.getSegments()
        if id(_s1) not in self.__objects:
            raise ValueError, "Chamfer s1 Segment not found in Layer."
        if id(_s2) not in self.__objects:
            raise ValueError, "Chamfer s2 Segment not found in Layer."
        self.__chamfers.append(ch)
        if ch.getLog() is None:
            _log = segjoint.ChamferLog(ch)
            ch.setLog(_log)
        return True

    def __addFillet(self, f):
        """Add a Fillet object to the Layer.

_addFillet(f)

This method is private to the Layer object.
        """
        _s1, _s2 = f.getSegments()
        if id(_s1) not in self.__objects:
            raise ValueError, "Fillet s1 Segment not found in Layer."
        if id(_s2) not in self.__objects:
            raise ValueError, "Fillet s2 Segment not found in Layer."
        self.__fillets.append(f)
        if f.getLog() is None:
            _log = segjoint.FilletLog(f)
            f.setLog(_log)
        return True

    def __addLeader(self, l):
        """Add a Leader object to the Layer.

_addLeader(l)

This method is private to the Layer object.
        """
        _p1, _p2, _p3 = l.getPoints()
        if id(_p1) not in self.__objects:
            raise ValueError, "Leader p1 Point not found in Layer."
        if id(_p2) not in self.__objects:
            raise ValueError, "Leader p2 Point not found in Layer."
        if id(_p3) not in self.__objects:
            raise ValueError, "Leader p3 Point not found in Layer."
        self.__leaders.addObject(l)
        if l.getLog() is None:
            _log = leader.LeaderLog(l)
            l.setLog(_log)
        return True

    def __addPolyline(self, pl):
        """Add a Polyline object to the Layer.

_addPolyline(pl)

This method is private to the Layer object.
        """
        for _pt in pl.getPoints():
            if id(_pt) not in self.__objects:
                raise ValueError, "Polyline point not in layer: " + str(_pt)
        self.__polylines.addObject(pl)
        if pl.getLog() is None:
            _log = polyline.PolylineLog(pl)
            pl.setLog(_log)
        return True

    def __addTextBlock(self, tb):
        """Add a TextBlock object to the Layer.

_addTextBlock(tb)

The TextBlock object 'tb' is added to the layer if there is not
already a TextBlock in the layer at the same location and with the
same text.
        """
        self.__textblocks.append(tb)
        if tb.getLog() is None:
            _log = text.TextBlockLog(tb)
            tb.setLog(_log)
        return True

    def __addAngularDimension(self, adim):
        """Add an AngularDimension object to the Layer.

_addAngularDimension(adim)

This method is private to the Layer object.
        """
        _p1, _p2, _p3 = adim.getDimPoints()
        if _p1.getParent() is None:
            raise ValueError, "Dimension Point P1 not found in a Layer"
        if _p2.getParent() is None:
            raise ValueError, "Dimension Point P2 not found in a Layer!"
        if _p3.getParent() is None:
            raise ValueError, "Dimension Point P3 not found in a Layer!"
        self.__adims.addObject(adim)
        if adim.getLog() is None:
            _log = dimension.DimLog(adim)
            adim.setLog(_log)
            _ds1, _ds2 = adim.getDimstrings()
            _log = dimension.DimStringLog(_ds1)
            _ds1.setLog(_log)
            _log = dimension.DimStringLog(_ds2)
            _ds2.setLog(_log)
        return True

    def __addRadialDimension(self, rdim):
        """Add a RadialDimension object to the Layer.

_addRadialDimension(rdim)

This method is private to the Layer object.
        """
        _dc = rdim.getDimCircle()
        if _dc.getParent() is None:
            raise ValueError, "RadialDimension circular object not found in a Layer"
        self.__rdims.addObject(rdim)
        if rdim.getLog() is None:        
            _log = dimension.DimLog(rdim)
            rdim.setLog(_log)
            _ds1, _ds2 = rdim.getDimstrings()
            _log = dimension.DimStringLog(_ds1)
            _ds1.setLog(_log)
            _log = dimension.DimStringLog(_ds2)
            _ds2.setLog(_log)
        return True

    def __addHorizontalDimension(self, hdim):
        """Add a HorizontalDimension object to the Layer.

_addHorizontalDimension(hdim)

This method is private to the Layer object.
        """
        _p1, _p2 = hdim.getDimPoints()
        if _p1.getParent() is None:
            raise ValueError, "HorizontalDimension Point P1 not found in layer"
        if _p1.getParent() is None:
            raise ValueError, "HorizontalDimension Point P2 not found in layer"
        self.__hdims.addObject(hdim)
        if hdim.getLog() is None:
            _log = dimension.DimLog(hdim)
            hdim.setLog(_log)
            _ds1, _ds2 = hdim.getDimstrings()
            _log = dimension.DimStringLog(_ds1)
            _ds1.setLog(_log)
            _log = dimension.DimStringLog(_ds2)
            _ds2.setLog(_log)
        return True

    def __addVerticalDimension(self, vdim):
        """Add a VerticalDimension object to the Layer.

_addVerticalDimension(vdim)

This method is private to the Layer object.
        """
        _p1, _p2 = vdim.getDimPoints()
        if _p1.getParent() is None:
            raise ValueError, "VerticalDimension Point P1 not found in layer"
        if _p2.getParent() is None:
            raise ValueError, "VerticalDimension Point P2 not found in layer"
        self.__vdims.addObject(vdim)
        if vdim.getLog() is None:
            _log = dimension.DimLog(vdim)
            vdim.setLog(_log)
            _ds1, _ds2 = vdim.getDimstrings()
            _log = dimension.DimStringLog(_ds1)
            _ds1.setLog(_log)
            _log = dimension.DimStringLog(_ds2)
            _ds2.setLog(_log)
        return True

    def __addLinearDimension(self, ldim):
        """Add a LinearDimension object to the Layer.

_addLinearDimension(ldim)

This method is private to the Layer object.
        """
        _p1, _p2 = ldim.getDimPoints()
        if _p1.getParent() is None:
            raise ValueError, "LinearDimension Point P1 not found in layer"
        if _p2.getParent() is None:
            raise ValueError, "LinearDimension Point P2 not found in layer"
        self.__ldims.addObject(ldim)
        if ldim.getLog() is None:
            _log = dimension.DimLog(ldim)
            ldim.setLog(_log)
            _ds1, _ds2 = ldim.getDimstrings()
            _log = dimension.DimStringLog(_ds1)
            _ds1.setLog(_log)
            _log = dimension.DimStringLog(_ds2)
            _ds2.setLog(_log)
        return True

    def delObject(self, obj):
        """Remove an object from this Layer.

delObject(obj)

The object should be a Point, Segment, Arc, Circle,
HCLine, VCLine, ACLine, CLine, CCircle, Chamfer,
Fillet, Leader, or Dimension. Anything else raises
a TypeError exception.
        """
        if self.isLocked():
            raise RuntimeError, "Deleting entity not allowed - layer locked."
        if id(obj) not in self.__objects:
            raise ValueError, "Object not found in layer: " + `obj`
        if isinstance(obj, point.Point):
            self.__delPoint(obj)
        elif isinstance(obj, segment.Segment):
            self.__delSegment(obj)
        elif isinstance(obj, arc.Arc):
            self.__delArc(obj)
        elif isinstance(obj, circle.Circle):
            self.__delCircle(obj)
        elif isinstance(obj, hcline.HCLine):
            self.__delHCLine(obj)
        elif isinstance(obj, vcline.VCLine):
            self.__delVCLine(obj)
        elif isinstance(obj, acline.ACLine):
            self.__delACLine(obj)
        elif isinstance(obj, cline.CLine):
            self.__delCLine(obj)
        elif isinstance(obj, ccircle.CCircle):
            self.__delCCircle(obj)
        elif isinstance(obj, segjoint.Chamfer):
            self.__delChamfer(obj)
        elif isinstance(obj, segjoint.Fillet):
            self.__delFillet(obj)
        elif isinstance(obj, leader.Leader):
            self.__delLeader(obj)
        elif isinstance(obj, polyline.Polyline):
            self.__delPolyline(obj)
        elif isinstance(obj, text.TextBlock):
            self.__delTextBlock(obj)
        elif isinstance(obj, dimension.AngularDimension):
            self.__delAngularDimension(obj)
        elif isinstance(obj, dimension.RadialDimension):
            self.__delRadialDimension(obj)
        elif isinstance(obj, dimension.HorizontalDimension):
            self.__delHorizontalDimension(obj)
        elif isinstance(obj, dimension.VerticalDimension):
            self.__delVerticalDimension(obj)
        elif isinstance(obj, dimension.LinearDimension):
            self.__delLinearDimension(obj)
        else:
            raise TypeError, "Invalid object type for removal: " + `type(obj)`

    def __freeObj(self, obj):
        #
        # disconnect object before calling setParent() so that
        # the layer log will not recieve a 'modified' message
        # from the object ...
        #
        del self.__objects[id(obj)]
        _oid = obj.getID()
        del self.__objids[_oid]
        if isinstance(obj, dimension.Dimension):
            _ds1, _ds2 = obj.getDimstrings()
            _log = _ds1.getLog()
            if _log is not None:
                _oid = _ds1.getID()
                self.__logs[_oid] = _log
            _log = _ds2.getLog()
            if _log is not None:
                _oid = _ds2.getID()
                self.__logs[_oid] = _log
        _log = obj.getLog()
        if _log is not None: # store the object's log
            _log.detatch()
            self.__logs[_oid] = _log
            obj.setLog(None)
        _log = self.getLog()        
        if _log is not None:
            obj.disconnect(_log)
        obj.setParent(None)
        
    def __delPoint(self, p):
        """Delete a Point from the Layer.

_delPoint(p)

This method is private to the Layer object.
        """
        _delete = True
        _users = p.getUsers()
        for _user in _users:
            if not isinstance(_user, dimension.Dimension):
                _delete = False
                break
        if _delete:
            for _user in _users:
                _layer = _user.getParent()
                if _layer is self:
                    if not self.inUndo() and not self.inRedo():
                        self.delObject(_user)
                    else:
                        p.disconnect(_user)
                        p.freeUser(_user)
                elif _layer is not None:
                    if not isinstance(_user, dimension.Dimension):
                        raise RuntimeError, "Point " + `p` + " bound to non-layer object: " + `_user`
                    if not self.inUndo() and not self.inRedo():
                        _layer.delObject(_user)
                    else:
                        p.disconnect(_user)
                        p.freeUser(_user)
                else:
                    pass
            self.__points.delObject(p)
            self.__freeObj(p)
            p.finish()

    def __delSegment(self, s):
        """Delete a Segment from the Layer.

_delSegment(s)

This method is private to the Layer object.
        """
        for _user in s.getUsers(): # chamfers, fillets, or hatching
            _layer = _user.getParent()
            if _layer is self:
                if not self.inUndo() and not self.inRedo():
                    self.delObject(_user) # restore segments on ch/fl?
                else:
                    s.freeUser(_user)
                    s.disconnect(_user)
            elif _layer is not None:
                raise RuntimeError, "Segment " + `s` + " bound to non-layer object: " + `_user`
            else:
                pass
        _p1, _p2 = s.getEndpoints()
        assert id(_p1) in self.__objects, "Segment p1 Point not in objects"
        assert id(_p2) in self.__objects, "Segment p2 Point not in objects"
        self.__segments.delObject(s)
        self.__freeObj(s)
        s.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_p1) # remove possibly unused point _p1
            self.delObject(_p2) # remove possibly unused point _p2

    def __delCircle(self, c):
        """Delete a Circle from the Layer.

_delCircle(c)

This method is private to the Layer object.
        """
        assert not isinstance(c, arc.Arc), "Arc in _delCircle()"
        for _user in c.getUsers(): # dimensions or hatching
            _layer = _user.getParent()
            if _layer is self:
                if not self.inUndo() and not self.inRedo():
                    self.delObject(_user)
                else:
                    c.freeUser(_user)
                    c.disconnect(_user)
            elif _layer is not None:
                if not isinstance(_user, dimension.Dimension):
                    raise RuntimeError, "Circle " + `c` + " bound to non-layer object: " + `_user`
                if not self.inUndo() and not self.inRedo():
                    _layer.delObject(_user)
                else:
                    c.freeUser(_user)
                    c.disconnect(_user)
            else:
                pass
        _cp = c.getCenter()
        assert id(_cp) in self.__objects, "Circle center point not in objects"
        self.__circles.delObject(c)
        self.__freeObj(c)
        c.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_cp) # remove possibly unused point _cp

    def __delArc(self, a):
        """Delete an Arc from the Layer.

_delArc(a)

This method is private to the Layer object.
        """
        for _user in a.getUsers(): # dimensions or hatching
            _layer = _user.getParent()
            if _layer is self:
                if not self.inUndo() and not self.inRedo():
                    self.delObject(_user)
                else:
                    a.freeUser(_user)
                    a.disconnect(_user)
            elif _layer is not None:
                if not isinstance(_user, dimension.Dimension):
                    raise RuntimeError, "Arc " + `a` + " bound to non-layer object: " + `_user`
                if not self.inUndo() and not self.inRedo():
                    _layer.delObject(_user)
                else:
                    a.freeUser(_user)
                    a.disconnect(_user)
            else:
                pass
        _cp = a.getCenter()
        assert id(_cp) in self.__objects, "Arc center point not in objects"
        self.__arcs.delObject(a)
        self.__freeObj(a)
        for _ep in a.getEndpoints():
            _pts = self.find('point', _ep[0], _ep[1])
            _p = None
            for _pt in _pts:
                for _user in _pt.getUsers():
                    if _user is a:
                        _p = _pt
                        break
                if _p is not None:
                    break
            assert _p is not None, "Arc endpoint not found in layer"
            assert id(_p) in self.__objects, "Arc endpoint not in objects"
            _p.disconnect(a)
            _p.freeUser(a)
            if not self.inUndo() and not self.inRedo():
                self.delObject(_p) # remove possibly unused point _p
            if abs(a.getStartAngle() - a.getEndAngle()) < 1e-10:
                break
        a.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_cp) # remove possibly unused point _cp

    def __delHCLine(self, hcl):
        """Remove a HCLine object from the Layer.

_delHCLine(hcl)

This method is private to the Layer object.
        """
        _lp = hcl.getLocation()
        assert id(_lp) in self.__objects, "HCLine point not in objects"
        self.__hclines.delObject(hcl)
        self.__freeObj(hcl)
        hcl.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_lp) # remove possibly unused point _lp

    def __delVCLine(self, vcl):
        """Remove a VCLine object from the Layer.

_delVCLine(vcl)

This method is private to the Layer object.
        """
        _lp = vcl.getLocation()
        assert id(_lp) in self.__objects, "VCLine point not in objects"
        self.__vclines.delObject(vcl)
        self.__freeObj(vcl)
        vcl.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_lp) # remove possibly unused point _lp

    def __delACLine(self, acl):
        """Remove an ACLine object from the Layer.

_delACLine(acl)

This method is private to the Layer object.
        """
        _lp = acl.getLocation()
        assert id(_lp) in self.__objects, "ACLine point not in objects"
        self.__aclines.delObject(acl)
        self.__freeObj(acl)
        acl.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_lp) # remove possibly unused point _lp

    def __delCLine(self, cl):
        """Delete a CLine from the Layer.

_delCLine(cl)

This method is private to the Layer object.
        """
        _p1, _p2 = cl.getKeypoints()
        assert id(_p1) in self.__objects, "CLine point p1 not in objects"
        assert id(_p2) in self.__objects, "CLine point p2 not in objects"
        self.__clines.delObject(cl)
        self.__freeObj(cl)
        cl.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_p1) # remove possibly unused point _p1
            self.delObject(_p2) # remove possibly unused point _p2

    def __delCCircle(self, cc):
        """Delete a CCircle from the Layer.

_delCCircle(cc)

This method is private to the Layer object.
        """
        _cp = cc.getCenter()
        assert id(_cp) in self.__objects, "CCircle center point not in objects"
        self.__ccircles.delObject(cc)
        self.__freeObj(cc)
        cc.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_cp) # remove possibly unused point _cp

    def __delChamfer(self, ch):
        """Remove a Chamfer from the Layer.

_delChamfer(ch)

This method is private to the Layer.
        """
        _chamfers = self.__chamfers
        _idx = None
        for _i in range(len(_chamfers)):
            if ch is _chamfers[_i]:
                _idx = _i
                break
        assert _idx is not None, "lost chamfer from list"
        for _user in ch.getUsers(): # could be hatching ...
            _layer = _user.getParent()
            if _layer is self:
                if not self.inUndo() and not self.inRedo():
                    self.delObject(_user)
                else:
                    ch.freeUser(_user)
                    ch.disconnect(_user)
            elif _layer is not None:
                raise RuntimeError, "Chamfer " + `ch` + " bound to non-layer object: " + `_user`
            else:
                pass
        _s1, _s2 = ch.getSegments()
        assert id(_s1) in self.__objects, "Chamfer s1 segment not in objects"
        assert id(_s2) in self.__objects, "Chamfer s2 segment not in objects"
        del _chamfers[_idx] # restore the things the chamfer connects?
        self.__freeObj(ch)
        ch.finish()

    def __delFillet(self, fl):
        """Remove a Fillet from the Layer.

_delFillet(fl)

This method is private to the Layer.
        """
        _fillets = self.__fillets
        _idx = None
        for _i in range(len(_fillets)):
            if fl is _fillets[_i]:
                _idx = _i
                break
        assert _idx is not None, "lost fillet from list"
        for _user in fl.getUsers(): # could be hatching ...
            _layer = _user.getParent()
            if _layer is self:
                if not self.inUndo() and not self.inRedo():
                    self.delObject(_user)
                else:
                    fl.freeUser(_user)
                    fl.disconnect(_user)
            elif _layer is not None:
                raise RuntimeError, "Fillet " + `fl` + " bound to non-layer object: " + `_user`
            else:
                pass
        _s1, _s2 = fl.getSegments()
        assert id(_s1) in self.__objects, "Fillet s1 segment not in objects"
        assert id(_s2) in self.__objects, "Fillet s2 segment not in objects"
        del _fillets[_idx] # restore the things the fillet connects?
        self.__freeObj(fl)
        fl.finish()

    def __delLeader(self, l):
        """Delete a Leader from the Layer.

_delLeader(l, f)

This method is private to the Layer object.
        """
        _p1, _p2, _p3 = l.getPoints()
        assert id(_p1) in self.__objects, "Leader p1 Point not in objects"
        assert id(_p2) in self.__objects, "Leader p2 Point not in objects"
        assert id(_p3) in self.__objects, "Leader p3 Point not in objects"
        self.__leaders.delObject(l)
        self.__freeObj(l)
        l.finish()
        if not self.inUndo() and not self.inRedo():
            self.delObject(_p1) # remove possibly unused point _p1
            self.delObject(_p2) # remove possibly unused point _p2
            self.delObject(_p3) # remove possibly unused point _p3

    def __delPolyline(self, pl):
        """Delete a Polyline from the Layer.

_delPolyline(pl, f)

This method is private to the Layer object.
        """
        for _user in pl.getUsers(): # could be hatching
            _layer = _user.getParent()
            if _layer is self:
                if not self.inUndo() and not self.inRedo():
                    self.delObject(_user)
                else:
                    pl.freeUser(_user)
                    pl.disconnect(_user)
            elif _layer is not None:
                raise RuntimeError, "Polyline " + `pl` + " bound to non-layer object: " + `_user`
            else:
                pass
        _pts = pl.getPoints()
        for _pt in _pts:
            assert id(_pt) in self.__objects, "Polyline point not in objects"
        self.__polylines.delObject(pl)
        self.__freeObj(pl)
        pl.finish()
        if not self.inUndo() and not self.inRedo():
            for _pt in _pts:
                self.delObject(_pt) # remove possibly unused point _pt

    def __delTextBlock(self, tb):
        """Delete a TextBlock from the Layer.

_delTextBlock(tb)

This method is private to the Layer object.
        """
        _tbs = self.__textblocks
        _idx = None
        for _i in range(len(_tbs)):
            if tb is _tbs[_i]:
                _idx = _i
                break
        assert _idx is not None, "lost textblock in list"
        del _tbs[_idx]
        self.__freeObj(tb)
        tb.finish()

    def __delAngularDimension(self, adim):
        """Delete an AngularDimension from the Layer.

_delAngularDimension(adim, f)

This method is private to the Layer object.
        """
        _p1, _p2, _p3 = adim.getDimPoints()
        if _p1.getParent() is self:
            assert id(_p1) in self.__objects, "ADim P1 not in objects"
        if _p2.getParent() is self:
            assert id(_p2) in self.__objects, "ADim P2 not in objects"
        if _p3.getParent() is self:
            assert id(_p3) in self.__objects, "ADim P3 not in objects"
        self.__adims.delObject(adim)
        self.__freeObj(adim)
        adim.finish()

    def __delRadialDimension(self, rdim):
        """Delete a RadialDimension from the Layer.

_delRadialDimension(rdim, f)

This method is private to the Layer object.
        """
        _circ = rdim.getDimCircle()
        if _circ.getParent() is self:
            assert id(_circ) in self.__objects, "RDim circle not in objects"
        self.__rdims.delObject(rdim)
        self.__freeObj(rdim)
        rdim.finish()

    def __delHorizontalDimension(self, hdim):
        """Delete an HorizontalDimension from the Layer.

_delHorizontalDimension(hdim, f)

This method is private to the Layer object.
        """
        _p1, _p2 = hdim.getDimPoints()
        if _p1.getParent() is self:
            assert id(_p1) in self.__objects, "HDim P1 not in objects"
        if _p2.getParent() is self:
            assert id(_p2) in self.__objects, "HDim P2 not in objects"
        self.__hdims.delObject(hdim)
        self.__freeObj(hdim)
        hdim.finish()

    def __delVerticalDimension(self, vdim):
        """Delete an VerticalDimension from the Layer.

_delVerticalDimension(vdim, f)

This method is private to the Layer object.
        """
        _p1, _p2 = vdim.getDimPoints()
        if _p1.getParent() is self:
            assert id(_p1) in self.__objects, "VDim P1 not in objects"
        if _p2.getParent() is self:
            assert id(_p2) in self.__objects, "VDim P2 not in objects"
        self.__vdims.delObject(vdim)
        self.__freeObj(vdim)
        vdim.finish()

    def __delLinearDimension(self, ldim):
        """Delete an LinearDimension from the Layer.

_delLinearDimension(ldim, f)

This method is private to the Layer object.
        """
        _p1, _p2 = ldim.getDimPoints()
        if _p1.getParent() is self:
            assert id(_p1) in self.__objects, "LDim P1 not in objects"
        if _p2.getParent() is self:
            assert id(_p2) in self.__objects, "LDim P2 not in objects"
        self.__ldims.delObject(ldim)
        self.__freeObj(ldim)
        ldim.finish()

    def getObject(self, eid):
        """
            Return an object of with a specified entity ID.
            Argument eid is an entity ID.
        """
        return self.__objids.get(eid)

    def hasObject(self, eid):
        """
            Argument eid is an entity ID.
        """
        return eid in self.__objids

    def findObject(self, obj):
        """
            Return an object in the layer that is equivalent to a test object.
            This method returns None if a suitable object is not found.
        """
        _retobj = None
        if id(obj) in self.__objects:
            _retobj = obj
        else:
            _objs = []
            if isinstance(obj, point.Point):
                _x, _y = obj.getCoords()
                _objs.extend(self.__points.find(_x, _y))
            elif isinstance(obj, segment.Segment):
                _p1, _p2 = obj.getEndpoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                _objs.extend(self.__segments.find(_x1, _y1, _x2, _y2))
            elif isinstance(obj, arc.Arc):
                _x, _y = obj.getCenter().getCoords()
                _r = obj.getRadius()
                _sa = obj.getStartAngle()
                _ea = obj.getEndAngle()
                _objs.extend(self.__arcs.find(_x, _y, _r, _sa, _ea))
            elif isinstance(obj, circle.Circle):
                _x, _y = obj.getCenter().getCoords()
                _r = obj.getRadius()
                _objs.extend(self.__circles.find(_x, _y, _r))
            elif isinstance(obj, hcline.HCLine):
                _y = obj.getLocation().y
                _objs.extend(self.__hclines.find(_y))
            elif isinstance(obj, vcline.VCLine):
                _x = obj.getLocation().x
                _objs.extend(self.__vclines.find(_x))
            elif isinstance(obj, acline.ACLine):
                _x, _y = obj.getLocation().getCoords()
                _angle = obj.getAngle()
                _objs.extend(self.__aclines.find(_x, _y, _angle))
            elif isinstance(obj, cline.CLine):
                _p1, _p2 = obj.getKeypoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                _objs.extend(self.__clines.find(_x1, _y1, _x2, _y2))
            elif isinstance(obj, ccircle.CCircle):
                _x, _y = obj.getCenter().getCoords()
                _r = obj.getRadius()
                _objs.extend(self.__ccircles.find(_x, _y, _r))
            elif isinstance(obj, segjoint.Fillet):
                for _f in self.__fillets:
                    if _f is obj:
                        _retobj = _f
                        break
            elif isinstance(obj, segjoint.Chamfer):
                for _c in self.__chamfers:
                    if _c == obj:
                        _retobj = _f
                        break
            elif isinstance(obj, leader.Leader):
                _p1, _p2, _p3 = obj.getPoints()
                _x1, _y1 = _p1.getCoords()
                _x2, _y2 = _p2.getCoords()
                _x3, _y3 = _p3.getCoords()
                _objs.extend(self.__leaders.find(_x1, _y1, _x2, _y2, _x3, _y3))
            elif isinstance(obj, polyline.Polyline):
                _coords = []
                for _pt in obj.getPoints():
                    _coords.append(_pt.getCoords())
                _objs.extend(self.__polylines.find(_coords))
            elif isinstance(obj, text.TextBlock):
                for _tb in self.__textblocks:
                    if _tb == obj:
                        _retobj = _f
                        break
            elif isinstance(obj, dimension.HorizontalDimension):
                _p1, _p2 = obj.getDimPoints()
                _objs.extend(self.__hdims.find(_p1, _p2))
            elif isinstance(obj, dimension.VerticalDimension):
                _p1, _p2 = obj.getDimPoints()
                _objs.extend(self.__vdims.find(_p1, _p2))
            elif isinstance(obj, dimension.LinearDimension):
                _p1, _p2 = obj.getDimPoints()
                _objs.extend(self.__ldims.find(_p1, _p2))
            elif isinstance(obj, dimension.RadialDimension):
                _c1 = obj.getDimCircle()
                _objs.extend(self.__rdims.find(_c1))
            elif isinstance(obj, dimension.AngularDimension):
                _vp, _p1, _p2 = obj.getDimPoints()
                _objs.extend(self.__adims.find(_vp, _p1, _p2))
            else:
                raise TypeError, "Invalid object type: " + `type(obj)`
            if _retobj is not None:
                for _obj in _objs:
                    if _obj is obj:
                        _retobj = _obj
                        break
        return _retobj

    def find(self, typestr, *args):
        """
            Find an existing entity in the drawing.
            typestr: A string giving the type of entity to find
            *args: A variable number of arguments used for searching
        """
        if not isinstance(typestr, str):
            raise TypeError, "Invalid type string: " + `type(typestr)`
        _objs = []
        if typestr == 'point':
            _objs.extend(self.__points.find(*args))
        elif typestr == 'segment':
            _objs.extend(self.__segments.find(*args))
        elif typestr == 'circle':
            _objs.extend(self.__circles.find(*args))
        elif typestr == 'arc':
            _objs.extend(self.__arcs.find(*args))
        elif typestr == 'hcline':
            _objs.extend(self.__hclines.find(*args))
        elif typestr == 'vcline':
            _objs.extend(self.__vclines.find(*args))
        elif typestr == 'acline':
            _objs.extend(self.__aclines.find(*args))
        elif typestr == 'cline':
            _objs.extend(self.__clines.find(*args))
        elif typestr == 'ccircle':
            _objs.extend(self.__ccircles.find(*args))
        elif typestr == 'leader':
            _objs.extend(self.__leaders.find(*args))
        elif typestr == 'polyline':
            _objs.extend(self.__polylines.find(*args))
        elif typestr == 'ldim':
            _objs.extend(self.__ldims.find(*args))
        elif typestr == 'hdim':
            _objs.extend(self.__hdims.find(*args))
        elif typestr == 'vdim':
            _objs.extend(self.__vdims.find(*args))
        elif typestr == 'rdim':
            _objs.extend(self.__rdims.find(*args))
        elif typestr == 'adim':
            _objs.extend(self.__adims.find(*args))
        else:
            raise ValueError, "Unexpected type string '%s'" % typestr
        return _objs

    def mapPoint(self, p, tol=tolerance.TOL, count=2):
        """
            Find a Point in the layer
            There is a single required argument:
            p: Either a Point object or a tuple of two-floats
            There are two optional arguments:
            tol: A float equal or greater than 0 for distance tolerance comparisons.
            count: An integer value indicating the largest number of objects to
            return. By default this value is 2.
            Setting 'count' to None or a negative value will result in the maximum
            number of objects being unlimited.
            This method tests the objects in the Layer to see if the
            Point can be mapped on to any of them. The returned list
            consists of tuples in the form:
            (obj, pt)
            Where 'obj' is the object the point was mapped to and 'pt'
            is the projected point on the object.
        """
        _hits = []
        _p = p
        if not isinstance(_p, point.Point):
            _p = point.Point(p)
        _t = tolerance.toltest(tol)
        _count = count
        if _count is None:
            _count = sys.maxint
        else:
            if not isinstance(_count, int):
                _count = int(count)
            if _count < 0:
                _count = sys.maxint
        if _count < 1: # bail out, but why set count to this value?
            return _hits
        _x, _y = _p.getCoords()
        _xmin = _x - _t
        _xmax = _x + _t
        _ymin = _y - _t
        _ymax = _y + _t
        #
        # scan for non-point objects first, then look at points,
        # because there will not be any way the same object can
        # be found in differnt trees/lists
        #
        for _obj in self.__segments.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__circles.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__arcs.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__hclines.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__vclines.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__aclines.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__ccircles.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__clines.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__leaders.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__polylines.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__ldims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__hdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__vdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__rdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        for _obj in self.__adims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _pt = _obj.mapCoords(_x, _y, _t)
            if _pt is not None:
                _px, _py = _pt
                _pts = self.__points.find(_px, _py)
                if len(_pts) == 0:
                    _pts.append(point.Point(_px, _py))
                for _pt in _pts:
                    _hits.append((_obj, _pt))
                    if len(_hits) == _count:
                        return _hits
        #
        # scan for point, but do not append any object that
        # has already been added to the hit list
        #
        _objs = {}
        for _obj, _pt in _hits:
            _objs[id(_obj)] = True
        _pts = self.find('point', _x, _y, _t)
        if len(_pts) != 0:
            for _pt in _pts:
                assert id(_pt) in self.__objects, "Point not in objects"
                for _user in _pt.getUsers():
                    _uid = id(_user)
                    if _uid not in _objs:
                        _objs[_uid] = True
                        _hits.append((_user, _pt))
                        if len(_hits) == _count:
                            break
        return _hits

    def mapCoords(self, x, y, **kw):
        """
            Find objects at coordinates in the Layer.
            Arguments 'x' and 'y' are mandatory and should be float values.
            Non-float values will be converted to that type if possible.
            There are several optional keyword arguments:
            tolerance: A float equal or greater than 0 for distance tolerance comparisons.
            count: An integer value indicating the largest number of objects to
                   return. By default this value is the sys.maxint value, essentially
                   making the count unlimited.
            types: A dictionary containing key/value pairs. If any key is given a
                   value of 'True', only types for keys with 'True' values are examined.
                   If any  key is given a 'False' value, the type corresponding to that
                   key is skipped.
                    This method tests the objects in the Layer to see if the specified
                    x/y coordiantes can can be mapped on to any of them. The returned list
                    consists of tuples in the form:(obj, {var})
            Where 'obj' is the object the point was mapped to and '{var}'
            is either an existing Point in the Layer or a tuple of the
            form (x, y) giving the coordinates where a new Point can be
            added.
        """
        #
        # utility function for testing whether or not an entity type
        # is to be examined
        #
        def _test_entity(tdict, skip, etype):
            _rv = True
            if tdict is not None:
                if skip is True:
                    if not tdict.has_key(etype) or tdict[etype] is not True:
                        _rv = False
                else:
                    if tdict.has_key(etype) and tdict[etype] is False:
                        _rv = False
            return _rv
        _x = util.get_float(x)
        _y = util.get_float(y)
        _t = 1e-10
        _types = None
        _skip = False
        _count = sys.maxint
        if 'tolerance' in kw:
            _val = util.get_float(kw['tolerance'])
            if _val < 0.0:
                raise ValueError, "Invalid negative tolerance: %f" % _val
            _t = _val
        if 'count' in kw:
            _val = kw['count']
            if not isinstance(_val, int):
                _val = int(kw['count'])
            if _val < 0:
                raise ValueError, "Invalid negative entity count %d" % _val
        if 'types' in kw:
            _val = kw['types']
            if not isinstance(_val, dict):
                raise TypeError, "Invalid 'types' dictionary: " + `type(_val)`
            for _k, _v in _val.items():
                if not isinstance(_k, str):
                    raise TypeError, "Invalid key %s type: %s " (str(_k), `type(_k)`)
                util.test_boolean(_v)
                if _skip is False and _v is True:
                    _skip = True
            _types = _val
        _hits = []
        if _count == 0:
            return _hits
        _xmin = _x - _t
        _xmax = _x + _t
        _ymin = _y - _t
        _ymax = _y + _t
        #
        # start testing entities
        #
        if _test_entity(_types, _skip, 'point'):
            _pts = self.__points.getInRegion(_xmin, _ymin, _xmax, _ymax)
            if len(_pts):
                _plist = []
                for _pt in _pts:
                    _sqlen = pow((_x - _pt.x), 2) + pow((_y - _pt.y), 2)
                    _plist.append((_sqlen, _pt))
                _plist.sort() # sorts tuples by first value!
                for _sqlen, _pt in _plist:
                    _hits.append((_pt, _pt))
                    if len(_hits) == _count:
                        return _hits
                # _users = {}
                # for _i in range(len(_pts)):
                    # _pt = _pts[_i]
                    # _count = _pt.countUsers()
                    # _ulist = _users.setdefault(_count, [])
                    # _ulist.append(_pt)
                # _counts = _users.keys()
                # _counts.sort(lambda _a, _b: cmp(_b, _a)) # largest to smallest
                # for _i in range(len(_counts)):
                    # _count = _counts[_i]
                    # for _pt in _users[_count]:
                        # _hits.append((_pt, _pt))
                        # if len(_hits) == _count:
                            # return _hits
        if _test_entity(_types, _skip, 'segment'):
            for _obj in self.__segments.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _p1, _p2 = _obj.getEndpoints()
                    if ((abs(_px - _p1.x) < _t) and (abs(_py - _p1.y) < _t)):
                        _hits.append((_obj, _p1))
                    elif ((abs(_px - _p2.x) < _t) and (abs(_py - _p2.y) < _t)):
                        _hits.append((_obj, _p2))
                    else:
                        _hits.append((_obj, (_px, _py)))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'circle'):
            for _obj in self.__circles.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'arc'):
            for _obj in self.__arcs.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'hcline'):
            for _obj in self.__hclines.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _lp = _obj.getLocation()
                    if ((abs(_px - _lp.x) < _t) and (abs(_py - _lp.y) < _t)):
                        _hits.append((_obj, _lp))
                    else:
                        _hits.append((_obj, (_px, _py)))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'vcline'):
            for _obj in self.__vclines.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _lp = _obj.getLocation()
                    if ((abs(_px - _lp.x) < _t) and (abs(_py - _lp.y) < _t)):
                        _hits.append((_obj, _lp))
                    else:
                        _hits.append((_obj, (_px, _py)))              
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'acline'):
            for _obj in self.__aclines.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _lp = _obj.getLocation()
                    if ((abs(_px - _lp.x) < _t) and (abs(_py - _lp.y) < _t)):
                        _hits.append((_obj, _lp))
                    else:
                         _hits.append((_obj, (_px, _py)))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'ccircle'):
            for _obj in self.__ccircles.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'cline'):
            for _obj in self.__clines.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _p1, _p2 = _obj.getKeypoints()
                    if ((abs(_px - _p1.x) < _t) and (abs(_py - _p1.y) < _t)):
                        _hits.append((_obj, _p1))
                    elif ((abs(_px - _p2.x) < _t) and (abs(_py - _p2.y) < _t)):
                        _hits.append((_obj, _p2))
                    else:
                        _hits.append((_obj, (_px, _py)))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'leader'):
            for _obj in self.__leaders.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _p1, _p2, _p3 = _obj.getPoints()
                    if ((abs(_px - _p1.x) < _t) and (abs(_py - _p1.y) < _t)):
                        _hits.append((_obj, _p1))
                    elif ((abs(_px - _p2.x) < _t) and (abs(_py - _p2.y) < _t)):
                        _hits.append((_obj, _p2))
                    elif ((abs(_px - _p3.x) < _t) and (abs(_py - _p3.y) < _t)):
                        _hits.append((_obj, _p3))
                    else:
                        _hits.append((_obj, (_px, _py)))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'polyline'):
            for _obj in self.__polylines.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _px, _py = _pt
                    _pp = None
                    for _tp in _obj.getPoints():
                        if ((abs(_px - _tp.x) < _t) and
                            (abs(_py - _tp.y) < _t)):
                            _pp = _tp
                            break
                    if _pp is not None:
                        _hits.append((_obj, _pp))
                    else:
                        _hits.append((_obj, (_px, _py)))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'linear_dimension'):
            for _obj in self.__ldims.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'horizontal_dimension'):
            for _obj in self.__hdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'vertical_dimension'):
            for _obj in self.__vdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'radial_dimension'):
            for _obj in self.__rdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        if _test_entity(_types, _skip, 'angular_dimension'):
            for _obj in self.__adims.getInRegion(_xmin, _ymin, _xmax, _ymax):
                _pt = _obj.mapCoords(_x, _y, _t)
                if _pt is not None:
                    _hits.append((_obj, (_pt[0], _pt[1])))
                    if len(_hits) == _count:
                        return _hits
        return _hits

    def hasEntities(self):
        """
            Test if the Layer has entities.
            This method returns a boolean
        """
        if (self.__points or
            self.__segments or
            self.__circles or
            self.__arcs or
            self.__leaders or
            self.__polylines or
            self.__hclines or
            self.__vclines or
            self.__aclines or
            self.__clines or
            self.__ccircles or
            (len(self.__chamfers) > 0) or
            (len(self.__fillets) > 0) or
            (len(self.__textblocks) > 0) or
            self.__ldims or
            self.__hdims or
            self.__vdims or
            self.__rdims or
            self.__adims):
            return True
        return False

    def getEntityCount(self, etype):
        """
            Return the number of an entity type stored in the  Layer
            The argument 'etype' should be one of the following:
            point, segment, circle, arc, hcline, vcline, acline,
            cline, ccircle, chamfer, fillet, leader, polyline,
            textblock, linear_dimension, horizontal_dimenions,
            vertical_dimension, radial_dimension, or angular_dimension.
        """
        if etype == "point":
            _res = len(self.__points)
        elif etype == "segment":
            _res = len(self.__segments)
        elif etype == "circle":
            _res = len(self.__circles)
        elif etype == "arc":
            _res = len(self.__arcs)
        elif etype == "leader":
            _res = len(self.__leaders)
        elif etype == "polyline":
            _res = len(self.__polylines)
        elif etype == "chamfer":
            _res = len(self.__chamfers)
        elif etype == "fillet":
            _res = len(self.__fillets)
        elif etype == "hcline":
            _res = len(self.__hclines)
        elif etype == "vcline":
            _res = len(self.__vclines)
        elif etype == "acline":
            _res = len(self.__aclines)
        elif etype == "cline":
            _res = len(self.__clines)
        elif etype == "ccircle":
            _res = len(self.__ccircles)
        elif etype == "text" or etype == 'textblock':
            _res = len(self.__textblocks)
        elif etype == "linear_dimension":
            _res = len(self.__ldims)
        elif etype == "horizontal_dimension":
            _res = len(self.__hdims)
        elif etype == "vertical_dimension":
            _res = len(self.__vdims)
        elif etype == "radial_dimension":
            _res = len(self.__rdims)
        elif etype == "angular_dimension":
            _res = len(self.__adims)
        else:
            raise ValueError, "Unexpected entity type string'%s'" % etype
        return _res
    
    def getLayerEntities(self, entity):
        """
            Get all of a particular type of entity in the Layer.
            The argument 'entity' should be one of the following:
            point, segment, circle, arc, hcline, vcline, acline,
            cline, ccircle, chamfer, fillet, leader, polyline,
            textblock, linear_dimension, horizontal_dimenions,
            vertical_dimension, radial_dimension, or angular_dimension.
        """
        if not isinstance(entity, str):
            raise TypeError, "Invalid entity type: " + `type(entity)`
        if entity == "point":
            _objs = self.__points.getObjects()
        elif entity == "segment":
            _objs = self.__segments.getObjects()
        elif entity == "circle":
            _objs = self.__circles.getObjects()
        elif entity == "arc":
            _objs = self.__arcs.getObjects()
        elif entity == "hcline":
            _objs = self.__hclines.getObjects()
        elif entity == "vcline":
            _objs = self.__vclines.getObjects()
        elif entity == "acline":
            _objs = self.__aclines.getObjects()
        elif entity == "cline":
            _objs = self.__clines.getObjects()
        elif entity == "ccircle":
            _objs = self.__ccircles.getObjects()
        elif entity == "chamfer":
            _objs = self.__chamfers[:]
        elif entity == "fillet":
            _objs = self.__fillets[:]
        elif entity == "leader":
            _objs = self.__leaders.getObjects()
        elif entity == "polyline":
            _objs = self.__polylines.getObjects()
        elif entity == "text" or entity == 'textblock':
            _objs = self.__textblocks[:]
        elif entity == "linear_dimension":
            _objs = self.__ldims.getObjects()
        elif entity == "horizontal_dimension":
            _objs = self.__hdims.getObjects()
        elif entity == "vertical_dimension":
            _objs = self.__vdims.getObjects()
        elif entity == "radial_dimension":
            _objs = self.__rdims.getObjects()
        elif entity == "angular_dimension":
            _objs = self.__adims.getObjects()
        else:
            raise ValueError, "Invalid layer entity '%s'" % entity
        return _objs
    
    def getAllEntitys(self):
        """
            Return all the entity stored in the layer
        """
        _entArray=[
            'point', 'segment', 'circle', 'arc', 'hcline', 'vcline', 'acline',
            'cline', 'ccircle', 'chamfer', 'fillet', 'leader', 'polyline',
            'textblock', 'horizontal_dimension','linear_dimension',
            'vertical_dimension','radial_dimension','angular_dimension']
        _eArr=[]
        for _e in _entArray:
            _objs=self.getLayerEntities(_e)
            for _o in _objs:
                _eArr.append(_o)
        return _eArr
    
    def canParent(self, obj):
        """
            Test if an Entity can be the parent of another Entity.
            This method overrides the Entity::canParent() method. A layer can
            be the parent of any object contained within itself.
        """
        return isinstance(obj, (point.Point, segment.Segment,
                                circle.Circle, arc.Arc,
                                leader.Leader, polyline.Polyline,
                                hcline.HCLine, vcline.VCLine,
                                acline.ACLine, cline.CLine, segjoint.SegJoint,
                                ccircle.CCircle, dimension.Dimension,
                                dimension.DimString, # ???
                                text.TextBlock))


    def setParentLayer(self, parent):
        """
            Store the parent layer of a layer within itself.
            Argument 'parent' must be either another Layer or None.
        """
        if parent is not None and not isinstance(parent, Layer):
            raise TypeError, "Invalid layer type: " + `type(parent)`
        _p = self.__parent_layer
        if _p is not parent:
            if _p is not None:
                _p.delSublayer(self)
            if parent is not None:
                parent.addSublayer(self)
            self.__parent_layer = parent
            self.sendMessage('reparented', _p)
            self.modified()

    def getParentLayer(self):
        return self.__parent_layer

    def addSublayer(self, l):
        if l is not None and not isinstance(l, Layer):
            raise TypeError, "Invalid layer type: " + `type(l)`
        if self.__sublayers is None:
            self.__sublayers = []
        if l in self.__sublayers:
            raise ValueError, "Layer already a sublayer: " + `l`
        self.__sublayers.append(l)
        self.sendMessage('added_sublayer', l)
        self.modified()

    def delSublayer(self, l):
        if l is not None and not isinstance(l, Layer):
            raise TypeError, "Invalid layer type: " + `type(l)`
        if self.__sublayers is None:
            raise ValueError, "Layer has no sublayers: " + `self`
        if l not in self.__sublayers:
            raise ValueError, "Layer not a sublayer: " + `l`
        self.__sublayers.remove(l)
        if len(self.__sublayers) == 0:
            self.__sublayers = None
        self.sendMessage('deleted_sublayer', l)
        self.modified()

    def hasSublayers(self):
        return self.__sublayers is not None and len(self.__sublayers) > 0

    def getSublayers(self):
        if self.__sublayers is not None:
            return self.__sublayers[:]
        return []

    def getScale(self):
        """
            Return the scale factor of the Layer.
        """
        return self.__scale

    def setScale(self, scale):
        """
            Set the scale factor for the Layer.
            The scale factor must be a positive float value greater than 0.0
        """
        _s = util.get_float(scale)
        if _s < 1e-10:
            raise ValueError, "Invalid scale factor: %g" % _s
        _os = self.__scale
        if abs(_os - _s) > 1e-10:
            self.startChange('scale_changed')
            self.__scale = _s
            self.endChange('scale_changed')
            self.sendMessage('scale_changed', _os)
            self.modified()

    scale = property(getScale, setScale, None, "Layer scale factor.")

    def getBoundary(self):
        """
            Return the maximum and minimum values of the object in the Layer.
            The function returns a tuple holding four float values:
            (xmin, ymin, xmax, _ymax)
            A default value of (-1.0, -1.0, 1.0, 1.0) is returned for a Layer
            containing no objects.
        """
        _xmin = None
        _ymin = None
        _xmax = None
        _ymax = None
        for _obj in self.__points.getObjects():
            _x, _y = _obj.getCoords()
            if _xmin is None or _x < _xmin:
                _xmin = _x
            if _ymin is None or _y < _ymin:
                _ymin = _y
            if _xmax is None or _x > _xmax:
                _xmax = _x
            if _ymax is None or _y > _ymax:
                _ymax = _y
        for _obj in self.__arcs.getObjects():
            _axmin, _aymin, _axmax, _aymax = _obj.getBounds()
            if _xmin is None or _axmin < _xmin:
                _xmin = _axmin
            if _ymin is None or _aymin < _ymin:
                _ymin = _aymin
            if _xmax is None or _axmax > _xmax:
                _xmax = _axmax
            if _ymax is None or _aymax > _ymax:
                _ymax = _aymax
        for _obj in self.__circles.getObjects() + self.__ccircles.getObjects():
            _x, _y = _obj.getCenter().getCoords()
            _r = _obj.getRadius()
            _val = _x - _r
            if _xmin is None or _val < _xmin:
                _xmin = _val
            _val = _y - _r
            if _ymin is None or _val < _ymin:
                _ymin = _val
            _val = _x + _r
            if _xmax is None or _val > _xmax:
                _xmax = _val
            _val = _y + _r
            if _ymax is None or _val > _ymax:
                _ymax = _val
        _dims = (self.__ldims.getObjects() +
                 self.__hdims.getObjects() +
                 self.__vdims.getObjects() +
                 self.__rdims.getObjects() +
                 self.__adims.getObjects())
        for _obj in _dims:
            _dxmin, _dymin, _dxmax, _dymax = _obj.getBounds()
            if _xmin is None or _dxmin < _xmin:
                _xmin = _dxmin
            if _ymin is None or _dymin < _ymin:
                _ymin = _dymin
            if _xmax is None or _dxmax > _xmax:
                _xmax = _dxmax
            if _ymax is None or _dymax > _ymax:
                _ymax = _dymax
            _ds1, _ds2 = _obj.getDimstrings()
            _x, _y = _ds1.getLocation()
            _bounds = _ds1.getBounds()
            if _bounds is not None:
                _w, _h = _bounds
                if _x < _xmin:
                    _xmin = _x
                if (_y - _h) < _ymin:
                    _ymin = (_y - _h)
                if (_x + _w) > _xmax:
                    _xmax = (_x + _w)
                if _y > _ymax:
                    _ymax = _y
            if _obj.getDualDimMode():
                _x, _y = _ds2.getLocation()
                _bounds = _ds2.getBounds()
                if _bounds is not None:
                    _w, _h = _bounds
                    if _x < _xmin:
                        _xmin = _x
                    if (_y - _h) < _ymin:
                        _ymin = (_y - _h)
                    if (_x + _w) > _xmax:
                        _xmax = (_x + _w)
                    if _y > _ymax:
                        _ymax = _y
        for _textblock in self.__textblocks:
            _x, _y = _textblock.getLocation() # upper left corner
            _w = _h = 0.0
            _bounds = _textblock.getBounds()
            if _bounds is not None:
                _w, _h = _bounds
                _align = _textblock.getAlignment()
                if _align != text.TextStyle.ALIGN_LEFT:
                    if _align == text.TextStyle.ALIGN_CENTER:
                        _x = _x - _w/2.0
                    elif _align == text.TextStyle.ALIGN_RIGHT:
                        _x = _x - _w
            if _xmin is None or _x < _xmin:
                _xmin = _x
            if _ymin is None or (_y - _h) < _ymin:
                _ymin = (_y - _h)
            if _xmax is None or (_x + _w) > _xmax:
                _xmax = (_x + _w)
            if _ymax is None or _y > _ymax:
                _ymax = _y
        if _xmin is None: _xmin = -1.0
        if _ymin is None: _ymin = -1.0
        if _xmax is None: _xmax = 1.0
        if _ymax is None: _ymax = 1.0
        return _xmin, _ymin, _xmax, _ymax

    def objsInRegion(self, xmin, ymin, xmax, ymax, fully=False):
        """
            Return a all the objects in the Layer visible within the bounds.
            The function has four required arguments:
            xmin: The minimum x-value of the region
            ymin: The minimum y-value of the region
            xmax: The maximum x-value of the region
            ymax: The maximum y-value of the region
            There is a single optional argument:
            fully: A True/False value indicating if the object must be
                   entirely within the region [fully=True], or can
                   merely pass through [fully=False]. The default value
                   is False.
            The function returns a list of objects.
        """
        _xmin = util.get_float(xmin)
        _ymin = util.get_float(ymin)
        _xmax = util.get_float(xmax)
        if xmax < xmin:
            raise ValueError, "Value error: xmax < xmin"
        _ymax = util.get_float(ymax)
        if _ymax < _ymin:
            raise ValueError, "Value error: ymax < ymin"
        util.test_boolean(fully)
        _objs = []
        _objs.extend(self.__points.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__segments.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__circles.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__arcs.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__hclines.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__vclines.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__aclines.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__clines.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__ccircles.getInRegion(_xmin, _ymin, _xmax, _ymax))
        for _obj in self.__chamfers:
            if _obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _objs.append(_obj)
        _objs.extend(self.__leaders.getInRegion(_xmin, _ymin, _xmax, _ymax))
        _objs.extend(self.__polylines.getInRegion(_xmin, _ymin, _xmax, _ymax))
        for _obj in self.__fillets:
            if _obj.inRegion(_xmin, _ymin, _xmax, _ymax):
                _objs.append(_obj)
        for _obj in self.__ldims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _objs.append(_obj)
            _ds1, _ds2 = _obj.getDimstrings()
            _objs.append(_ds1)
            if _obj.getDualDimMode():
                _objs.append(_ds2)
        for _obj in self.__hdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _objs.append(_obj)
            _ds1, _ds2 = _obj.getDimstrings()
            _objs.append(_ds1)
            if _obj.getDualDimMode():
                _objs.append(_ds2)
        for _obj in self.__vdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _objs.append(_obj)
            _ds1, _ds2 = _obj.getDimstrings()
            _objs.append(_ds1)
            if _obj.getDualDimMode():
                _objs.append(_ds2)
        for _obj in self.__rdims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _objs.append(_obj)
            _ds1, _ds2 = _obj.getDimstrings()
            _objs.append(_ds1)
            if _obj.getDualDimMode():
                _objs.append(_ds2)
        for _obj in self.__adims.getInRegion(_xmin, _ymin, _xmax, _ymax):
            _objs.append(_obj)
            _ds1, _ds2 = _obj.getDimstrings()
            _objs.append(_ds1)
            if _obj.getDualDimMode():
                _objs.append(_ds2)
        for _obj in self.__textblocks:
            _x, _y = _obj.getLocation()
            _bounds = _obj.getBounds()
            if _bounds is not None:
                _w, _h = _bounds
            else:
                _w = _h = 0                
            _txmin = _x
            _txmax = _x + _w
            _tymin = _y - _h
            _tymax = _y
            if not ((_txmax < _xmin) or
                    (_txmin > _xmax) or
                    (_tymax < _ymin) or
                    (_tymin > _ymax)):
                _objs.append(_obj)
        return _objs

    def sendsMessage(self, m):
        if m in Layer.__messages:
            return True
        return super(Layer, self).sendsMessage(m)

    def update(self):
        """
            Check that the objects in this layer are stored correctly.
            This function checks that the objects held in this layer are kept
            in the proper order. Also, any duplicated objects that may have
            be created due to modifying entities in the layer are removed.
        """
        raise RuntimeError, "Layer::update() called."

#
# Layer history class
#

class LayerLog(entity.EntityLog):
    def __init__(self, l):
        if not isinstance(l, Layer):
            raise TypeError, "Invalid layer type: " + `type(l)`
        super(LayerLog, self).__init__(l)
        l.connect('scale_changed', self.__scaleChanged)
        l.connect('name_changed', self.__nameChanged)
        l.connect('added_child', self.__addedChild)
        l.connect('removed_child', self.__removedChild)

    def __addedChild(self, l, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        _vals = _obj.getValues()
        if not isinstance(_vals, entity.EntityData):
            raise TypeError, "Unexpected type for values: " + `type(_obj)`
        _vals.lock()
        self.saveUndoData('added_child', _vals)

    def __removedChild(self, l, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _obj = args[0]
        _vals = _obj.getValues()
        if not isinstance(_vals, entity.EntityData):
            raise TypeError, "Unexpected type for values: " + `type(_obj)`
        _vals.lock()
        self.saveUndoData('removed_child', _vals)

    def __nameChanged(self, l, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _name = args[0]
        if not isinstance(_name, types.StringTypes):
            raise TypeError, "Unexpected type for name: " + `type(_name)`
        self.saveUndoData('name_changed', _name)

    def __scaleChanged(self, l, *args):
        _alen = len(args)
        if _alen < 1:
            raise ValueError, "Invalid argument count: %d" % _alen
        _scale = args[0]
        if not isinstance(_scale, float):
            raise TypeError, "Unexpected type for scale: " + `type(_scale)`
        if _scale < 1e-10:
            raise ValueError, "Invalid scale: %g" % _scale
        self.saveUndoData('scale_changed', _scale)

    def execute(self, undo, *args):
        # print "LayerLog::execute() ..."
        # print args
        util.test_boolean(undo)
        _alen = len(args)
        if len(args) == 0:
            raise ValueError, "No arguments to execute()"
        _l = self.getObject()
        _op = args[0]
        if _op == 'name_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _l.getName()
            self.ignore(_op)
            try:
                _name = args[1]
                if undo:
                    _l.startUndo()
                    try:
                        _l.setName(_name)
                    finally:
                        _l.endUndo()
                else:
                    _l.startRedo()
                    try:
                        _l.setName(_name)
                    finally:
                        _l.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'scale_changed':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _sdata = _l.getScale()
            self.ignore(_op)
            try:
                _scale = args[1]
                if undo:
                    _l.startUndo()
                    try:
                        _l.setScale(_scale)
                    finally:
                        _l.endUndo()
                else:
                    _l.startRedo()
                    try:
                        _l.setScale(_scale)
                    finally:
                        _l.endRedo()
            finally:
                self.receive(_op)
            self.saveData(undo, _op, _sdata)
        elif _op == 'added_child':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _vals = args[1]
            if not isinstance(_vals, entity.EntityData):
                raise TypeError, "Unexpected type for values: " + `type(_vals)`
            self.ignore('modified')
            try:
                if undo:
                    _sdata = _vals
                    self.ignore('removed_child')
                    try:
                        self.__delObject(undo, _vals)
                    finally:
                        self.receive('removed_child')
                else:
                    _obj = self.__makeObject(_vals)
                    self.ignore(_op)
                    try:
                        _l.startRedo()
                        try:
                            _l.addObject(_obj)
                        finally:
                            _l.endRedo()
                    finally:
                        self.receive(_op)
                    _sdata = _obj.getValues()
                    _sdata.lock()
            finally:
                self.receive('modified')
            self.saveData(undo, _op, _sdata)
        elif _op == 'removed_child':
            if len(args) < 2:
                raise ValueError, "Invalid argument count: %d" % _alen
            _vals = args[1]
            if not isinstance(_vals, entity.EntityData):
                raise TypeError, "Unexpected type for values: " + `type(_vals)`
            self.ignore('modified')
            try:
                if undo:
                    _obj = self.__makeObject(_vals)
                    self.ignore('added_child')
                    try:
                        _l.startUndo()
                        try:
                            _l.addObject(_obj)
                        finally:
                            _l.endUndo()
                        _sdata = _obj.getValues()
                        _sdata.lock()
                    finally:
                        self.receive('added_child')
                else:
                    _sdata = _vals
                    self.ignore(_op)
                    try:
                        self.__delObject(undo, _vals)
                    finally:
                        self.receive(_op)
            finally:
                self.receive('modified')
            self.saveData(undo, _op, _sdata)
        else:
            super(LayerLog, self).execute(undo, *args)

    def __getImageColor(self, r, g, b):
        _image = self.getObject().getParent()
        _color = None
        if _image is not None:
            for _ic in _image.getImageEntities('color'):
                if _ic.r == r and _ic.g == g and _ic.b == b:
                    _color = _ic
                    break
        if _color is None:
            _color = color.Color(r, g, b)
        return _color

    def __makeImageColor(self, values):
        # print "LayerLog::__makeImageColor() ..."
        _image = self.getObject().getParent()
        _cdata = values.get('color')
        _color = None
        if _image is not None and _cdata is not None:
            # print "restoring image color: " + str(_cdata)
            _r, _g, _b = _cdata
            for _ic in _image.getImageEntities('color'):
                if _ic.r == _r and _ic.g == _g and _ic.b == _b:
                    _color = _ic
                    break
        if _color is None and _cdata is not None: # make one
            _r, _g, _b = _cdata
            _color = color.Color(_r, _g, _b)
        return _color
        
    def __makeGraphicLinetype(self, values):
        # print "LayerLog::__makeGraphicLinetype() ..."
        _image = self.getObject().getParent()
        _ltdata = values.get('linetype')
        _linetype = None
        if _image is not None and _ltdata is not None:
            # print "restoring graphic linetype: " + str(_ltdata)
            _name, _dlist = _ltdata
            for _ilt in _image.getImageEntities('linetype'):
                if ((_ilt.getName() == _name) and (_ilt.getList() == _dlist)):
                    _linetype = _ilt
                    break
        if _linetype is None and _ltdata is not None: # make one
            _name, _dlist = _ltdata
            _linetype = linetype.Linetype(_name, _dlist)
        return _linetype
    
    def __makeGraphicStyle(self, values):
        # print "LayerLog::__makeGraphicStyle() ..."
        _image = self.getObject().getParent()
        _sdata = values.get('style')
        _style = None
        if _image is not None and _sdata is not None:
            # print "restoring graphic style: " + str(_sdata)
            _name, _lt, _col, _th = _sdata
            _ln, _ld = _lt
            for _istyle in _image.getImageEntities('style'):
                if _istyle.getName() != _name:
                    continue
                _ilt = _istyle.getLinetype()
                if ((_ilt.getName() != _ln) or (_ilt.getList() != _ld)):
                    continue
                if _istyle.getColor().getColors() != _col:
                    continue
                if abs(_istyle.getThickness() - _th) > 1e-10:
                    continue
                _style = _istyle
                break
        if _style is None and _sdata is not None: # make one
            _name, _lt, _col, _th = _sdata
            _r, _g, _b = _col
            _color = self.__getImageColor(_r, _g, _b)
            _linetype = linetype.Linetype(_lt[0], _lt[1])
            _style = style.Style(_name, _linetype, _color, _th)
        return _style

    def __resetGraphicValues(self, obj, values):
        # print "LayerLog::__resetGraphicValues() ..."
        _style = self.__makeGraphicStyle(values)
        if _style is not None:
            # print "resetting style ..."
            obj.setStyle(_style)
        _linetype = self.__makeGraphicLinetype(values)
        if _linetype is not None:
            # print "resetting linetype ..."
            obj.setLinetype(_linetype)
        _color = self.__makeImageColor(values)
        if _color is not None:
            # print "resetting color ..."
            obj.setColor(_color)
        _thickness = values.get('thickness')
        if _thickness is not None:
            # print "resetting thickness ..."
            obj.setThickness(_thickness)
        
    def __makeTextStyle(self, values):
        # print "LayerLog::__makeTextStyle() ..."
        _image = self.getObject().getParent()
        _tdata = values.get('textstyle')
        _textstyle = None
        if _image is not None and _tdata is not None:
            # print "restoring textstyle: " + str(_tdata)
            for _ts in _image.getImageEntities('textstyle'):
                # print "Comparing stored TextStyle: %s " % _ts.getName()
                if _ts.getName() != _tdata['name']:
                    # print "name differs"
                    continue
                if _ts.getFamily() != _tdata['family']:
                    # print "family differs"
                    continue
                if _ts.getStyle() != _tdata['style']:
                    # print "style differs"
                    continue
                _c = _ts.getColor()
                _r, _g, _b = _tdata['color']
                if ((_c.r != _r) or (_c.g != _g) or (_c.b != _b)):
                    # print "color differs"
                    continue
                if abs(_ts.getSize() - _tdata['size']) > 1e-10:
                    # print "size differs"
                    continue
                if abs(_ts.getAngle() - _tdata['angle']) > 1e-10:
                    # print "angle differs"
                    continue
                if _ts.getAlignment() != _tdata['align']:
                    # print "alignment differs"
                    continue
                _textstyle = _ts
                break
        if _textstyle is None and _tdata is not None: # make one
            # print "Creating new TextStyle instance"
            _r, _g, _b = _tdata['color']
            _color = self.__getImageColor(_r, _g, _b)
            _textstyle = text.TextStyle(_tdata['name'],
                                        family=_tdata['family'],
                                        style=_tdata['style'],
                                        weight=_tdata['weight'],
                                        color=_color,
                                        size=_tdata['size'],
                                        angle=_tdata['angle'],
                                        align=_tdata['align'])
        return _textstyle

    def __makeDimStyle(self, values):
        # print "LayerLog::__makeDimStyle() ..."
        _image = self.getObject().getParent()
        _dsdata = values.get('dimstyle')
        _dimstyle = None
        if _image is not None and _dsdata is not None:
            # print "restoring dimstylstyle: " + str(_tdata)
            _name = _dsdata['name']
            _dscopy = {}
            for _key in _dsdata.keys():
                if _key != 'name':
                    _dscopy[_key] = _dsdata[_key]
            for _ds in _image.getImageEntities('dimstyle'):
                if _ds.getName() != _name:
                    continue
                _keys = _ds.getKeys()
                _seen = True
                for _key in _keys:
                    if _key not in _dscopy:
                        _seen = False
                        break
                if not _seen:
                    continue
                for _key in _dscopy:
                    if _key not in _keys:
                        _seen = False
                        break
                if not _seen:
                    continue
                _hit = True
                for _key, _val in _dscopy.items():
                    _dsv = _ds.getValue(_key)
                    if ((_key == 'DIM_COLOR') or
                        (_key == 'DIM_PRIMARY_FONT_COLOR') or
                        (_key == 'DIM_SECONDARY_FONT_COLOR')):
                        if _dsv.getColors() != _val:
                            _hit = False
                            break
                    else:
                        if _dsv != _val:
                            _hit = False
                            break
                if not _hit:
                    continue
                # print "hit on existing DimStyle ..."
                _dimstyle = _ds
                break
        if _dimstyle is None and _dsdata is not None: # make one
            # print "making new DimStyle ..."
            _name = _dsdata['name']
            _vals = {}
            for _key in _dsdata.keys():
                if _key != 'name':
                    _val = _dsdata[_key]
                    if ((_key == 'DIM_COLOR') or
                        (_key == 'DIM_PRIMARY_FONT_COLOR') or
                        (_key == 'DIM_SECONDARY_FONT_COLOR')):
                        _r, _g, _b = _val
                        _color = self.__getImageColor(_r, _g, _b)
                        _vals[_key] = _color
                    else:
                        _vals[_key] = _val
            _dimstyle = dimension.DimStyle(_name, _vals)
        return _dimstyle
        
    def __makeDimString(self, values):
        # print "LayerLog::__makeDimString() ..."
        _textstyle = self.__makeTextStyle(values)
        _id = values.get('id')
        if _id is None:
            raise ValueError, "Lost 'id' for recreating DimString"
        _val = values.get('location')
        if _val is None:
            raise ValueError, "Lost 'location' value for DimString"
        _x, _y = _val
        _ds = dimension.DimString(_x, _y, textstyle=_textstyle, id=_id)
        #
        # TextBlock info
        #
        _val = values.get('family')
        if _val is not None:
            _ds.setFamily(_val)
        _val = values.get('style')
        if _val is not None:
            _ds.setStyle(_val)
        _val = values.get('weight')
        if _val is not None:
            _ds.setWeight(_val)
        _val = values.get('color')
        if _val is not None:
            _r, _g, _b = _val
            _ds.setColor(self.__getImageColor(_r, _g, _b))
        _val = values.get('size')
        if _val is not None:
            _ds.setSize(_val)
        _val = values.get('angle')
        if _val is not None:
            _ds.setAngle(_val)
        _val = values.get('alignment')
        if _val is not None:
            _ds.setAlignment(_val)
        #
        # DimString info
        #
        _val = values.get('prefix')
        if _val is None:
            raise ValueError, "Lost 'prefix' value for DimString"
        _ds.setPrefix(_val)
        _val = values.get('suffix')
        if _val is None:
            raise ValueError, "Lost 'suffix' value for DimString"
        _ds.setSuffix(_val)
        _val = values.get('units')
        if _val is None:
            raise ValueError, "Lost 'units' value for DimString"
        if _val == 'millimeters':
            _unit = units.MILLIMETERS
        elif _val == 'micrometers':
            _unit = units.MICROMETERS
        elif _val == 'meters':
            _unit = units.METERS
        elif _val == 'kilometers':
            _unit = units.KILOMETERS
        elif _val == 'inches':
            _unit = units.INCHES
        elif _val == 'feet':
            _unit = units.FEET
        elif _val == 'yards':
            _unit = units.YARDS
        elif _val == 'miles':
            _unit = units.MILES
        else:
            raise ValueError, "Unexpected unit: %s" % _val
        _ds.setUnits(_unit)
        _val = values.get('precision')
        if _val is None:
            raise ValueError, "Lost 'precision' value for DimString"
        _ds.setPrecision(_val)
        _val = values.get('print_zero')
        if _val is None:
            raise ValueError, "Lost 'print_zero' value for DimString"
        _ds.setPrintZero(_val)
        _val = values.get('print_decimal')
        if _val is None:
            raise ValueError, "Lost 'print_decimal' value for DimString"
        _ds.setPrintDecimal(_val)
        return _ds

    def __adjustDimension(self, obj, values):
        # print "LayerLog::__adjustDimension() ..."
        _val = values.get('offset')
        if _val is not None:
            obj.setOffset(_val)
        _val = values.get('extension')
        if _val is not None:
            obj.setExtension(_val)
        _val = values.get('position')
        if _val is not None:
            obj.setPosition(_val)
        _val = values.get('eptype')
        if _val is not None:
            obj.setEndpointType(_val)
        _val = values.get('epsize')
        if _val is not None:
            obj.setEndpointSize(_val)
        _val = values.get('color')
        if _val is not None:
            _r, _g, _b = _val
            obj.setColor(self.__getImageColor(_r, _g, _b))
        _val = values.get('dualmode')
        if _val is not None:
            obj.setDualDimMode(_val)
        _val = values.get('poffset')
        if _val is not None:
            obj.setPositionOffset(_val)
        _val = values.get('dmoffset')
        if _val is not None:
            obj.setDualModeOffset(_val)
        _val = values.get('thickness')
        if _val is not None:
            obj.setThickness(_val)
        
    def __makeObject(self, values):
        # print "LayerLog::__makeObject() ..."
        _type = values.get('type')
        if _type is None:
            _keys = values.keys()
            _keys.sort()
            for _key in _keys:
                print "key: %s: value: %s" % (_key, str(values.get(_key)))
            raise RuntimeError, "No type defined for these values"
        _id = values.get('id')
        if _id is None:
            raise ValueError, "Lost 'id' for recreating object"
        _l = self.getObject()
        _obj = None
        #
        if _type == 'point':
            _x = values.get('x')
            if _x is None:
                raise ValueError, "Lost 'x' value for Point"
            _y = values.get('y')
            if _y is None:
                raise ValueError, "Lost 'y' value for Point"
            _obj = point.Point(_x, _y, id=_id)
        elif _type == 'segment':
            _p1id = values.get('p1')
            if _p1id is None:
                raise ValueError, "Lost 'p1' value for Segment"
            _p1 = _l.getObject(_p1id)
            if _p1 is None or not isinstance(_p1, point.Point):
                raise ValueError, "Segment P1 point missing; id=%d" % _p1id
            _p2id = values.get('p2')
            if _p2id is None:
                raise ValueError, "Lost 'p2' value for Segment"
            _p2 = _l.getObject(_p2id)
            if _p2 is None or not isinstance(_p2, point.Point):
                raise ValueError, "Segment P2 point missing; id=%d" % _p2id
            _obj = segment.Segment(_p1, _p2, id=_id)
            self.__resetGraphicValues(_obj, values)
        elif _type == 'circle':
            _cid = values.get('center')
            if _cid is None:
                raise ValueError, "Lost 'center' value for Circle"
            _cp = _l.getObject(_cid)
            if _cp is None or not isinstance(_cp, point.Point):
                raise ValueError, "Circle center missing: id=%d" % _cid
            _r = values.get('radius')
            if _r is None:
                raise ValueError, "Lost 'radius' value for Circle"
            _obj = circle.Circle(_cp, _r, id=_id)
            self.__resetGraphicValues(_obj, values)
        elif _type == 'arc':
            _cid = values.get('center')
            if _cid is None:
                raise ValueError, "Lost 'center' value for Arc."
            _cp = _l.getObject(_cid)
            if _cp is None or not isinstance(_cp, point.Point):
                raise ValueError, "Arc center missing: id=%d" % _cid
            _r = values.get('radius')
            if _r is None:
                raise ValueError, "Lost 'radius' value for Arc."
            _sa = values.get('start_angle')
            if _sa is None:
                raise ValueError, "Lost 'start_angle' value for Arc."
            _ea = values.get('end_angle')
            if _ea is None:
                raise ValueError, "Lost 'end_angle' value for Arc."
            _obj = arc.Arc(_cp, _r, _sa, _ea, id=_id)
            self.__resetGraphicValues(_obj, values)
        elif _type == 'ellipse':
            raise TypeError, "Ellipse not yet handled ..."
        elif _type == 'leader':
            _p1id = values.get('p1')
            if _p1id is None:
                raise ValueError, "Lost 'p1' value for Leader."
            _p1 = _l.getObject(_p1id)
            if _p1 is None or not isinstance(_p1, point.Point):
                raise ValueError, "Leader P1 point missing: id=%d" % _p1id
            _p2id = values.get('p2')
            if _p2id is None:
                raise ValueError, "Lost 'p2' value for Leader."
            _p2 = _l.getObject(_p2id)
            if _p2 is None or not isinstance(_p2, point.Point):
                raise ValueError, "Leader P2 point missing: id=%d" % _p2id
            _p3id = values.get('p3')
            if _p3id is None:
                raise ValueError, "Lost 'p3' value for Leader."
            _p3 = _l.getObject(_p3id)
            if _p3 is None or not isinstance(_p3, point.Point):
                raise ValueError, "Leader P3 point missing: id=%d" % _p3id
            _size = values.get('size')
            if _size is None:
                raise ValueError, "Lost 'size' value for Leader."
            _obj = leader.Leader(_p1, _p2, _p3, _size, id=_id)
            self.__resetGraphicValues(_obj, values)
        elif _type == 'polyline':
            _pids = values.get('points')
            _pts = []
            for _ptid in _pids:
                _p = _l.getObject(_ptid)
                if _p is None or not isinstance(_p, point.Point):
                    raise ValueError, "Polyline point missing: id=%d" % _ptid
                _pts.append(_p)
            _obj = polyline.Polyline(_pts, id=_id)
            self.__resetGraphicValues(_obj, values)
        elif _type == 'textblock':
            _loc = values.get('location')
            if _loc is None:
                raise ValueError, "Lost 'location' value for TextBlock."
            _x, _y = _loc
            _text = values.get('text')
            if _text is None:
                raise ValueError, "Lost 'text' value for TextBlock."
            _tstyle = self.__makeTextStyle(values)
            _obj = text.TextBlock(_x, _y, _text, textstyle=_tstyle, id=_id)
            _val = values.get('family')
            if _val is not None:
                _obj.setFamily(_val)
            _val = values.get('style')
            if _val is not None:
                _obj.setStyle(_val)
            _val = values.get('weight')
            if _val is not None:
                _obj.setWeight(_val)
            _val = values.get('color')
            if _val is not None:
                _r, _g, _b = _val
                _obj.setColor(self.__getImageColor(_r, _g, _b))
            _val = values.get('size')
            if _val is not None:
                _obj.setSize(_val)
            _val = values.get('angle')
            if _val is not None:
                _obj.setAngle(_val)
            _val = values.get('alignment')
            if _val is not None:
                _obj.setAlignment(_val)
        elif _type == 'hcline':
            _kid = values.get('keypoint')
            if _kid is None:
                raise ValueError, "Lost 'keypoint' value for HCLine."
            _p = _l.getObject(_kid)
            if _p is None or not isinstance(_p, point.Point):
                raise ValueError, "HCLine point missing: id=%d" % _kid
            _obj = hcline.HCLine(_p, id=_id)
        elif _type == 'vcline':
            _kid = values.get('keypoint')
            if _kid is None:
                raise ValueError, "Lost 'keypoint' value for VCLine."
            _p = _l.getObject(_kid)
            if _p is None or not isinstance(_p, point.Point):
                raise ValueError, "VCLine point missing: id=%d" % _kid
            _obj = vcline.VCLine(_p, id=_id)
        elif _type == 'acline':
            _kid = values.get('keypoint')
            if _kid is None:
                raise ValueError, "Lost 'keypoint' value for ACLine."
            _p = _l.getObject(_kid)
            if _p is None or not isinstance(_p, point.Point):
                raise ValueError, "ACLine point missing: id=%d" % _kid
            _angle = values.get('angle')
            if _angle is None:
                raise ValueError, "Lost 'angle' value for ACLine."
            _obj = acline.ACLine(_p, _angle, id=_id)
        elif _type == 'cline':
            _p1id = values.get('p1')
            if _p1id is None:
                raise ValueError, "Lost 'p1' value for CLine"
            _p1 = _l.getObject(_p1id)
            if _p1 is None or not isinstance(_p1, point.Point):
                raise ValueError, "CLine P1 point missing: id=%d" % _p1id
            _p2id = values.get('p2')
            if _p2id is None:
                raise ValueError, "Lost 'p2' value for CLine"
            _p2 = _l.getObject(_p2id)
            if _p2 is None or not isinstance(_p2, point.Point):
                raise ValueError, "CLine P2 point missing: id=%d" % _p2id
            _obj = cline.CLine(_p1, _p2, id=_id)
        elif _type == 'ccircle':
            _cid = values.get('center')
            if _cid is None:
                raise ValueError, "Lost 'center' value for CCircle"
            _cp = _l.getObject(_cid)
            if _cp is None or not isinstance(_cp, point.Point):
                raise ValueError, "CCircle center missing: id=%d" % _cid
            _r = values.get('radius')
            if _r is None:
                raise ValueError, "Lost 'radius' value for CCircle"
            _obj = ccircle.CCircle(_cp, _r, id=_id)
        elif _type == 'fillet':
            _s1id = values.get('s1')
            if _s1id is None:
                raise ValueError, "Lost 's1' value for Fillet"
            _s1 = _l.getObject(_s1id)
            if _s1 is None or not isinstance(_s1, segment.Segment):
                raise ValueError, "Fillet S1 segment missing: id=%d" % _s1id
            _s2id = values.get('s2')
            if _s2id is None:
                raise ValueError, "Lost 's2' value for Fillet"
            _s2 = _l.getObject(_s2id)
            if _s2 is None or not isinstance(_s2, segment.Segment):
                raise ValueError, "Fillet S2 segment missing: id=%d" % _s2id
            _r = values.get('radius')
            if _r is None:
                raise ValueError, "Lost 'radius' value for Fillet"
            _obj = segjoint.Fillet(_s1, _s2, _r, id=_id)
        elif _type == 'chamfer':
            _s1id = values.get('s1')
            if _s1id is None:
                raise ValueError, "Lost 's1' value for Chamfer"
            _s1 = _l.getObject(_s1id)
            if _s1 is None or not isinstance(_s1, segment.Segment):
                raise ValueError, "Fillet S1 segment missing: id=%d" % _s1id
            _s2id = values.get('s2')
            if _s2id is None:
                raise ValueError, "Lost 's2' value for Chamfer"
            _s2 = _l.getObject(_s2id)
            if _s2 is None or not isinstance(_s2, segment.Segment):
                raise ValueError, "Fillet S2 segment missing: id=%d" % _s2id
            _len = values.get('length')
            if _len is None:
                raise ValueError, "Lost 'length' value for Chamfer"
            _obj = segjoint.Chamfer(_s1, _s2, _len, id=_id)
        elif _type == 'ldim' or _type == 'hdim' or _type == 'vdim':
            _loc = values.get('location')
            if _loc is None:
                raise ValueError, "Lost 'location' value for L/H/V Dimension."
            _x, _y = _loc
            _l1id = values.get('l1')
            if _l1id is None:
                raise ValueError, "Lost 'l1' value for L/H/V Dimension."
            _p1id = values.get('p1')
            if _p1id is None:
                raise ValueError, "Lost 'p1' value for L/H/V Dimension."
            _l2id = values.get('l2')
            if _l2id is None:
                raise ValueError, "Lost 'l2' value for L/H/V Dimension."
            _p2id = values.get('p2')
            if _p2id is None:
                raise ValueError, "Lost 'p2' value for L/H/V Dimension."
            _l1 = _p1 = _l2 = _p2 = None
            _lid = _l.getID()
            _img = _l.getParent()
            if _img is None:
                raise ValueError, "Layer has no parent Image"
            if _l1id == _lid:
                _l1 = _l
            else:
                _l1 = _img.getObject(_l1id)
                if _l1 is None or not isinstance(_l1, Layer):
                    raise ValueError, "Dimension L1 layer missing: id=%d" % _l1id
            _p1 = _l1.getObject(_p1id)
            if _p1 is None or not isinstance(_p1, point.Point):
                raise ValueError, "Dimension P1 point missing: id=%d" % _p1id
            if _l2id == _lid:
                _l2 = _l
            else:
                _l2 = _img.getObject(_l2id)
                if _l2 is None or not isinstance(_l2, Layer):
                    raise ValueError, "Dimension L2 layer missing: id=%d" % _l2id
            _p2 = _l2.getObject(_p2id)
            if _p2 is None or not isinstance(_p2, point.Point):
                raise ValueError, "Dimension P2 point missing: id=%d" % _p2id
            _ds = self.__makeDimStyle(values)
            _dsdata = values.get('ds1')
            if _dsdata is None:
                raise ValueError, "Lost 'ds1' value for L/H/V Dimension."
            _ds1 = self.__makeDimString(_dsdata)
            _dsdata = values.get('ds2')
            if _dsdata is None:
                raise ValueError, "Lost 'ds2' value for L/H/V Dimension."
            _ds2 = self.__makeDimString(_dsdata)
            if _ds is None:
                _ds = _img.getOption('DIM_STYLE')
            if _type == 'ldim':
                _objtype = dimension.LinearDimension
            elif _type == 'hdim':
                _objtype = dimension.HorizontalDimension
            elif _type == 'vdim':
                _objtype = dimension.VerticalDimension
            else:
                raise ValueError, "Unexpected type: %s" % _type
            _obj = _objtype(_p1, _p2, _x, _y, _ds, ds1=_ds1, ds2=_ds2, id=_id)
            self.__adjustDimension(_obj, values)
        elif _type == 'rdim':
            _loc = values.get('location')
            if _loc is None:
                raise ValueError, "Lost 'location' value for RadialDimension."
            _x, _y = _loc
            _lid = values.get('layer')
            if _lid is None:
                raise ValueError, "Lost 'layer' value for RadialDimension."
            _cid = values.get('circle')
            if _cid is None:
                raise ValueError, "Lost 'circle' value for RadialDimension."
            _cl = _c = None
            _img = _l.getParent()
            if _img is None:
                raise ValueError, "Layer has no parent Image"
            if _lid == _l.getID():
                _cl = _l
            else:
                _cl = _img.getObject(_lid)
                if _cl is None or not isinstance(_cl, Layer):
                    raise ValueError, "Dimension Layer missing: id=%d" % _lid
            _c = _cl.getObject(_cid)
            if _c is None or not isinstance(_c, (circle.Circle, arc.Arc)):
                raise ValueError, "Dimension Circle/Arc missing: id=%d" % _cid
            _ds = self.__makeDimStyle(values)
            _dsdata = values.get('ds1')
            if _dsdata is None:
                raise ValueError, "Lost 'ds1' value for RadialDimension."
            _ds1 = self.__makeDimString(_dsdata)
            _dsdata = values.get('ds2')
            if _dsdata is None:
                raise ValueError, "Lost 'ds2' value for RadialDimension."
            _ds2 = self.__makeDimString(values.get('ds2'))
            _obj = dimension.RadialDimension(_c, _x, _y, _ds,
                                             ds1=_ds1, ds2=_ds2, id=_id)
            self.__adjustDimension(_obj, values)
            _mode = values.get('dia_mode')
            if _mode is None:
                raise ValueError, "Lost 'dia_mode' value for RadialDimension."
            _obj.setDiaMode(_mode)
        elif _type == 'adim':
            _x, _y = values.get('location')
            _vlid = values.get('vl')
            if _vlid is None:
                raise ValueError, "Lost 'vl' value for AngularDimension."
            _vpid = values.get('vp')
            if _vpid is None:
                raise ValueError, "Lost 'vp' value for AngularDimension."
            _l1id = values.get('l1')
            if _l1id is None:
                raise ValueError, "Lost 'l1' value for AngularDimension."
            _p1id = values.get('p1')
            if _p1id is None:
                raise ValueError, "Lost 'p1' value for AngularDimension."
            _l2id = values.get('l2')
            if _l2id is None:
                raise ValueError, "Lost 'l2' value for AngularDimension."
            _p2id = values.get('p2')
            if _p2id is None:
                raise ValueError, "Lost 'p2' value for AngularDimension."
            _vl = _vp = _l1 = _p1 = _l2 = _p2 = None
            _lid = _l.getID()
            _img = _l.getParent()
            if _img is None:
                raise ValueError, "Layer has no parent Image"
            if _vlid == _lid:
                _vl = _l
            else:
                _vl = _img.getObject(_vlid)
                if _vl is None or not isinstance(_vl, Layer):
                    raise ValueError, "Dimension vertex layer missing: id=%d" % _vlid
            _vp = _vl.getObject(_vpid)
            if _vp is None or not isinstance(_vp, point.Point):
                raise ValueError, "Dimension vertex point missing: id=%d" % _vpid
            if _l1id == _lid:
                _l1 = _l
            else:
                _l1 = _img.getObject(_l1id)
                if _l1 is None or not isinstance(_l1, Layer):
                    raise ValueError, "Dimension L1 layer missing: id=%d" % _l1id
            _p1 = _l1.getObject(_p1id)
            if _p1 is None or not isinstance(_p1, point.Point):
                raise ValueError, "Dimension P1 point missing: id=%d" % _p1id
            if _l2id == _lid:
                _l2 = _l
            else:
                _l2 = _img.getObject(_l2id)
                if _l2 is None or not isinstance(_l2, Layer):
                    raise ValueError, "Dimension L2 layer missing: id=%d" % _l2id
            _p2 = _l2.getObject(_p2id)
            if _p2 is None or not isinstance(_p2, point.Point):
                raise ValueError, "Dimension P2 point missing: id=%d" % _p2id
            _ds = self.__makeDimStyle(values)
            _dsdata = values.get('ds1')
            if _dsdata is None:
                raise ValueError, "Lost 'ds1' value for AngularDimension."
            _ds1 = self.__makeDimString(_dsdata)
            _dsdata = values.get('ds2')
            if _dsdata is None:
                raise ValueError, "Lost 'ds2' value for AngularDimension."
            _ds2 = self.__makeDimString(values.get('ds2'))
            _obj = dimension.AngularDimension(_vp, _p1, _p2, _x, _y, _ds,
                                              ds1=_ds1, ds2=_ds2, id=_id)
            self.__adjustDimension(_obj, values)
        else:
            raise TypeError, "Unexpected type: %s"  % _type
        return _obj

    def __delObject(self, undo, values):
        # print "LayerLog::__delObject() ..."
        _type = values.get('type')
        _id = values.get('id')
        # print "id: %d" % _id
        _l = self.getObject()
        _obj = _l.getObject(_id)
        if _obj is None:
            raise ValueError, "Missed object: %d, %s" % (_id, _type)
        #
        # layer still has to send messages out like 'removed_child'
        #
        if undo:
            _l.startUndo()
            try:
                _l.delObject(_obj)
            finally:
                _l.endUndo()
        else:
            _l.startRedo()
            try:
                _l.delObject(_obj)
            finally:
                _l.endRedo()
