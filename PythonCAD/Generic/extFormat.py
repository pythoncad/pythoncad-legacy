#
# Copyright (c) 2009 Matteo Boscolo
#
# This file is part of PythonCAD.
#
# PythonCAD is free software; you can redistribute it and/or modify
# it under the termscl_bo of the GNU General Public License as published by
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
#
# This code is written by Yagnesh Desai
#

dxfDebug=False

import os.path
import math # added to handle arc start and end point defination
import re # added to handle Mtext
from PythonCAD.Generic.point import Point
from PythonCAD.Generic.segment import Segment
from PythonCAD.Generic.circle import Circle
from PythonCAD.Generic.arc import Arc
from PythonCAD.Generic.polyline import Polyline
from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic.text import *

class ExtFormat(object):
    """
        This class provide base class for hendly different drawing format in pythoncad
    """
    def __init__(self,gtkimage):
        """
            Default Constructor
        """
        self.__gtkimage=gtkimage
 
    def openFile(self,fileName):
        """
           Open a generic file 
        """
        path,exte=os.path.splitext( fileName )
        if( exte.upper()==".dxf".upper()):
            dxf=Dxf(self.__gtkimage,fileName)
            dxf.importEntitis()

    def saveFile(self,fileName):
        """
            save the current file in a non pythoncad Format
        """
        path,exte=os.path.splitext( fileName )
        if( exte.upper()==".dxf".upper()):
            dxf=Dxf(self.__gtkimage,fileName)
            dxf.importEntitis()

class DrawingFile(object):
    """
        This Class provide base capability to read write a  file
    """
    def __init__(self,fileName):
        """
            Base Constructor
        """
        dPrint( "Debug: DrawingFile constructor")
        self.__fn=fileName
        self.__fb=None
        self.__error=[]
        self.__reading=False
        self.__lineNumber=0
    def readAsci(self):
        """
            Read a generic file 
        """
        dPrint("Debug: Read asci File")
        self.__fb=open(self.__fn,'r')
        self.__reading=True
        
    def createAsci(self):
        """
            create the new file 
        """
        self.__fb=open(self.__fn,'w')
        
    def fileObject(self):
        """
            Return the file opened 
        """
        dPrint( "Debug: GetFileObject")
        if self.__fb is not None: 
          dPrint( "Debug: Return file object")
          return self.__fb
        else: 
          dPrint( "Debug: None")
          return None
    
    def readLine(self):
        """
            read a line and return it
        """
        if self.__reading:
            self.__lineNumber=+1
            return self.__fb.readline()
        else:
            raise "Unable to perfor reading operation"
        
    def writeError(self,functionName,msg):
        """
            Add an Error to the Collection
        """
        _msg="Error on line %s function Name: %s Message %s"%(
            str(self.__lineNumber),functionName,msg)
        self.__error.append(_msg)

