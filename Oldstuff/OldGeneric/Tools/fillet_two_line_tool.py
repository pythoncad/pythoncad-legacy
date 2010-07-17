#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
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
# tool stuff
#

import math
import types
import array

from PythonCAD.Generic import util
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.leader import Leader
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.hcline import HCLine
from PythonCAD.Generic.vcline import VCLine
from PythonCAD.Generic.acline import ACLine
from PythonCAD.Generic.cline import CLine
from PythonCAD.Generic.ccircle import CCircle
from PythonCAD.Generic.text import TextStyle, TextBlock
from PythonCAD.Generic import dimension
from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic import tangent
from PythonCAD.Generic import intersections 
from PythonCAD.Generic.segjoint import Chamfer, Fillet
from PythonCAD.Generic import pyGeoLib 
from PythonCAD.Generic.snap import SnapPointStr

from PythonCAD.Generic import error
from PythonCAD.Generic.Tools.fillet_tool import FilletTool


class FilletTwoLineTool(FilletTool):
    """
        A specifie tool for drawing fillet using two segment
    """
    def __init__(self):
        super(FilletTwoLineTool, self).__init__()
        self.__FirstLine=None
        self.__SecondLine=None
        self.__SecondPoint=None
        self.__FirstPoint=None
        self.__TrimMode='b'
    def GetFirstLine(self):
        return self.__FirstLine
    def SetFirstLine(self,obj):
        if obj==None:
            raise "None Object"        
        if not isinstance(obj,Segment):
            raise "Invalid object Need Segment or CLine"
        self.__FirstLine=obj
    def GetSecondLine(self):
        return self.__SecondLine
    def SetSecondtLine(self,obj):
        if obj==None:
            raise "None Object"
        if not isinstance(obj,Segment):
            raise "Invalid object Need Segment or CLine"
        self.__SecondLine=obj            
    FirstLine=property(GetFirstLine,SetFirstLine,None,"Set first line object in the tool")
    SecondLine=property(GetSecondLine,SetSecondtLine,None,"Set second line object in the tool")
    def GetFirstPoint(self):
        """
            Return the first toolpoint
        """
        return self.__FirstPoint
    def SetFirstPoint(self,point):
        """
            Set the first toolpoint
        """
        if point==None:
            raise "None Object"
        if not isinstance(point,Point):
            raise "Invalid object Need Point"
        self.__FirstPoint=point
    def GetSecondPoint(self):
        """
            Return the second toolpoint
        """
        return self.__SecondPoint
    def SetSecondPoint(self,point):
        """
            Set the second toolpoint
        """
        if point==None:
            raise "None Object"
        if not isinstance(point,Point):
            raise "Invalid object Need Point"
        self.__SecondPoint=point
    FirstPoint=property(GetFirstPoint,SetFirstPoint,None,"First line object in the tool")
    SecondPoint=property(GetSecondPoint,SetSecondPoint,None,"Second line object in the tool")
    def SetTrimMode(self,mode):
        """
            set the trim mode
        """
        self.__TrimMode=mode
    def GetTrimMode(self):
        """
            get the trim mode
        """
        return self.__TrimMode
    TrimMode=property(GetTrimMode,SetTrimMode,None,"Trim Mode")
    
    def Create(self,image):
        """
            Create the Fillet
        """
        interPnt=[]
        if self.FirstLine != None and self.SecondLine != None :
            intersections._seg_seg_intersection(interPnt,self.__FirstLine,self.__SecondLine)
        else:
            if self.FirstLine==None:
                raise "tools.fillet.Create: First  obj is null"
            if self.SecondLine==None:
                raise "tools.fillet.Create: Second  obj is null"
        if(len(interPnt)):
            _active_layer = image.getActiveLayer() 
            _s = image.getOption('LINE_STYLE')
            _l = image.getOption('LINE_TYPE')
            _c = image.getOption('LINE_COLOR')
            _t = image.getOption('LINE_THICKNESS')
            p1,p2=self.FirstLine.getEndpoints() 
            p11,p12=self.SecondLine.getEndpoints()  
            p1=Point(p1.getCoords())           
            p2=Point(p2.getCoords())
            p11=Point(p11.getCoords())           
            p12=Point(p12.getCoords())          
            #
            interPoint1=Point(interPnt[0]) 
            _active_layer.addObject(interPoint1)    
            interPoint2=Point(interPnt[0]) 
            _active_layer.addObject(interPoint2)  
            # 
            # new function for calculating the new 2 points
            #
            self.setRightPoint(image,self.FirstLine,self.FirstPoint,interPoint1)                   
            self.setRightPoint(image,self.SecondLine,self.SecondPoint,interPoint2)
            _fillet=Fillet(self.FirstLine, self.SecondLine,self.rad, _s)
            if _l != _s.getLinetype():
                _fillet.setLinetype(_l)
            if _c != _s.getColor():
                _fillet.setColor(_c)
            if abs(_t - _s.getThickness()) > 1e-10:
                _fillet.setThickness(_t)             
            _active_layer.addObject(_fillet)    
            #
            # Adjust the lines
            #
            if self.TrimMode=='f' or self.TrimMode=='n': 
                image.delObject(self.SecondLine.p1)
                image.delObject(self.SecondLine.p2)               
                self.SecondLine.p1=p11
                self.SecondLine.p2=p12
                _active_layer.addObject(p11)
                _active_layer.addObject(p12)
            if self.TrimMode=='s' or self.TrimMode=='n':
                image.delObject(self.FirstLine.p1)
                image.delObject(self.FirstLine.p2)               
                self.FirstLine.p1=p1
                self.FirstLine.p2=p2       
                _active_layer.addObject(p1)
                _active_layer.addObject(p2)         
            
    def setRightPoint(self,image,objSegment,objPoint,objInterPoint):
        """
            Get the point used for the trim
        """
        _p1 , _p2 = objSegment.getEndpoints()       
        _x,_y = objPoint.getCoords()
        _objPoint=Point(objSegment.getProjection(_x,_y))
        if not (_p1==objInterPoint or _p2==objInterPoint):
            pickIntVect=pyGeoLib.Vector(objInterPoint,_objPoint).Mag()                    
            p1IntVect=pyGeoLib.Vector(objInterPoint,_p1).Mag()            
            if(pickIntVect==p1IntVect):
                objSegment.p2=objInterPoint
                image.delObject(_p2)
                return
            p2IntVect=pyGeoLib.Vector(objInterPoint,_p2).Mag()
            if(pickIntVect==p2IntVect):
                objSegment.p1=objInterPoint
                image.delObject(_p1)
                return
        ldist=_objPoint.Dist(_p1)
        if ldist>_objPoint.Dist(_p2):
            objSegment.p2=objInterPoint
            image.delObject(_p2)
        else:
            objSegment.p1=objInterPoint
            image.delObject(_p1)
    

            