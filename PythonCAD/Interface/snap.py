#
# Copyright (c) 2010 Matteo Boscolo
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
# This Module provide a snap management for the drawing scene and icommand
# 
#

from PyQt4 import QtCore, QtGui

from Kernel.initsetting             import SNAP_POINT_ARRAY
from Kernel.GeoEntity.point         import Point
from Kernel.GeoUtil.intersection    import *

from Interface.Entity.base          import BaseEntity

class SnapPoint():
    def __init__(self, scene):
        self.activeSnap=SNAP_POINT_ARRAY["ALL"]
        self.__scene=scene
        
    def getSnapPoint(self,  point, entity):
        """
            Get snapPoints
            Remarks:
            force:      [initsetting.SNAP_POINT_ARRAY element]
            fromPoint:  [Geoent.Pointfloat]
            fromEnt:    [GeoEnt.*]
        """
        
        snapPoint=point
        
        if SNAP_POINT_ARRAY["MID"] == self.activeSnap:
            snapPoint = self.getSnapMiddlePoint(entity)
        elif SNAP_POINT_ARRAY["END"] == self.activeSnap:
            snapPoint =self.getSnapEndPoint(entity, point)
        elif SNAP_POINT_ARRAY["ORTO"] == self.activeSnap:
            snapPoint =self.getSnapOrtoPoint(entity, point)
        elif SNAP_POINT_ARRAY["CENTER"]== self.activeSnap:
            snapPoint =self.getSnapCenterPoint(entity)
        elif SNAP_POINT_ARRAY["QUADRANT"]== self.activeSnap:
            snapPoint =self.getSnapQuadrantPoint(entity, snapPoint)
        elif SNAP_POINT_ARRAY["ORIG"]== self.activeSnap:
            snapPoint=Point(0.0, 0.0)
        elif SNAP_POINT_ARRAY["INTERSECTION"]== self.activeSnap:
            snapPoint=self.getIntersection(entity,snapPoint )
        elif SNAP_POINT_ARRAY["ALL"]== self.activeSnap:
            #this should be used when checklist of snap will be enabled
            snapPoints=[]
            
            pnt=self.getSnapMiddlePoint(entity)
            if pnt!=None:
                snapPoints.append(pnt)
                
            pnt=self.getSnapEndPoint(entity, snapPoint)
            if pnt!=None:
                snapPoints.append(pnt)
                
            pnt=self.getSnapQuadrantPoint(entity, snapPoint)
            if pnt!=None:
                snapPoints.append(pnt)       
                
            pnt=self.getSnapOrtoPoint(entity, snapPoint)
            if pnt!=None:
                snapPoints.append(pnt)
                
            outPoint=(None, None)
            for p in snapPoints:
                if p!=None:
                    distance=p.dist(snapPoint)
                    if outPoint[0]==None:
                        outPoint=(p, distance)
                    else:
                        if outPoint[1]>distance:
                            outPoint=(p, distance)
            else:
                if outPoint[0]!=None:
                    snapPoint=outPoint[0]
        
        if snapPoint==None:
            return point
        return snapPoint
        
    def getSnapOrtoPoint(self, entity, point):
        """
            this fucnticion compute the orto to point snap constraint
        """
        # Now only works for segments and arcs. USES THE getPROJECTION METHOD
        returnVal=None
        if self.__scene.fromPoint==None or entity == None:
            #print "log: getSnapOrtoPoint :frompoint or entity is none "
            return None
            
        if getattr(entity, 'geoItem', None):
            if getattr(entity.geoItem, 'getProjection', None):
                pT=entity.geoItem.getProjection(self.__scene.fromPoint)
                return pT
        else:
            return None
        
    def getSnapTangentPoint(selfself, point):    
        """
            this fucnticion compute the Tangent to point snap constraint
        """
        #TODO: getSnapTangentPoint
        returnVal=None
        #this function have to be implemented as follow
        #   1) get the Tangent point from the previews entity
        #   2) update the previews snap point
        return returnVal
        
    def getSnapMiddlePoint(self, entity):    
        """
            this fucnticion compute midpoint snap constraint to the entity argument
        """
        returnVal=None
        if getattr(entity, 'geoItem', None):
            if getattr(entity.geoItem, 'getMiddlePoint', None):
                returnVal=entity.geoItem.getMiddlePoint()
        return returnVal
    
    def getSnapEndPoint(self, entity, point):
        """
            this fucnticion compute the  snap endpoint 
        """
        if point == None or entity == None:
            print "log: getSnapEndPoint :point or entity is none "
            return None
            
        if getattr(entity, 'geoItem', None):
            if getattr(entity.geoItem, 'getEndpoints', None):
                p1, p2=entity.geoItem.getEndpoints()
                if point.dist(p1)<point.dist(p2):
                    return p1
                else:
                    return p2
        else:
            return None
    
    def getSnapCenterPoint(self, entity):
        """
            this fucnticion compute the  snap from the center of an entity
        """
        print "getSnapCenterPoint", entity
        returnVal=None
        if getattr(entity, 'geoItem', None):
            print "isgeoitem"
            geoEntity=entity.geoItem
            if getattr(geoEntity, 'getCenter', None):
                print "have cente attr"
                returnVal=geoEntity.center
            else:
                returnVal=None
        return returnVal
        
    def getIntersection(self, entity, point): 
        """
            this fucnticion compute the  snap intersection point
        """
        print "intersection"
        returnVal=None
        distance=None
        if entity!=None:
            geoEntityFrom=entity.geoItem
            entityList=self.__scene.collidingItems(entity)
            for ent in entityList:
                if isinstance(ent, BaseEntity):
                    intPoint=find_intersections(ent.geoItem,geoEntityFrom)
                    for tp in intPoint:
                        iPoint=Point(tp[0], tp[1])
                        if distance==None:
                            distance=iPoint.dist(point)
                            returnVal=iPoint
                        else:
                            spoolDist=iPoint.dist(point)
                            if distance>spoolDist:
                                distance=spoolDist
                                returnVal=iPoint
        return returnVal    

    def getSnapQuadrantPoint(self, entity, point):
        """
            this fucnticion compute the  snap from the quadrant 
        """
        returnVal=None
        if getattr(entity, 'geoItem', None):
            geoEntity=entity.geoItem
            if getattr(geoEntity, 'getQuadrant', None):
                dist=None
                for p in geoEntity.getQuadrant():
                    if dist==None:
                        returnVal=p
                        dist=point.dist(p)
                        continue
                    else:
                        newDist=point.dist(p)
                        if dist>newDist:
                            dist=newDist
                            returnVal=p
        return returnVal
        
        
        
        
        
        
        
        
class SnapMark(QtGui.QGraphicsItem):
    def __init__(self):
        super(SnapMark, self).__init__()
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations, True)
        self.hide()

    def shape(self):            
        """
            overloading of the shape method 
        """
        return self.definePath()
        
    def boundingRect(self):
        """
            overloading of the qt bounding rectangle
        """
        return self.shape().boundingRect()
    
    def paint(self, painter,option,widget):
        """
            overloading of the paint method
        """
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 50, 50), 2, join=QtCore.Qt.MiterJoin))
        painter.drawPath(self.definePath())
        
    def move(self, x, y):
        """
            show the previously added mark and place it in snap position
        """
        self.show()
        self.setPos(x, y)
        
class SnapEndMark(SnapMark):
    def __init__(self, x, y):
        super(SnapEndMark, self).__init__()
        self.setToolTip("EndPoint")
        self.x=x
        self.y=y
    
    def definePath(self):
        rect=QtCore.QRectF(self.x-5.0, self.y-5.0, 10.0, 10.0)
        path=QtGui.QPainterPath()
        path.addRect(rect)
        return path
   