class Dxf(DrawingFile):
    """
        this class provide dxf reading/writing capability 
    """
    def __init__(self,gtkimage,fileName):
        """
            Default Constructor
        """
        dPrint( "Debug: Dxf constructor")
        DrawingFile.__init__(self,fileName)
        self.__gtkimage=gtkimage
        self.__image=gtkimage.getImage()
        _layerName,_ext=os.path.splitext(os.path.basename(fileName))
        _layerName="Imported_"+_layerName
        _dxfLayer=Layer(_layerName)
        self.__image.addLayer(_dxfLayer)
        self.__dxfLayer=_dxfLayer 
        

    def exportEntitis(self):
        """
            export The current file in dxf format
        """
        _fo=self.createAsci()               #open the file for writing
        _layersEnts=self.getAllEntitis()    #get all the entities from the file
        for _key in _layersEnts:            #Looping at all layer
            for _obj in _layersEnt[_key]:   #looping at all entities in the layer
                if isinstance(_obj,Segment):#if it's segment 
                    self.writeSegment(_obj) # ad it at the dxf drawing
                # go on end implements the other case arc circle ...
                
    def getAllEntitis(self):
        """
            retrive all the entitys from the drawing 
        """
        _outLayers={}
        _layers = [self.__image.getActiveLayer()]
        while len(_layers):
            _layerEnts=[]
            _layer = _layers.pop()
            _layerName=_layer.getName()
            _objs=_layer.getAllEntitys()
            for _o in _objs:
                _layerEnts.append(_o)
            _outLayers[_layerName]=_layerEnts
        return _outLayers
    
    def writeSegment(self,e):
        """
           write segment to the dxf file 
        """
        pass
        
    def importEntitis(self):
        """
            Open The file and create The entity in pythonCad
        """
        dPrint( "Debug: import entitys")
        self.readAsci();
        while True:
            _k = self.readLine()
            if not _k: break
            else:
                dPrint( "Debug: Read Line line = [%s]"%str(_k))
                if _k[0:4] == 'LINE':
                    self.createLineFromDxf()
                    continue
                if _k[0:6] == 'CIRCLE':
                    self.createCircleFromDxf()
                    continue
                if _k[0:5] == 'MTEXT':
                    self.createTextFromDxf()
                    continue
                if _k[0:4] == 'TEXT':
                    self.createTextFromDxf()
                    continue
                if _k[0:3] == 'ARC':
                    self.createArcFromDxf()
                    continue
                if _k[0:10] == 'LWPOLYLINE':
                    self.createPolylineFromDxf()
                    continue
                if _k[0:8] == 'POLYLINE':
                    self.createPolylineFromDxf()
                    continue
                if not _k : break
                else:
                    self.writeError("importEntitis","Entity Not supported %s"%str(_k))

    def createLineFromDxf(self):
        """
            read the line dxf section and create the line
        """
        dPrint( "Debug createLineFromDxf" )
        x1 = None
        y1 = None
        x2 = None
        y2 = None
        g = 0 # start counter to read lines
        while g < 18:
            #print "Debug g =", g
            #print "Debug: Read line  g = %s Value = %s "%(str(g),str(line))
            _k = self.readLine()
            #print "Debug: Read line g = %s k =  %s "%(str(g),str(k))
            """if g == 5:# this line contains color property
            we can get the color presently not implemented
            color=(float(k[0:-1]))"""
            dPrint( "line value k="+_k)
            if _k[0:3] == ' 10':
                dPrint( "debug 10"+ _k)
                # this line of file contains start point"X" co ordinate
                #print "Debug: Convert To flot x1: %s" % str(k[0:-1])
                _k = self.readLine()
                x1 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 20':# this line of file contains start point "Y" co ordinate
                #print "Debug: Convert To flot y1: %s" % str(k[0:-1])
                _k = self.readLine()
                y1 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 30':# this line of file contains start point "Z" co ordinate
                #print "Debug: Convert To flot z1: %s" % str(k[0:-1])
                _k = self.readLine()
                z1 = (float(_k[0:-1])) 
                continue
                # Z co ordinates are not used in PythonCAD we can live without this line
            if _k[0:3] == ' 11':# this line of file contains End point "X" co ordinate
                #print "Debug: Convert To flot x2: %s" % str(k[0:-1])
                _k = self.readLine()
                x2 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 21':# this line of file contains End point "Y" co ordinate
                #print "Debug: Convert To flot y2: %s" % str(k[0:-1])
                _k = self.readLine()
                y2 = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 31':# this line of file contains End point "Z" co ordinate
                #print "Debug: Convert To flot z2: %s" % str(k[0:-1])
                _k = self.readLine() 
                z2 = (float(_k[0:-1]))
                g = 30
                continue
                #Z co ordinates are not used in PythonCAD we can live without this line
                'I need a "create segment code" here to append the segment to image'
            g+=1
        if not ( x1==None or y1 ==None or
           x2==None or y2 ==None ):
            self.createLine(x1,y1,x2,y2)


    def createLine(self,x1,y1,x2,y2):
      """
          Create the line into the current drawing
          In this implementation all the lines gose to the active layer and use the global settings of pythoncad
          Feauture implementation could be :
          1) Create a new layer(ex: Dxf Import)
          2) Read dxf import style propertis and set it to the line
      """    
      dPrint( "Debug Creatre line %s,%s,%s,%s"%(str(x1),str(y1),str(x2),str(y2)) )
      _active_layer = self.__dxfLayer
      _p1 = Point(x1, y1)
      _active_layer.addObject(_p1)
      _p2 = Point(x2, y2)
      _active_layer.addObject(_p2)
      _s = self.__image.getOption('LINE_STYLE')
      _seg = Segment(_p1, _p2, _s)
      _l = self.__image.getOption('LINE_TYPE')
      if _l != _s.getLinetype():
          _seg.setLinetype(_l)
      _c = self.__image.getOption('LINE_COLOR')
      if _c != _s.getColor():
          _seg.setColor(_c)
      _t = self.__image.getOption('LINE_THICKNESS')
      if abs(_t - _s.getThickness()) > 1e-10:
          _seg.setThickness(_t)
      _active_layer.addObject(_seg)
    
    def createCircleFromDxf(self):
        """
            Read and create the Circle into drawing
        """
        dPrint( "Debug createCircleFromDxf" )
        g = 0 # reset g
        while g < 1:
            _k = self.readLine()
            dPrint( "line value k="+ _k)
            if _k[0:3] == ' 10':
                _k = self.readLine()
                x = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 20':
                _k = self.readLine()
                y = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 40':
                _k = self.readLine()
                r = (float(_k[0:-1]))
                g = 10 # g > 1 for break
                'I need a "create Circle code" here to append the segment to image'
        self.createCircle(x,y,r)
        
    def createCircle(self,x,y,r):
        """
            create a circle entitys into the current drawing
        """
        _active_layer = self.__dxfLayer
        _center = Point(x, y)
        _active_layer.addObject(_center)
        _s = self.__image.getOption('LINE_STYLE')
        _circle = Circle(_center, r, _s)        
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
            _circle.setLinetype(_l)
        _c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
            _circle.setColor(_c)
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
            _circle.setThickness(_t)
        _active_layer.addObject(_circle)
    def createTextFromDxf(self):
        """
            Read and create the Circle into drawing
        """
        dPrint( "Debug createTextFromDxf" )
        g = 0 # reset g
        while g < 1:
            _k = self.readLine()
            dPrint("line value k="+ _k)
            if _k[0:3] == ' 10':
                _k = self.readLine()
                x = (float(_k[0:-1]))
                #print "Text Loc x =", x
                continue
            if _k[0:3] == ' 20':
                _k = self.readLine()
                y = (float(_k[0:-1]))
                #rint "Text Loc y =", y
                continue
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z = (float(_k[0:-1]))
                #print "Text Loc z =", z
                continue
            if _k[0:3] == ' 40':
                _k = self.readLine()
                h = (float(_k[0:-1]))
                dPrint("Text Height =%s"%str(h))
                continue
            if _k[0:3] == '  1':
                _k = self.readLine()
                _t = _k.replace('\~', ' ')
                _t = _t.replace('\P', '\n')
                #print "Text itself is ", x, y, z, 'height', h, _t#
                g = 10 # g > 1 for break
                continue
        self.createText(x,y,h,_t)
    def createArcFromDxf(self):
        """
            Read and create the ARC into drawing
        """ 
        g = 0 # reset g
        while g < 1:
            _k = self.readLine()
            if _k[0:3] == ' 10':
                _k = self.readLine()
                x = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 20':
                _k = self.readLine()
                y = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z = (float(_k[0:-1]))
            if _k[0:3] == ' 40':
                _k = self.readLine()
                r = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 50':
                _k = self.readLine()
                sa = (float(_k[0:-1]))
                continue
            if _k[0:3] == ' 51':
                _k = self.readLine()
                ea = (float(_k[0:-1]))
                g = 10 # g > 1 for break\\
                continue
        self.createArc(x,y,sa,ea,r)

    def createArc(self,x,y,sa,ea,r):
        """
            Create a Arc entitys into the current drawing
        """
        _active_layer = self.__dxfLayer
        _center = Point(x, y)
        _active_layer.addObject(_center)
        _s = self.__image.getOption('LINE_STYLE')
        py = (22.0/7.0)
        ex = x + r*math.cos((sa*py)/180)
        ey = y + r*math.sin((sa*py)/180)
        lpx = x + r*math.cos((ea*py)/180)
        lpy = y + r*math.sin((ea*py)/180)
        ep = Point(ex, ey)
        lp = Point(lpx, lpy)
        _active_layer.addObject(ep)
        _active_layer.addObject(lp)
        _arc = Arc(_center, r, sa, ea, _s)
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
            _arc.setLinetype(_l)
        _c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
            _arc.setColor(_c)
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
            _arc.setThickness(_t)
        _active_layer.addObject(_arc)

    def createText(self,x,y,h,t):
        """
            Create a Text entitys into the current drawing
        """
        _active_layer = self.__dxfLayer
        try:
            _text = unicode(str(t))
        except:
            self.writeError("createText","Debug Error Converting in unicode [%s]"%t)
            _text = str(t)
        _x, _y = x, y
        _ts = self.__image.getOption('TEXT_STYLE')
        _tb = TextBlock(_x, _y, _text, _ts)

        _f = self.__image.getOption('FONT_FAMILY')
        if _f != _ts.getFamily():
            _tb.setFamily(_f)

        _s = self.__image.getOption('FONT_STYLE')
        if _s != _ts.getStyle():
            _tb.setStyle(_s)

        _w = self.__image.getOption('FONT_WEIGHT')
        if _w != _ts.getWeight():
            _tb.setWeight(_w)
            
        _c = self.__image.getOption('FONT_COLOR')
        if _c != _ts.getColor():
            _tb.setColor(_c)
        _sz = h
        if abs(_sz - _ts.getSize()) > 1e-10:
            _tb.setSize(_sz)
        _a = self.__image.getOption('TEXT_ANGLE')
        if abs(_a - _ts.getAngle()) > 1e-10:
            _tb.setAngle(_a)
        _al = self.__image.getOption('TEXT_ALIGNMENT')
        if _al != _ts.getAlignment():
            _tb.setAlignment(_al)
        _active_layer.addObject(_tb)

    def createPolylineFromDxf(self):
        """
        Polyline creation read the line dxf section and create the line
        """
        dPrint("Exec createPolylineFromDxf")
        while True:
            _k = self.readLine()                  
            if _k[0:3] == ' 10':
                break
        points=[]
        p = ()
        while True:
            # this line of file contains start point"X" co ordinate
            # print "Debug: Convert To flot x1: %s" % str(k[0:-1])
            _k = self.readLine()
            x = (float(_k[0:-1]))
            _k = self.readLine()#pass for k[0:3] == ' 20'
            _k = self.readLine()
            y = (float(_k[0:-1]))
            p = (x,y)
            points.append(p)
            dPrint( str(points))
            _k = self.readLine()
            if _k[0:3] == ' 30':
                _k = self.readLine()
                z1 = (float(_k[0:-1]))
                continue
            elif _k[0:3] != ' 10':
                break
        if len(points)>1:
            self.createPolyline(points)
        
    def createPolyline(self,points):
        """
            Crate poliline into Pythoncad
        """
        dPrint("Exec createPolyline")
        _active_layer = self.__dxfLayer
        _x = 0.0
        _y = 0.0
        _pts = []
        for _x, _y in points:
            dPrint(_x)
            dPrint(_y)
            _p = Point(_x, _y)
            _active_layer.addObject(_p)
            _pts.append(_p)
        dPrint("Exec createPolyline lenPts(%s)"%str(len(_pts)))
        _s = self.__image.getOption('LINE_STYLE')
        _pline = Polyline(_pts, _s)
        _l = self.__image.getOption('LINE_TYPE')
        if _l != _s.getLinetype():
          _pline.setLinetype(_l)
        _c = self.__image.getOption('LINE_COLOR')
        if _c != _s.getColor():
          _pline.setColor(_c)
        _t = self.__image.getOption('LINE_THICKNESS')
        if abs(_t - _s.getThickness()) > 1e-10:
          _pline.setThickness(_t)
        _active_layer.addObject(_pline)


    
def dPrint(msg):
    """
        Debug function for the dxf file
    """
    if dxfDebug :
        print "Debug: %s " %str(msg)
