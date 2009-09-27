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

import math
import types
import warnings

import pygtk
pygtk.require('2.0')
import gtk

from PythonCAD.Generic import util
from PythonCAD.Generic import intersections
from PythonCAD.Generic.segment  import Segment
from PythonCAD.Generic.circle   import Circle
from PythonCAD.Generic import point

class Snap:
    """
        define a class used to find intersection point 
    """
    def __init__(self,topLayer,snapOption):
        """
            Default Constructor
        """
        self._topLayer=topLayer
        self._sn=snapOption
        self._oneShutSnap=snapOption.copy() 
        self._computeOneShutSnap=False
        self.__DinamicSnap=False
        self.__FirstEnt=None
        self.__FirstPoint=None,None
        self.__FirstType=None
        self.__Cursor=None
    def GetSnap(self,x,y,tollerance,windows):
        """
            Get the snap point 
        """
        if(self.__Cursor==None):
            self.__Cursor=snapCursor(windows)
        _x=util.get_float(x)
        _y=util.get_float(y)
        t=util.get_float(tollerance)

        if(self._computeOneShutSnap):
            sn=self._oneShutSnap
        else:
            sn=self._sn
        if t < 0.0:
            raise ValueError, "Invalid negative tolerance: %f" % t
        exitValue={'point':None,'responce':False,'cursor':None,'name':"noname"}        
        mousePoint=point.Point(_x,_y)
        if('mid' in  sn):
            if(sn['mid']):
                _X,_Y,found=self.GetMid(_x,_y,t)
                if(found):
                    newSnap=point.Point(_X,_Y)
                    exitValue['point']=newSnap
                    exitValue['responce']=found
                    exitValue['cursor']=self.__Cursor.MidPoint()
                    exitValue['name']="Mid"
        if('end' in  sn):
            if(sn['end']):
                _X,_Y,found=self.GetEnd(_x,_y,t)
                if(found):
                    newSnap=point.Point(_X,_Y)
                    cursor=self.__Cursor.EndPoint()
                    if(exitValue['point']==None):
                        exitValue['point']=newSnap
                        exitValue['responce']=found
                        exitValue['cursor']=cursor
                        exitValue['name']="End"
                    else:
                        if(newSnap.Dist(mousePoint)<exitValue['point'].Dist(mousePoint)):
                            exitValue['point']=newSnap
                            exitValue['responce']=found
                            exitValue['cursor']=cursor
                            exitValue['name']="End"
        if('intersection' in  sn):
            if(sn['intersection']):
                _X,_Y,found=self.GetIntersection(_x,_y,t)
                if(found):
                    newSnap=point.Point(_X,_Y)
                    cursor=self.__Cursor.IntersectionPoint()
                    if(exitValue['point']==None):
                        exitValue['point']=newSnap
                        exitValue['responce']=found
                        exitValue['cursor']=cursor
                        exitValue['name']="Intersection"
                    else:
                        if(newSnap.Dist(mousePoint)<exitValue['point'].Dist(mousePoint)):
                            exitValue['point']=newSnap
                            exitValue['responce']=found
                            exitValue['cursor']=cursor
                            exitValue['name']="Intersection"
        if('origin' in  sn):
            if(sn['origin']):
                newSnap=point.Point(0.0,0.0)
                exitValue['point']=newSnap
                exitValue['responce']=True
                exitValue['cursor']=self.__Cursor.ZeroZeroPoint()
                exitValue['name']="Origin"
        if('perpendicular' in  sn):
            if(sn['perpendicular']):
                if(self.GetEnt(_x,_y,t)!=None):
                    self.__DinamicSnap=True
                    exitValue['point']=None
                    exitValue['responce']=True
                    exitValue['cursor']=self.__Cursor.PerpendicularPoint()
                    exitValue['name']="Perpendicular"
        if('tangent' in sn):
            if(sn['tangent']):
                if(self.GetEnt(_x,_y,t)!=None):
                    self.__DinamicSnap=True
                    exitValue['point']=None
                    exitValue['responce']=True
                    exitValue['cursor']=self.__Cursor.TangentPoint()
                    exitValue['name']="Tangent"
        if('point' in  sn):
            if(sn['point']):
                _X,_Y,found=self.GetPoint(_x,_y,t)
                if found :
                    newSnap=point.Point(_X,_Y)
                    exitValue['point']=newSnap
                    exitValue['responce']=True
                    exitValue['cursor']=self.__Cursor.Point()
                    exitValue['name']="Point"        
        self.__exitValue=exitValue
        if(exitValue['point']!=None): retX,RetY=exitValue['point'].getCoords()
        else: retX,RetY=(None,None)
        return retX,RetY,exitValue['responce'],exitValue['cursor']
    
    def GetPoint(self,x,y,_t):
        """
            Get The point over the mouse
        """
        _types = {'point' : True}
        _tl=[self._topLayer]
        while len(_tl):
            _layer = _tl.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    _ix,_iy=_obj.getCoords()
                    return _ix,_iy,True
        return None,None,False
    
    def GetMid(self,x,y,_t):
        """"
            Calculate the mid point 
        """
        _types = {'segment' : True}
        _tl=[self._topLayer]
        while len(_tl):
            _layer = _tl.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    _ix,_iy=_obj.getMiddlePoint()
                    return _ix,_iy,True
        return None,None,False

    def GetEndPoint(self,x,y,entityHits):
        """
            Looking for a specifiePoint             
        """
        nearestPoint = (None,None)
        mousePoint=point.Point(x,y)
        if len(entityHits) > 0:
            for _obj, _pt in entityHits:
                _op1, _op2 = _obj.getEndpoints()
                if(mousePoint.Dist(_op1)<mousePoint.Dist(_op2)):
                    nPoint=_op1
                else:
                    nPoint=_op2
                distance=nPoint.Dist(mousePoint)
                if nearestPoint[0] is None or distance < nearestPoint[1]: 
                    nearestPoint = nPoint,distance
            _ex,_ey=nearestPoint[0].getCoords()
            return _ex,_ey ,True 
        return None,None,False
    
    def GetEnd(self,x,y,t):
        """
            Calculate the end point
        """
        _types = {'segment' : True}
        _active_layer = self._topLayer
        _sep = None
        _hits = _active_layer.mapCoords(x, y, tolerance=t, types=_types)
        retX,retY,validate=self.GetEndPoint(x,y,_hits)
        if(validate):
            return retX,retY,validate
        #
        # See if any other Layer contains a Point ...
        #
        _layers = [self._topLayer]
        while len(_layers):
            _layer = _layers.pop()
            if _layer is not _active_layer:
                _hits = _layer.mapCoords(x, y, tolerance=t, types=_types)
                retX,retY,validate=self.GetEndPoint(x,y,_hits)
                if(validate):
                    return retX,retY,validate
            _layers.extend(_layer.getSublayers())
        return None,None,False
    
    def GetIntersection(self,x,y,_t):
        """
            Calculate the intersection point
        """
        _objlist = []
        _intlist = []
        _types = {'point' : False,
                  'segment' : True,
                  'circle' : True,
                  'arc' : True,
                  'polyline' : True,
                  'hcline' : True,
                  'vcline' : True,
                  'acline' : True,
                  'cline' : True,
                  'ccircle' : True,
                  }
        _layers = [self._topLayer]
        while len(_layers):
            _layer = _layers.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    for _tobj, _mp in _objlist:
                        for _ix, _iy in intersections.find_intersections(_tobj, _obj):
                            if ((abs(_ix - x) < _t) and
                                (abs(_iy - y) < _t)):
                                _sqlen = pow((x - _ix), 2) + pow((y - _iy), 2)
                                _intlist.append((_sqlen, (_ix, _iy)))
                    _objlist.append((_obj, _pt))
            _layers.extend(_layer.getSublayers())
        #
        # use the nearest intersection point if one is available
        #
        if len(_intlist):
            _intlist.sort()
            _cp = _intlist[0][1]
            if _cp is not None:
                return _cp[0],_cp[1],True
        return None,None,False
    
    def GetOrigin(self):
        """
            Return the drawing origin point 
        """
        return 0.0,0.0,True

    def GetEnt(self,x,y,_t):
        """
            Get The Entity Under the Mouse Pointer
        """
        _objlist = []
        _intlist = []
        _types = {'point' : False,
                  'segment' : True,
                  'circle' : True,
                  'arc' : True,
                  'polyline' : True,
                  'hcline' : True,
                  'vcline' : True,
                  'acline' : True,
                  'cline' : True,
                  'ccircle' : True,
                  }
        _layers = [self._topLayer]
        while len(_layers):
            _layer = _layers.pop()
            _hits = _layer.mapCoords(x, y, tolerance=_t, types=_types)
            if len(_hits) > 0:
                for _obj, _pt in _hits:
                    if(_obj != None):
                        return _obj
        return None
    def SetOneShutSnap(self,activeSnap):
        """
            Set One Shot snap 
        """       
        for key in self._oneShutSnap.keys():
            if(key==activeSnap):
                self._oneShutSnap[key]=True
            else:
                self._oneShutSnap[key]=False
        self.ComputeOneShutSnap()

    def ComputeOneShutSnap(self):
        """
            Activate Compute One ShotSnap
        """
        self._computeOneShutSnap=True

    def StopOneShutSnap(self):
        """
            Stop Computetion One ShutSnap
        """
        self._computeOneShutSnap=False
    def DinamicSnap(self):
        """
            Indicate if snap Compute the point
        """
        return self.__DinamicSnap
    def ResetDinamicSnap(self):
        """
            Indicate if snap Compute the point
        """
        self.__FirstEnt=None
        self.__FirstPoint=None,None
        self.StopOneShutSnap()
        self.StopDinamicSnap()
    def StopDinamicSnap(self):
        """
            stop using dianmic snap
        """
        self.__DinamicSnap=False
        for key in self._oneShutSnap.keys():
            self._oneShutSnap[key]=False
        
    def GetCoords(self,px,py,_t):
        """
            Get The Cordinate for Building the segment 
            used for the Preview too
        """
        _x=util.get_float(px)
        _y=util.get_float(py)
        if(self.__FirstEnt!=None):
            if(isinstance(self.__FirstEnt,Segment)):
                firstObj=self.__FirstEnt
                x,y,found,cursor=self.GetSnap(_x,_y,_t,None)
                if(x is None):
                    pjPoint=firstObj.GetLineProjection(_x,_y)
                else:
                    pjPoint=firstObj.GetLineProjection(x,y)
                if(pjPoint!=None):
                    x,y=pjPoint
                else: #Convention get the first endline point
                    x1=firstObj.getP1().x 
                    y1=firstObj.getP1().y
                return x,y,_x,_y 
            if(isinstance(self.__FirstEnt,Circle)):
                if(self.__FirstType=="Tangent"): #Firts snap is a tangent
                    obj=self.__FirstEnt
                    x,y=self.__FirstPoint
                    pjPoint=obj.GetTangentPoint(x,y,_x,_y)
                    if(pjPoint!=None):
                        x1,y1=pjPoint.getCoords()         
                        return _x,_y,x1,y1
            else:
                print("is Not a snap Known Entitis")       
        if(self.__FirstPoint!=(None,None)): #First pick is a point     
            obj=self.GetEnt(_x,_y,_t)       #Evaluate the sencond
            x,y=self.__FirstPoint
            x1,y1=_x,_y 
            if(obj!=None):
                if(isinstance(obj,Segment)):
                    if(self.__exitValue['name']=="Perpendicular"):
                        pjPoint=obj.GetLineProjection(x,y)
                        x1,y1=pjPoint
                if(isinstance(obj,Circle)):
                    if(self.__exitValue['name']=="Tangent"):
                        pjPoint=obj.GetTangentPoint(x1,y1,x,y)
                        if(pjPoint!=None):
                            x1,y1=pjPoint.getCoords()            
            return x,y,x1,y1
        raise "No solution found in GetCoords"

    def getProjection(self,fromX,fromY,mauseX,mauseY,t):
        """
            get the projection of the point fromX,fromY,to the entity found 
            under mauseX,mauseY
        """
        obj=self.GetEnt(mauseX,mauseY,t)
        if(obj!=None):
            if(isinstance(obj,Segment)):
                if(self.__exitValue['name']=="Tangent"):
                    pjPoint=obj.GetLineProjection(fromX,fromY)
                    x1,y1=pjPoint  
                    return x1,y1
            if(isinstance(obj,Circle)):
                if(self.__exitValue['name']=="Tangent"):
                    return obj.GetRadiusPointFromExt(fromX,fromY)
            
        return mauseX,mauseY

    def SetFirstClick(self,_x,_y,_t):
        """
            set First Click 
        """
        obj=self.GetEnt(_x,_y,_t)
        self.__FirstType=self.__exitValue['name']
        if(obj!=None and self.DinamicSnap()):
            self.__FirstEnt=obj
            self.__FirstPoint=_x,_y
        else:
            self.__FirstEnt=None
            x,y,found,cursor=self.GetSnap(_x,_y,_t,None)
            if(x is None):
                self.__FirstPoint=_x,_y
            else:
                self.__FirstPoint=x,y

