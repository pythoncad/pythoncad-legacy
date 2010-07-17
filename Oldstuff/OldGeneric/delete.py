#
# Copyright (c) 2002, 2003, 2004, 2006 Art Haas
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
# Deleting objects
#

from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.text import TextBlock
from PythonCAD.Generic.dimension import DimString
from PythonCAD.Generic.layer import Layer

def delete_objects(objlist):
    """Remove a list of objects from the parent Layer.

delete_objects(objlist)

The objlist argument must be either a tuple or list.
    """
    if not isinstance(objlist, (list, tuple)):
        raise TypeError, "Invalid object list: " + `type(objlist)`
    _delobjs = []
    for _obj in objlist:
        if not isinstance(_obj, DimString):
            _parent = _obj.getParent()
            if _parent is not None and isinstance(_parent, Layer):
                _delobjs.append(_obj)
    _objdict = {}
    for _obj in _delobjs:
        _objdict[id(_obj)] = True
    for _obj in _delobjs:
        if isinstance(_obj, Point):
            continue
        elif isinstance(_obj, Segment):
            _p1, _p2 = _obj.getEndpoints()
            _pid = id(_p1)
            if _pid in _objdict:
                _objdict[_pid] = False
            _pid = id(_p2)
            if _pid in _objdict:
                _objdict[_pid] = False
        elif isinstance(_obj, Arc):
            _cp = _obj.getCenter()
            _pid = id(_cp)
            if _pid in _objdict:
                _objdict[_pid] = False
            _parent = _obj.getParent()
            for _ep in _obj.getEndpoints():
                _lp = None
                _pts = _parent.find('point', _ep[0], _ep[1])
                for _pt in _pts:
                    for _user in _pt.getUsers():
                        if _user is _obj:
                            _lp = _pt
                            break
                if _lp is None:
                    raise RuntimeError, "Arc endpoint missing: " + str(_ep)
                _pid = id(_lp)
                if _pid in _objdict:
                    _objdict[_pid] = False
        elif isinstance(_obj, (Circle, CCircle)):
            _cp = _obj.getCenter()
            _pid = id(_cp)
            if _pid in _objdict:
                _objdict[_pid] = False
        elif isinstance(_obj, (HCLine, VCLine, ACLine)):
            _lp = _obj.getLocation()
            _pid = id(_lp)
            if _pid in _objdict:
                _objdict[_pid] = False
        elif isinstance(_obj, CLine):
            _p1, _p2 = _obj.getKeypoints()
            _pid = id(_p1)
            if _pid in _objdict:
                _objdict[_pid] = False
            _pid = id(_p2)
            if _pid in _objdict:
                _objdict[_pid] = False
        elif isinstance(_obj, (Chamfer, Fillet)):
            continue # chamfers/fillets do not delete attached segments
        elif isinstance(_obj, (Leader, Polyline)):
            for _pt in _obj.getPoints():
                _pid = id(_pt)
                if _pid in _objdict:
                    _objdict[_pid] = False
        elif isinstance(_obj, TextBlock):
            continue
        else:
            pass
    for _obj in _delobjs:
        if _objdict[id(_obj)]:
            _parent = _obj.getParent()
            #
            # if the parent is None then the object has already been
            # deleted as a result of earlier deletions such as a
            # dimension being removed when the referenced points were
            # removed
            #
            if _parent is not None:
                _parent.delObject(_obj)
