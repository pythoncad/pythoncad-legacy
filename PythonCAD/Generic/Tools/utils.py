#
# Copyright (c) 2003 Art Haas
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
# This code handles interpreting entries in the gtkimage.entry box
# and calling the apprpriate internal command
#
# Author: David Broadwell ( dbroadwell@mindspring.com, 05/26/2003 )
#



# Usefull function
def getSegmentSnap(firstPoint,secondPoint):
    """
        Get a quadruple of coords that define the line taking care of 
        the user snaps
    """
    _singlePoint=['Freepoint','End','Intersection','Point','Origin','Mid','Center']
    _computePoint=['Perpendicular','Tangent']
    _x1,_y1=firstPoint.point.getCoords()
    _x2,_y2=secondPoint.point.getCoords()
    _firstKind=firstPoint.kind
    _secondKind=secondPoint.kind
    if _firstKind in _singlePoint and _secondKind in _computePoint :
        if _secondKind =="Perpendicular":
            if isinstance(secondPoint.entity,(Segment,CLine,ACLine,HCLine,VCLine)):
                pjPoint=Point(secondPoint.entity.getProjection(_x1,_y1))
                if pjPoint is not None:
                    _x2,_y2=pjPoint.getCoords()
        if _secondKind =="Tangent":
            if isinstance(secondPoint.entity,(Circle,Arc,CCircle)):
                x2,y2=secondPoint.entity.GetTangentPoint(_x2,_y2,_x1,_y1)
                if(x2,y2 is not None,None):       
                    _x2,_y2=x2,y2
    if _firstKind in _computePoint and _secondKind in _singlePoint :
        if _firstKind =="Perpendicular":
            if isinstance(firstPoint.entity,(Segment,CLine,ACLine,HCLine,VCLine)):
                pjPoint=Point(firstPoint.entity.getProjection(_x2,_y2))
                if pjPoint is not None:
                    _x1,_y1=pjPoint.getCoords()
        if _firstKind =="Tangent":            
            if isinstance(firstPoint.entity,(Circle,Arc,CCircle)):
                x1,y1=firstPoint.entity.GetTangentPoint(_x1,_y1,_x2,_y2)
                if(x1,y1 is not None,None):       
                    _x1,_y1=x1,y1
    if _firstKind in _computePoint and _secondKind in _computePoint:
        if _firstKind =="Tangent" and _secondKind =="Tangent":
            if (isinstance(firstPoint.entity,(Circle,Arc,CCircle)) and 
                isinstance(secondPoint.entity,(Circle,Arc,CCircle))):
                _x1,_y1,_x2,_y2=tanTanSegment(firstPoint,secondPoint)         
    return _x1,_y1,_x2,_y2

def tanTanSegment(p1,p2):
    """
        get the coordinates of bi tangent line over two circle ents using strPoint
        return a x,y,x1,x1 coords that define the segment
    """
    if p1 is None:
        raise ValueError, "First construction point not set."    
    if p2 is None :
        raise ValueError, "Second construction point not set."
    #
    # calculate the tangent points if they exist
    #
    _cc1 = p1.entity
    _cc2 = p2.entity
    _cx1, _cy1 = _cc1.getCenter().getCoords()
    _r1 = _cc1.getRadius()
    _cx2, _cy2 = _cc2.getCenter().getCoords()
    _r2 = _cc2.getRadius()
    _sep = math.hypot((_cx2 - _cx1), (_cy2 - _cy1))
    _angle = math.atan2((_cy2 - _cy1), (_cx2 - _cx1))
    _sine = math.sin(_angle)
    _cosine = math.cos(_angle)
    #
    # tangent points are calculated as if the first circle
    # center is (0, 0) and both circle centers on the x-axis,
    # so the points need to be transformed to the correct coordinates
    #
    _exitSegment=None
    _tansets = tangent.calc_two_circle_tangents(_r1, _r2, _sep)
    for _set in _tansets:
        _x1, _y1, _x2, _y2 = _set
        _tx1 = ((_x1 * _cosine) - (_y1 * _sine)) + _cx1
        _ty1 = ((_x1 * _sine) + (_y1 * _cosine)) + _cy1
        _tx2 = ((_x2 * _cosine) - (_y2 * _sine)) + _cx1
        _ty2 = ((_x2 * _sine) + (_y2 * _cosine)) + _cy1
        sp1=Point(_tx1, _ty1)
        sp2=Point(_tx2, _ty2)
        if _exitSegment is None:
            _globalDist=abs(p1.point-sp1)+abs(p2.point-sp2)       
            _exitSegment= _tx1, _ty1,_tx2, _ty2
        else:
            if _globalDist>abs(p1.point-sp1)+abs(p2.point-sp2):
                _globalDist=abs(p1.point-sp1)+abs(p2.point-sp2)      
                _exitSegment= _tx1, _ty1,_tx2, _ty2
    return _exitSegment