class snapCursor:
    """
        This class provide a cursor object for each snap
    """
    def __init__(self,windows):
        """
            Base Constructor
        """
        #self.__pm = gtk.gdk.Pixmap(None,15,15,1)
        #self.__mask = gtk.gdk.Pixmap(None,15,15,1)
        #colormap = gtk.gdk.colormap_get_system()
        #black = colormap.alloc_color('black')
        #white = colormap.alloc_color('white')
        #self.__bgc = self.__pm.new_gc(foreground=black)
        #self.__wgc = self.__pm.new_gc(foreground=white)
        #self.__mask.draw_rectangle(self.__bgc,True,0,0,15,15)
        #self.__pm.draw_rectangle(self.__wgc,True,0,0,15,15)
        self.__pm = None
        self.__mask = None
        self.__Draw=windows
        self.__style=gtk.Style()
    def Cursor(self):
        """
            set The Cursor at the window
        """
        if(self.__pm==None or self.__mask==None):
            print("NonePixmaps")
        #cur=gtk.gdk.Cursor(self.__pm,self.__mask,gtk.gdk.color_parse("black"),gtk.gdk.color_parse("white"),1,1)
        cur=gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
        return cur
    def UpdatePixmap(self,pixmapName):
        """
            Create a pixmap from a vector
        """
        try:
            self.__pm, self.__mask = gtk.gdk.pixmap_create_from_xpm_d(
                self.__Draw,self.__style.bg[gtk.STATE_NORMAL], pixmapName)
        except:
            print("Unable to create the pixmap")
    def Point(self):
        """
            Define the Point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "..@@@@@@@@@@@..",
         ".@@@@@@@@@@@@@.",
         "@@@@@@@.@@@@@@@",
         "@@@@.......@@@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@@@.......@@@@",
         "@@@@@@@.@@@@@@@",
         ".@@@@@@@@@@@@@.",
         "..@@@@@@@@@@@.."
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.DOTBOX)
    def EndPoint(self):
        """
            Define the endPoint Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "..@@@@@@@@@@@..",
         ".@@@@@@@@@@@@@.",
         "@@@@@@@.@@@@@@@",
         "@@@@.......@@@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@@@.......@@@@",
         "@@@@@@@.@@@@@@@",
         ".@@@@@@@@@@@@@.",
         "..@@@@@@@@@@@.."
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.DOTBOX)
    def MidPoint(self):
        """
            Define the Mid point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "@@@@@@@@@@@@@@@",
         "@@@@@@@@@@@@@@@",
         "@@@@@@@@@@@@@@@",
         "@@..........@@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@...........@@",
         "@@@..........@@",
         "@@@@@@@@@@@@@@@",
         "@@@@@@@@@@@@@@@",
         "@@@@@@@@@@@@@@@"
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.ICON)
    def ZeroZeroPoint(self):
        """
            Define the Origin point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "...............",
         "...............",
         "...............",
         "...............",
         ".@@.........@@.",
         "@..@.......@..@",
         "@..@.......@..@",
         "@..@.......@..@",
         ".@@....@....@@.",
         "...............",
         "...............",
         "...............",
         "...............",
         "...............",
         "..............."
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.DRAPED_BOX)
    def PerpendicularPoint(self):
        """
            Define the perpendicular point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "...@@@.........",
         "...@@@.........",
         "...@@@.........",
         "...@@@.........",
         "...@@@.........",
         "...@@@.........",
         "...@@@.........",
         "...@@@.........",
         "...@@@@@@@@@@..",
         "...@@@@@@@@@@..",
         "...@@@...@@@@..",
         "...@@@....@@@..",
         "...@@@....@@@..",
         "@@@@@@@@@@@@@@@",
         "@@@@@@@@@@@@@@@"
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.BOTTOM_TEE)
    def IntersectionPoint(self):
        """
            Define the perpendicular point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "@............@@",
         "@@..........@@.",
         ".@@........@@..",
         "..@@......@@...",
         "...@@....@@....",
         "....@@..@@.....",
         ".....@@@@......",
         "......@@.......",
         ".....@@@@......",
         "....@@..@@.....",
         "...@@....@@....",
         "..@@......@@...",
         ".@@........@@..",
         "@@..........@@.",
         "@............@@"
        ]
        mask=self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
    def TangentPoint(self):
        """
            Define the perpendicular point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "...............",
         "...............",
         "...............",
         ".....@@@@@.....",
         "...@@@@.@@@@...",
         "..@@@@...@@@@..",
         ".@@@.......@@@.",
         "@@@.........@@@",
         "@@@.........@@@",
         ".@@@.......@@@.",
         "..@@@.....@@@..",
         "...@@@...@@@...",
         "@@@@@@@@@@@@@@@",
         "@@@@@@@@@@@@@@@",
         "..............."
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
    def OnCurvePoint(self):
        """
            Define the perpendicular point Cursor
        """
        xpm = [
         "15 15 2 1",
         ".      c none",
         "@      c black",
         "...............",
         "...............",
         "@@.............",
         ".@@............",
         "..@@...........",
         "..@@@@@@@@.....",
         "..@.@@@@.@.....",
         "..@....@@@@....",
         "..@......@@@...",
         "..@@@@@@@@..@@@",
         ".............@@",
         "..............@",
         "...............",
         "...............",
         "..............."
        ]
        self.UpdatePixmap(xpm)
        #return self.Cursor()
        return gtk.gdk.Cursor(gtk.gdk.X_CURSOR)
