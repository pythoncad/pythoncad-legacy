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
# This module provide class to manage geometrical vector and points operation
#

import math

class Point:
    """
        Provide a Full 2d point operation and definition
    """
    def __init__(self,x,y,t=None):
        """
            Default Constructor
        """
        self.X=float(x)
        self.Y=float(y)
        if(t==None): self.T=0.00001
        else: self.T=t
    def Coord(self):
        """
          Get The Point Coordinate
        """
        return self.X,self.Y
    def __eq__(self,point):
        """
          The 2 point are equal
        """
        if(not isinstance(point,Point)):
          raise TypeError,"Invalid Argument point: Point Required"
        x,y=self.GetCoord()
        x1,y1=point.GetCoord()
        deltaX=abs(x-x1)
        deltaY=abs(y-y1)
        if(deltaX<=t and deltaY<=t):
          return True
        else:
          return False
    def Mag(self,point):
        """
            Get Distantce p1-p2
        """
        if(not isinstance(point,Point)):
          raise TypeError,"Invalid Argument point: Point Required"
        x,y=point.Coord()
        xDelta=abs(self.X-x)
        yDelta=abs(self.Y-y)
        d=math.sqrt(pow(xDelta,2)+pow(yDelta,2))
        return d

class Vector:
    """
        Provide a full 2d vector operation and definition
    """
    def __init__(self,p1,p2):
        """
            Default Constructor
        """
        if(not isinstance(p1,Point)):
          raise TypeError,"Invalid Argument p1: Point Required"
        if(not isinstance(p2,Point)):
          raise TypeError,"Invalid Argument p2: Point Required"
        x,y=p1.Coord()
        x1,y1=p2.Coord()
        self.X=x1-x
        self.Y=y1-y
    def Mag(self):
        """
            Get the versor
        """
        if(self.X==0 or self.Y==0):
            if(self.X==0):
                x=0
                if(self.Y>0):
                    y=1
                else:
                    y=-1
            else:
                y=0
                if(self.X>0):
                    x=1
                else:
                    x=-1
        else:
          module=self.Norm()
          y=self.Y/module
          x=self.X/module
        p1=Point(0,0)
        p2=Point(x,y)
        retVector=Vector(p1,p2)
        return retVector
    def Norm(self):
        """
          Get The Norm Of the vector
        """
        return math.sqrt(pow(self.X,2)+pow(self.Y,2))
    def __eq__(self,vector):
        """
            the 2 vecror are equal
        """ 
        if(not isinstance(vector,Vector)):
          raise TypeError,"Invalid Argument vector: Vector Required"   
        if(self.Point()==vector.Point()):
            return True             
        else:
            return False
    def Point(self):
        """
              Return The Point 
        """
        return Point(self.X,self.Y)
    def Dot(self,vector):
        """
            Compute The Dot Product
        """
        if(not isinstance(vector,Vector)):
            raise TypeError,"Invalid Argument vector: Vector Required"  
        v0=self.Point().Coord()
        v1=vector.Point().Coord()
        som=0
        for a, b in zip(v0, v1):
          som+=a*b
        return som  
    def Cross(self,vector):
        """
            Compute The Cross Product
        """
        if(not isinstance(vector,Vector)):
            raise TypeError,"Invalid Argument vector: Vector Required"  
        x1,y1=self.Point().Coord()
        x2,y2=vector.Point().Coord()
        cros=x1*y2 - y1*x2
        return cros
    def Ang(self,vector):
        """
            Calculate the angle Between the two vector
        """
        if(not isinstance(vector,Vector)):
            raise TypeError,"Invalid Argument vector: Vector Required"  
        vself=self.Mag()
        vvector=vector.Mag()
        dot=vself.Dot(vvector)
        if(dot<-1):
            dot=-1
        if(dot>1):
            dot=1
        ang=math.acos(dot)
        return ang
    def Mult(self,scalar):
        """
            Multiplae the vector for a scalar value
        """
        self.X=scalar*self.X
        self.Y=scalar*self.Y
    def Map(self,x,y):
        """
            Get a vector for the mapping point
        """
        p0=Point(0,0)
        pPro=Point(x,y)
        vProj=Vector(p0,pPro)
        ang=self.Ang(vProj)
        vProjNorm=vProj.Norm()
        projectionUnitDistance=vProjNorm*math.cos(ang)
        vSelfMag=self.Mag()
        vSelfMag.Mult(projectionUnitDistance)
        return vSelfMag    

 
