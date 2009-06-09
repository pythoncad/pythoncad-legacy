#
# Copyright (c) 2002-2004 Art Haas
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
# Cocoa CAD drawing view 
#

from math import hypot, ceil

from objc import nil

from PyObjCTools import NibClassBuilder
from Foundation import *
from AppKit import *

import PythonCAD.Generic.graphicobject
import PythonCAD.Generic.layer
import PythonCAD.Generic.globals
import PythonCAD.Generic.segment
import PythonCAD.Generic.circle
import PythonCAD.Generic.arc
import PythonCAD.Generic.hcline
import PythonCAD.Generic.vcline
import PythonCAD.Generic.acline
import PythonCAD.Generic.cline
import PythonCAD.Generic.ccircle
import PythonCAD.Generic.conobject
import PythonCAD.Generic.segjoint
import PythonCAD.Generic.leader
import PythonCAD.Generic.polyline
import PythonCAD.Generic.text
import PythonCAD.Generic.dimension
import PythonCAD.Generic.tools

import PythonCAD.Interface.Cocoa.Globals
# import PythonCAD.Interface.Cocoa.ImageDocument
# import PythonCAD.Interface.Cocoa.ImageWindowController
# import PythonCAD.Interface.Cocoa.AppController


#
# Define True & False in case this is Python < 2.2.1
#
try:
    True, False
except NameError:
    True, False = 1, 0
    
#
# Global variables
#
PythonCAD.Generic.globals.NSColors = {}
PythonCAD.Generic.globals.NSFonts = {}

NibClassBuilder.extractClasses("ImageDocument")


class CADView(NibClassBuilder.AutoBaseClass, PythonCAD.Generic.message.Messenger):
    """ Custom NSView for visual display & editing of a PythonCad CAD image.
    
A CADView is an NSView used for editing & display of a generic Image object.

    """

#
# Beginning of Cocoa methods
#
    def init(self):
        """ NSView override for cocoa initializer of CADView
        
init()
        """
        self = super(CADView, self).init()
        if (self):
            self.__mouseTrackTimer = None
            self.__document = None
            self.__tracking_rect = None
            self.__trans = None
            self.__x_scale = 1.0
            self.__y_scale = 1.0
            
        return self
            

    def awakeFromNib(self):
        """ NSView override for post-NIB loading initialization

awakeFromNib(self)
        """
        #
        # initialize variables
        #
        self.__mouseTrackTimer = None
        self.__document = None
        self.__tracking_rect = None
        self.__trans = None
        self.__temporaryObject = []
        self.__temporaryPoint = NSMakePoint(0.0,0.0)
        self.__temporaryRect = NSMakeRect(0.0, 0.0, 0.0, 0.0)
        self.__x_scale = 1.0
        self.__y_scale = 1.0
        self.updateTrackingRect()
        self.setTransform()
        _cv = self.enclosingScrollView().contentView()
        #
        # register for frame updates
        #
        _nc = NSNotificationCenter.defaultCenter()
        _nc.addObserver_selector_name_object_(self, "frameChangeNotification:", "NSViewFrameDidChangeNotification", _cv)
        _nc.addObserver_selector_name_object_(self, "boundsChangeNotification:", "NSViewBoundsDidChangeNotification", self)
        _nc.addObserver_selector_name_object_(self, "windowCloseNotification:", "NSWindowWillCloseNotification", self.window())
                
    def isOpaque(self):
        _bool = self.inLiveResize()
        if _bool:
            return False
        return True
        
    def getDocument(self):
        """ Gets ImageDocument displayed by this view
        
getDocument()
        """
        if self.__document is None:
            self.__document = self.window().windowController().document()
        return self.__document
                        
    def setMouseTimer(self, timer):
        """ Sets timer for tracking mouse location
        
setMouseTimer(timer)
        """
        if (self.__mouseTrackTimer) is not None:
            self.__mouseTrackTimer.invalidate()
        self.__mouseTrackTimer = timer
        
    def setTrackingRect(self, rect):
        """ Sets up tracking rectange for mouse location
        
setTrackingRect(rect)
        """
        if (self.__tracking_rect) is not None:
            self.removeTrackingRect_(self.__tracking_rect)
        self.__tracking_rect = rect
          
                    
        
    def windowCloseNotification_(self, note):
        _nc = NSNotificationCenter.defaultCenter()
        _nc.removeObserver_(self)
        self.setMouseTimer(None)
        
    def frameChangeNotification_(self, note):
        """ NSView message for changes in enclosing clip view frame size
        
frameChangeNotification(note)
        """
        #
        # if the area for the CADView is bigger than the CADview,
        # we make the CADView bigger.  It might make sense later to
        # shrink the CADView IF we can do so without hiding any images
        #
        _cv = note.object()
        _cvsize = _cv.frame().size
        _mysize = self.frame().size
        _redraw = False
        if (_cvsize.width > _mysize.width):
            _mysize.width = _cvsize.width
            _redraw = True
        if (_cvsize.height > _mysize.height):
            _mysize.height = _cvsize.height
            _redraw = True
        if (_redraw):
            self.setFrameSize_(_mysize)
            self.setNeedsDisplay_(True)
        self.updateTrackingRect()
        PythonCAD.Generic.globals.NSFonts.clear()
        self.setTransform()


    def boundsChangeNotification_(self, note):
        """ NSView message for changes in bounds size
        
boundsChangeNotification(note)
        """
        self.setTransform()
        PythonCAD.Generic.globals.NSFonts.clear()
        
    def itemAddedNotification_(self, note):
        """ ImageDocument message for new item added to drawing

itemAddedNotification(note)
        """
        self.setNeedsDisplayInRect_(self._getTempRect())
        self._clearTempItems()
        _info = note.userInfo()
        if not _info.has_key("layer"):
            return
        if not _info["layer"].isVisible():
            return
        if _info.has_key("item") and self.canDraw():
            _item = _info["item"]
            _objList = [_item]
            # 
            # assume item added to active layer - might be a problem
            #
            self.lockFocus()
            _bounds = self.bounds()
            if isinstance(_item, PythonCAD.Generic.conobject.ConstructionObject):
                self._drawConstructionObjects(_objList, _bounds, True)
                
            elif isinstance(_item, PythonCAD.Generic.point.Point):
                if self.getDocument().getOption('HIGHLIGHT_POINTS'):
                    self._drawPoints(_objList, _bounds)
            else:
                self._drawObjects(_objList, _bounds, True)
                
            self.unlockFocus()

    def itemDeletedNotification_(self, note):
        """ ImageDocument message for item deleted from drawing

itemDeletedNotification(note)
        """
        _info = note.userInfo()
        if not _info.has_key("layer"):
            return
        if not _info["layer"].isVisible():
            return
        self.setNeedsDisplay_(True)
            
    def setTempPoint(self, point=NSMakePoint(0.0, 0.0)):
        self.__temporaryPoint = point
            
    def setTempObject(self, obj=None, flush=True):
        if obj is None:
            self.__temporaryObject = []
        elif isinstance(obj, (PythonCAD.Generic.graphicobject.GraphicObject,
                              PythonCAD.Generic.graphicobject.old_GraphicObject,
                              PythonCAD.Generic.text.TextBlock,
                              PythonCAD.Generic.dimension.Dimension)):
                if flush:
                    self.__temporaryObject=[obj]
                else:
                    self.__temporaryObject.append(obj)
        else:
            raise TypeError, "Invalid graphics object:" + `obj`

    def flushTempObjects(self):
        self.setNeedsDisplayInRect_(self._getTempRect())
        self._clearTempItems()

    def _setTempRect(self, rect=NSMakeRect(0.0,0.0,0.0,0.0)):
        self.__temporaryRect = rect
        
    def _getTempRect(self):
        return self.__temporaryRect

    def _getTempObject(self):
        return self.__temporaryObject
        
    def _clearTempItems(self):
        self.setTempPoint()
        self._setTempRect()
        self.setTempObject(None)
            
    def getImageRep(self):
        _frame = self.frame() 
        _img = NSImage.alloc().initWithSize_(_frame.size)
        _img.setScalesWhenResized_(False)
        _img.lockFocus()
        self.drawRect_(self.frame())
        _img.unlockFocus()
        return _img
          
#    def viewWillStartLiveResize(self):
#        super(CADView, self).viewWillStartLiveResize()
#        _bounds = self.bounds() 
#        _image = NSImage.alloc().initWithSize_(_bounds.size) 
#        _image.setCachedSeparately_(True)
#        _image.lockFocus()
#        self.drawRect_(_bounds)
#        _image.unlockFocus()
#        self.__image = NSImageView.alloc().initWithFrame_(_bounds)
#        self.addSubview_(self.__image)
#        self.__image.setAutoresizingMask_(NSViewWidthSizable|NSViewHeightSizable)
#        self.__image.setBounds_(_bounds)
#        self.__image.setImage_(_image)
        
       
    def postLoadSetup(self):
        """ Called after window loaded to make sure things register correctly.
        Should be able to do this with built-in functions, but can't get it to work.
        """
        _img = self.getDocument().getImage()
        _obj = PythonCAD.Interface.Cocoa.Globals.wrap(_img)
        _nc = NSNotificationCenter.defaultCenter()
        _nc.addObserver_selector_name_object_(self,"itemAddedNotification:","added_object", _obj)
        _nc.addObserver_selector_name_object_(self,"itemDeletedNotification:","deleted_object", _obj)
     

    def viewDidEndLiveResize(self):
        super(CADView, self).viewDidEndLiveResize()
#        self.__image.removeFromSuperviewWithoutNeedingDisplay()
#        del self.__image
#        self.__image = None
#        self.setNeedsDisplay_(True)
        self.updateTrackingRect()
         
    def updateTrackingRect(self):
        """ Sets tracking rectangle over frame boundary to track mouse
        
updateTrackingRect()
        """
        _point = self.getMouseLocation()
        _vis = self.visibleRect()
        _flag = self.mouse_inRect_(_point, _vis)
        _rect = self.addTrackingRect_owner_userData_assumeInside_(_vis, self, 0, _flag)
        self.setTrackingRect(_rect)
        
    def mouseEntered_(self, event):
        """ NSView override to announce mouse entered CADView.  Use for location update.
        
mouseEntered_(event)
        """
        # fire timer every 0.1 sec to track mouse moves
        
        _timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(0.1, self, "updateMouseLocation:", 0, True)
        self.setMouseTimer(_timer)
    
    def mouseExited_(self, event):
        """ NSView override to announce mouse exited CADView.  Use for location update.

mouseExited_(event)
        """
        self.setMouseTimer(None)
        
    def mouseDown_(self, event):
        _doc = self.getDocument()
        _tool = _doc.getTool()
        if _tool is not None and _tool.hasHandler("left_button_press"):
            _handler = _tool.getHandler("left_button_press")
            _handler(_doc, event, _tool)

    def updateMouseLocation_(self, timer):
        """ timer callback that updates current mouse location in ImageDocument
        
updateMouseLocation_(timer):
        """
        _point = self.getMouseLocation()
        _doc = self.getDocument()
        _ox, _oy = _doc.getPoint()
        if (_ox == _point.x) and (_oy == _point.y):
            return
        _doc.setPoint(_point.x,_point.y)
        _tool = _doc.getTool()
        if _tool is not None and _tool.hasHandler("mouse_move"):
            _handler = _tool.getHandler("mouse_move")
            _handler(_doc, _point, _tool)
            _x = _y = _w = _h = None
            
            if isinstance(_tool, (PythonCAD.Generic.tools.TwoPointCircleTool,
                                  PythonCAD.Generic.tools.TangentCCircleTool,
                                  PythonCAD.Generic.tools.TwoPointTangentCCircleTool)):
                _r = _tool.getRadius()
                if _r is not None and _r > 0:
                    _cx, _cy = _tool.getCenter()
                    _w = _h = _r * 2.1
                    _x = _cx - _r * 1.05
                    _y = _cy - _r * 1.05
                else:
                    return
                    
            elif isinstance(_tool, PythonCAD.Generic.tools.ArcTool):
                _r = _tool.getRadius()
                if _r is not None and _r > 0:
                    _cx, _cy = _tool.getCenter()
                    _w = _h = _r * 2.1
                    _x = _cx - _r * 1.05
                    _y = _cy - _r * 1.05
                              
            elif isinstance(_tool, PythonCAD.Generic.tools.CircleTool):
                _r = hypot((self.__temporaryPoint.x - _point.x), (self.__temporaryPoint.y - _point.y))
                _w = _h = _r * 2.1
                _x = self.__temporaryPoint.x - _r * 1.05
                _y = self.__temporaryPoint.y - _r * 1.05
                
            elif isinstance(_tool, PythonCAD.Generic.tools.CCircleTangentLineTool):
                _tanpts = _tool.getTangentPoints()
                _tanrect = NSMakeRect(0,0,0,0)
                for _set in _tanpts:
                    _x1, _y1, _x2, _y2 = _set
                    _wt = abs(_x2 - _x1) * 1.06
                    _ht = abs(_y2 - _y1) * 1.06
                    _xt = min(_x1, _x2) - _wt * 0.03
                    _yt = min(_y1, _y2) - _ht * 0.03
                    _setrect = NSMakeRect(_xt, _yt, _wt, _ht)
                    _tanrect = NSUnionRect(_tanrect, _setrect)
                _x = NSMinX(_tanrect)
                _y = NSMinY(_tanrect)
                _w = NSWidth(_tanrect)
                _h = NSHeight(_tanrect) 
                
            elif isinstance(_tool, PythonCAD.Generic.tools.PolygonTool):
                _count = _tool.getSideCount()
                (_xc, _yc) = _tool.getCoord(0)
                _x = _xmax = _xc
                _y = _ymax = _yc
                for _i in range(1, _count):
                    (_xc, _yc) = _tool.getCoord(_i)
                    _x = min(_x, _xc)
                    _xmax = max(_xmax, _xc)
                    _y = min(_y, _yc)
                    _ymax = max(_ymax, _yc)
                _w = abs(_xmax - _x) * 1.06
                _h = abs(_ymax - _y) * 1.06
                _x = _x - _w*0.03
                _y = _y - _h*0.03
                
            elif isinstance(_tool, PythonCAD.Generic.tools.TextTool):
                _x = _point.x
                _y = _point.y
                _vis = self.visibleRect()
                _w = NSWidth(_vis)/10.0
                _h = NSHeight(_vis)/10.0

            elif isinstance(_tool, PythonCAD.Generic.tools.AngularDimensionTool):
                _l1, _fp = _tool.getFirstPoint()
                _l2, _sp = _tool.getSecondPoint()
                if (_fp is not None) and (_sp is not None):
                    _l, _vp = _tool.getVertexPoint()
                    _vx, _vy = _vp.getCoords()
                    _rad = hypot((_vx - _point.x), (_vy - _point.y))
                    _dim = _tool.getDimension()
                    _bar1, _bar2 = _dim.getDimBars()
                    _ep1, _ep2 = _bar1.getEndpoints()
                    _ep3, _ep4 = _bar2.getEndpoints()
                    _x1, _y1 = _ep1
                    _x2, _y2 = _ep2
                    _x3, _y3 = _ep3
                    _x4, _y4 = _ep4
                    _x5 = _vx - _rad
                    _x6 = _vx + _rad
                    _y5 = _vy - _rad
                    _y6 = _vy + _rad
                    _xmax = max(_x1, _x2, _x3, _x4, _x5, _x6, _point.x) 
                    _ymax = max(_y1, _y2, _y3, _y4, _y5, _y6, _point.y) 
                    _xmin = min(_x1, _x2, _x3, _x4, _x5, _x6, _point.x) 
                    _ymin = min(_y1, _y2, _y3, _y4, _y5, _y6, _point.y)
                    _w = abs(_xmax - _xmin) * 1.1
                    _h = abs(_ymax - _ymin) * 1.1
                    _x = _xmin - _w * 0.05
                    _y = _ymin - _h * 0.05
                    
            
            elif isinstance(_tool, PythonCAD.Generic.tools.LinearDimensionTool):
                _l1, _p1 = _tool.getFirstPoint()
                _l2, _p2 = _tool.getSecondPoint()
                if _p1 is not None and _p2 is not None:
                    _dim = _tool.getDimension()
                    _bar1, _bar2 = _dim.getDimBars()
                    _crossbar = _dim.getDimCrossbar()
                    #
                    # draw dimension lines
                    #
                    _ep1, _ep2 = _bar1.getEndpoints()
                    _ep3, _ep4 = _bar2.getEndpoints()
                    _ep5, _ep6 = _crossbar.getEndpoints()
                    _x1, _y1 = _ep1
                    _x2, _y2 = _ep2
                    _x3, _y3 = _ep3
                    _x4, _y4 = _ep4
                    _x5, _y5 = _ep5
                    _x6, _y6 = _ep6
                    _xmax = max(_x1, _x2, _x3, _x4, _x5, _x6, _point.x) 
                    _ymax = max(_y1, _y2, _y3, _y4, _y5, _y6, _point.y) 
                    _xmin = min(_x1, _x2, _x3, _x4, _x5, _x6, _point.x) 
                    _ymin = min(_y1, _y2, _y3, _y4, _y5, _y6, _point.y)
                    _w = abs(_xmax - _xmin) * 1.1
                    _h = abs(_ymax - _ymin) * 1.1
                    if (_w < 50):
                        _w = 50
                    if (_h < 30):
                        _h = 30
                    _x = _xmin - _w * 0.05
                    _y = _ymin - _h * 0.05
                    
            elif isinstance(_tool, PythonCAD.Generic.tools.RadialDimensionTool):
                _rdim = _tool.getDimension()
                _cb = _rdim.getDimCrossbar()
                _ep1, _ep2 = _cb.getEndpoints()
                _x1, _y1 = _ep1
                _x2, _y2 = _ep2
                _xmax = max(_x1, _x2, _point.x)
                _ymax = max(_y1, _y2, _point.y)
                _xmin = min(_x1, _x2, _point.x)
                _ymin = min(_y1, _y2, _point.y)
                _w = abs(_xmax - _xmin) * 1.2
                _h = abs(_ymax - _ymin) * 1.2
                if (_w < 50):
                    _w = 50
                if (_h < 30):
                    _h = 30
                _x = _xmin - _w * 0.15
                _y = _ymin - _h * 0.15
             
                   
                
            if (_x is None) or (_y is None) or (_w is None) or (_h is None): 
                _w = abs(_point.x - self.__temporaryPoint.x) * 1.06
                _h = abs(_point.y - self.__temporaryPoint.y) * 1.06
                _x = min(_point.x, self.__temporaryPoint.x) - _w * 0.03
                _y = min(_point.y, self.__temporaryPoint.y) - _h * 0.03
            _rect = NSMakeRect(_x, _y, _w, _h)
            _trect = self._getTempRect()
            self.setNeedsDisplayInRect_(_trect)
            self.setNeedsDisplayInRect_(_rect)
            self._setTempRect(_rect)
 
    def getMouseLocation(self):
        """ Finds mouse location in view
        
getMouseLocation()

This function returns an NSPoint corresponding to
mouse location in view's coordinate system.
        """
        _mouseLoc = self.window().mouseLocationOutsideOfEventStream()
        return self.convertPoint_fromView_(_mouseLoc, None)

    def fitImage(self):
        """Redraw the image so all entities are visible in the window.

fitImage()        
        """
        _clipView = self.enclosingScrollView().contentView()
        _conRect = _clipView.documentRect()
        _doc = self.getDocument()
        _xmin, _ymin, _xmax, _ymax = _doc.getImage().getExtents()
        _xdiff = abs(_xmax - _xmin) * 1.05
        _ydiff = abs(_ymax - _ymin) * 1.05
        _xs = _xdiff / NSWidth(_conRect) 
        _ys = _ydiff / NSHeight(_conRect)
        _xmid = (_xmin + _xmax) * 0.5
        _ymid = (_ymin + _ymax) * 0.5
        if _xs > _ys:
            _width = _xdiff
            _height = NSHeight(_conRect) * _xs
        else:
            _height = _ydiff
            _width = NSWidth(_conRect) * _ys
        _nx = _xmid - _width * 0.5
        _ny = _ymid - _height * 0.5
        self.zoomToRect(((_nx, _ny), (_width, _height)))
        
    def zoomToRect(self, rect):
        _clipView = self.enclosingScrollView().contentView()
        (_nx, _ny), (_nw, _nh) = rect
        (_cx, _cy), (_cw, _ch) = _clipView.frame()
        (_fx, _fy), (_fw, _fh) = self.frame()
        (_vx, _vy), (_vw, _vh) = self.visibleRect()
        _wzoom = _vw / _nw
        _hzoom = _vh / _nh
        _zoom = min(_wzoom, _hzoom)
        _nfw = _fw * _zoom
        _nfh = _fh * _zoom
        if _nfw < _cw or _nfh < _ch:
            _nfw = _cw
            _nfh = _ch
        self.setFrameSize_((_nfw, _nfh))
        (_bx, _by), (_bw, _bh) = self.bounds()
        self.setBoundsSize_((_bw / _zoom, _bh / _zoom))
        self.scrollRectToVisible_(rect)
        self.setNeedsDisplay_(True)
  
        
    def drawRect_(self, rect):
        """ NSView override to draw image in view
        
drawRect(rect)

Drawing view clipped to passed in NSRect "rect"
        """
        _doc = self.getDocument()
        _gc = NSGraphicsContext.currentContext()
        _gc.setShouldAntialias_(False)            
        self._drawBackground(_doc, rect)
        _active_layer = _doc.getImage().getActiveLayer()
        _layers = []
        _layers.append(_doc.getImage().getTopLayer())
        while (len(_layers)):
            _layer = _layers.pop()
            if _layer is not _active_layer and _layer.isVisible():
                self._drawLayer(_doc, _layer, rect)
            if _layer.hasSublayers():
                _layers.extend(_layer.getSublayers())
        if _active_layer.isVisible():
            self._drawLayer(_doc, _active_layer, rect)
            
    def _drawBackground(self, doc, rect):
        """ draws background color of ImageDocument doc in NSRect rect
        
_drawBackground(doc, rect)
        """
        _color = doc.getOption('BACKGROUND_COLOR')
        _nscolor = self.getNSColor(_color)
        _nscolor.set()
        NSRectFill(rect)
        
    def _drawLayer(self, doc, layer, rect):
        """ draws Layer "layer" of ImageDocument "doc" in NSRect "rect"
        
_drawLayer(doc, layer, rect)
        """
        _size = self.pointSize()
        _bigRect = NSInsetRect(rect, -_size.width, -_size.height)
        (_xmin, _ymin, _xmax, _ymax) = self.rectToCoordTransform(_bigRect)
        _objs = layer.objsInRegion(_xmin, _ymin, _xmax, _ymax)
        _active_layer = doc.getImage().getActiveLayer()
        if _active_layer is layer:
            active = True
            _tempObj = self._getTempObject()
            if len(_tempObj) > 0:
                for _obj in _tempObj:
                    _objs.append(_obj)
        else:
            active = False

        _conobjs = []
        _vobjs = []
        _pts = []

        for _obj in _objs:
            if isinstance(_obj, PythonCAD.Generic.conobject.ConstructionObject):
                _conobjs.append(_obj)
            elif isinstance(_obj, PythonCAD.Generic.point.Point):
                _pts.append(_obj)
            else:
                _vobjs.append(_obj)
        
        _bounds = self.bounds()
        self._drawConstructionObjects(_conobjs, _bounds, active)
        if doc.getOption('HIGHLIGHT_POINTS'):
            self._drawPoints(_pts, _bounds)
        self._drawObjects(_vobjs, _bounds, active)
                
        
    def _drawConstructionObjects(self, objs, rect, active):
        #
        # style bits are the same for all construction objects, so all
        # in the same bezier path
        #
        _constyle = PythonCAD.Generic.conobject.ConstructionObject._ConstructionObject__defstyle
        _dashArray = _constyle.getLinetype().getList()
        if _dashArray is None:
            _dashArray = [2, 2]
        _scaledArray = []
        for _num in _dashArray:
            _scaledArray.append(_num*self.__x_scale)
        _path = NSBezierPath.bezierPath()
        _path.setLineDash_count_phase_(_scaledArray, len(_scaledArray), 0.0)
        _path.setLineCapStyle_(NSButtLineCapStyle)
        _path.setLineJoinStyle_(NSMiterLineJoinStyle)
        _path.setLineWidth_(0.0)
        if active:
            _color = _constyle.getColor()
        else:
            _color = self.getDocument().getOption('INACTIVE_LAYER_COLOR')
        self.getNSColor(_color).set()
        (_xmin, _ymin, _xmax, _ymax) = self.rectToCoordTransform(rect)
        for _obj in objs:
            if isinstance(_obj, PythonCAD.Generic.hcline.HCLine):
                _x, _y = _obj.getLocation().getCoords()
                _tp = self.nudgePoint(rect, NSMakePoint(_x, _y))
                _point = NSMakePoint(_xmin, _tp.y)
                _path.moveToPoint_(_point)
                _point = NSMakePoint(_xmax, _tp.y)
                _path.lineToPoint_(_point)
            elif isinstance(_obj, PythonCAD.Generic.vcline.VCLine):
                _x, _y = _obj.getLocation().getCoords()
                _tp = self.nudgePoint(rect, NSMakePoint(_x, _y))
                _point = NSMakePoint(_tp.x, _ymin)
                _path.moveToPoint_(_point)
                _point = NSMakePoint(_tp.x, _ymax)
                _path.lineToPoint_(_point)
            elif isinstance(_obj, PythonCAD.Generic.acline.ACLine):
                _coords = _obj.clipToRegion(_xmin, _ymin, _xmax, _ymax)
                if _coords is not None:
                    _x1, _y1, _x2, _y2 = _coords
                    _tp1 = self.nudgePoint(rect, NSMakePoint(_x1, _y1))
                    _tp2 = self.nudgePoint(rect, NSMakePoint(_x2, _y2))
                    _path.moveToPoint_(_tp1)
                    _path.lineToPoint_(_tp2)
            elif isinstance(_obj, PythonCAD.Generic.cline.CLine):
                _coords = _obj.clipToRegion(_xmin, _ymin, _xmax, _ymax)
                if _coords is not None:
                    _x1, _y1, _x2, _y2 = _coords
                    _tp1 = self.nudgePoint(rect, NSMakePoint(_x1, _y1))
                    _tp2 = self.nudgePoint(rect, NSMakePoint(_x2, _y2))
                    _path.moveToPoint_(_tp1)
                    _path.lineToPoint_(_tp2)
            elif isinstance(_obj, PythonCAD.Generic.ccircle.CCircle):
                _x, _y = _obj.getCenter().getCoords()
                _radius = _obj.getRadius()
                _tp = self.nudgePoint(rect, NSMakePoint(_x - _radius, _y - _radius))
                _rect = NSMakeRect(_tp.x, _tp.y, _radius*2.0, _radius*2.0)
                _path.appendBezierPathWithOvalInRect_(_rect)
            else:
                pass
        _path.stroke()
       
    def _drawPoints(self, pts, rect):
        _ptSize = self.pointSize()
        _xcorr = _ptSize.width * 0.5
        _ycorr = _ptSize.height * 0.5
        _pathSingle = NSBezierPath.bezierPath()
        _pathSingle.setLineCapStyle_(NSButtLineCapStyle)
        _pathSingle.setLineJoinStyle_(NSMiterLineJoinStyle)
        _pathSingle.setLineWidth_(0.0)
        _pathMulti = _pathSingle.copyWithZone_(None)
        for _pt in pts:
            _users = _pt.getUsers()
            _path = _pathSingle
            if len(_users) > 1:
                _nd = 0
                for _uref in _users:
                    _user = _uref()
                    if not isinstance(_user, PythonCAD.Generic.dimension.Dimension):
                        _nd = _nd + 1
                    if _nd > 1:
                        _path = _pathMulti
                        break
            _orig = NSMakePoint(_pt.x - _xcorr, _pt.y - _ycorr)
            _orig = self.nudgePoint(rect, _orig)
            _path.appendBezierPathWithRect_(NSMakeRect(_orig.x, _orig.y, _ptSize.width, _ptSize.height))
        _color =  self.getDocument().getOption('SINGLE_POINT_COLOR')
        self.getNSColor(_color).set()
        _pathSingle.stroke()    
        _color =  self.getDocument().getOption('MULTI_POINT_COLOR')
        self.getNSColor(_color).set()
        _pathMulti.stroke()
               
    def _drawObjects(self, objs, rect, active):
        #
        # set default color if inactive
        #
        if not active:
            _color = self.getDocument().getOption('INACTIVE_LAYER_COLOR')
            self.getNSColor(_color).set()
        (_xmin, _ymin, _xmax, _ymax) = self.rectToCoordTransform(rect)

        #
        # iterate through items & draw
        #
        for _obj in objs:
            if (isinstance(_obj, PythonCAD.Generic.graphicobject.GraphicObject) or
                isinstance(_obj, PythonCAD.Generic.graphicobject.old_GraphicObject)):
                #
                # setup path
                #
                _path = NSBezierPath.bezierPath()
                #
                # line type
                #
                _dashList = _obj.getLinetype().getList()
                if _dashList is None:
                    _dashList = [1]
                _scaledList = []
                for _num in _dashList:
                    _scaledList.append(_num*self.__x_scale)
                _path.setLineDash_count_phase_(_scaledList, len(_scaledList), 0.0)
                #
                # line color
                #
                if active:
                    _color = _obj.getColor()
                    self.getNSColor(_color).set()
                #
                # line thickness, cap, join
                #
                _path.setLineWidth_(_obj.getThickness())
                _path.setLineJoinStyle_(NSMiterLineJoinStyle)
                _path.setLineCapStyle_(NSRoundLineCapStyle)
                #
                # items
                #
                if isinstance(_obj, PythonCAD.Generic.segment.Segment):
                    _coords = _obj.clipToRegion(_xmin, _ymin, _xmax, _ymax)
                    if _coords is not None:
                        _x1, _y1, _x2, _y2 = _coords
                        _tp1 = self.nudgePoint(rect, NSMakePoint(_x1, _y1))
                        _tp2 = self.nudgePoint(rect, NSMakePoint(_x2, _y2))
                        _path.moveToPoint_(_tp1)
                        _path.lineToPoint_(_tp2)
                        _path.stroke()
                elif isinstance(_obj, PythonCAD.Generic.arc.Arc):
                    _x, _y = _obj.getCenter().getCoords()
                    _point = self.nudgePoint(rect, NSMakePoint(_x, _y))
                    _r = _obj.getRadius()
                    _sa = _obj.getStartAngle()
                    _ea = _obj.getEndAngle()
                    _path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(_point, _r, _sa, _ea, False)
                    _path.stroke()
                elif isinstance(_obj, PythonCAD.Generic.circle.Circle):
                    _x, _y = _obj.getCenter().getCoords()
                    _radius = _obj.getRadius()
                    _tp = self.nudgePoint(rect, NSMakePoint(_x - _radius, _y - _radius))
                    _rect = NSMakeRect(_tp.x, _tp.y, _radius*2.0, _radius*2.0)
                    _path.appendBezierPathWithOvalInRect_(_rect)
                    _path.stroke()
                elif isinstance(_obj, PythonCAD.Generic.segjoint.Chamfer):
                    _p1, _p2 = _obj.getMovingPoints()
                    _tp1 = self.nudgePoint(rect, NSMakePoint(_p1.x, _p1.y))
                    _tp2 = self.nudgePoint(rect, NSMakePoint(_p2.x, _p2.y))
                    _path.moveToPoint_(_tp1)
                    _path.lineToPoint_(_tp2)
                    _path.stroke()                  
                elif isinstance(_obj, PythonCAD.Generic.segjoint.Fillet):
                    _x, _y = _obj.getCenter()
                    _p = self.nudgePoint(rect, NSMakePoint(_x, _y))
                    _r = _obj.getRadius()
                    _sa, _ea = _obj.getAngles()
                    _path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(_p, _r, _sa, _ea, False)
                    _path.stroke()
                  
                elif isinstance(_obj, PythonCAD.Generic.leader.Leader):
                    _p1, _p2, _p3 = _obj.getPoints()
                    _tp1 = self.nudgePoint(rect, NSMakePoint(_p1.x, _p1.y))
                    _tp2 = self.nudgePoint(rect, NSMakePoint(_p2.x, _p2.y))
                    _tp3 = self.nudgePoint(rect, NSMakePoint(_p3.x, _p3.y))
                    _path.moveToPoint_(_tp1)
                    _path.lineToPoint_(_tp2)
                    _path.lineToPoint_(_tp3)
                    _path.stroke()
                    _path.removeAllPoints()
                    _apts = _obj.getArrowPoints()
                    _ap1 = self.nudgePoint(rect, NSMakePoint(_apts[0], _apts[1]))
                    _ap2 = self.nudgePoint(rect, NSMakePoint(_apts[2], _apts[3]))
                    _path.moveToPoint_(_tp3)
                    _path.lineToPoint_(_ap1)
                    _path.lineToPoint_(_ap2)
                    _path.closePath()
                    _path.stroke()
                    _path.fill()
                    
                elif isinstance(_obj, PythonCAD.Generic.polyline.Polyline):
                    for _pt in _obj.getPoints():
                        _x, _y = _pt.getCoords()
                        _point = self.nudgePoint(rect, NSMakePoint(_x, _y))
                        try:
                            _path.lineToPoint_(_point)
                        except: # catches first point
                            _path.moveToPoint_(_point)
                    _path.stroke()
            elif isinstance(_obj, PythonCAD.Generic.text.TextBlock):
                self._drawText(_obj, rect)
            elif isinstance(_obj, PythonCAD.Generic.dimension.HorizontalDimension):
                self._drawLinearDimension(_obj, rect, active)
            elif isinstance(_obj, PythonCAD.Generic.dimension.VerticalDimension):
                self._drawLinearDimension(_obj, rect, active)
            elif isinstance(_obj, PythonCAD.Generic.dimension.LinearDimension):
                self._drawLinearDimension(_obj, rect, active)
            elif isinstance(_obj, PythonCAD.Generic.dimension.RadialDimension):
                self._drawRadialDimension(_obj, rect, active)
            elif isinstance(_obj, PythonCAD.Generic.dimension.AngularDimension):
                self._drawAngularDimension(_obj, rect, active)
            else:
                pass
                       
    def _drawLinearDimension(self, dim, rect, active):
        _path = NSBezierPath.bezierPath()
        _path.setLineWidth_(0)
        _path.setLineJoinStyle_(NSMiterLineJoinStyle)
        _path.setLineCapStyle_(NSButtLineCapStyle)
        if active:
            _color = dim.getColor()
            self.getNSColor(_color).set()
        if dim.isModified():
            dim.calcDimValues()
            dim.reset()
        _bar1, _bar2 = dim.getDimBars()
        _crossbar = dim.getDimCrossbar()
        #
        # draw dimension lines
        #
        _ep1, _ep2 = _bar1.getEndpoints()
        _tp1 = self.nudgePoint(rect, NSMakePoint(_ep1[0], _ep1[1]))
        _tp2 = self.nudgePoint(rect, NSMakePoint(_ep2[0], _ep2[1]))
        _path.moveToPoint_(_tp1)
        _path.lineToPoint_(_tp2)
        _ep1, _ep2 = _bar2.getEndpoints()
        _tp1 = self.nudgePoint(rect, NSMakePoint(_ep1[0], _ep1[1]))
        _tp2 = self.nudgePoint(rect, NSMakePoint(_ep2[0], _ep2[1]))
        _path.moveToPoint_(_tp1)
        _path.lineToPoint_(_tp2)
        _ep1, _ep2 = _crossbar.getEndpoints()
        _tp1 = self.nudgePoint(rect, NSMakePoint(_ep1[0], _ep1[1]))
        _tp2 = self.nudgePoint(rect, NSMakePoint(_ep2[0], _ep2[1]))
        _path.moveToPoint_(_tp1)
        _path.lineToPoint_(_tp2)
        _path.stroke()
        #
        # draw endpoints
        #
        _mpts = _crossbar.getCrossbarPoints()
        _mp = _mpts[0]
        _mp1 = NSMakePoint(_mp[0], _mp[1])
        _mp = _mpts[1]
        _mp2 = NSMakePoint(_mp[0], _mp[1])
        _etype = dim.getEndpointType()
        if (_etype == PythonCAD.Generic.dimension.Dimension.ARROW or
            _etype == PythonCAD.Generic.dimension.Dimension.FILLED_ARROW or
            _etype == PythonCAD.Generic.dimension.Dimension.SLASH):
            _epts = _crossbar.getMarkerPoints()
            assert len(_epts) == 4, "Bad marker point count: %d" % len(_epts)
            self._drawLineEndpoints(_etype, _epts[0:2], _mp1)
            self._drawLineEndpoints(_etype, _epts[2:4], _mp2)
                    
        elif _etype == PythonCAD.Generic.dimension.Dimension.CIRCLE:
            _size = dim.getEndpointSize()
            self._drawCircleEndpoints(_mp1, _size)
            self._drawCircleEndpoints(_mp2, _size)
            
        else:
            pass
            
        self._drawDimensionText(dim)
            
                
    def _drawRadialDimension(self, dim, rect, active):
        _path = NSBezierPath.bezierPath()
        _path.setLineWidth_(0)
        _path.setLineJoinStyle_(NSMiterLineJoinStyle)
        _path.setLineCapStyle_(NSButtLineCapStyle)
        if active:
            _color = dim.getColor()
            self.getNSColor(_color).set()
        if dim.isModified():
            dim.calcDimValues()
            dim.reset()
        #
        # draw line
        #
        _crossbar = dim.getDimCrossbar()
        _ep1, _ep2 = _crossbar.getEndpoints()
        _tp1 = self.nudgePoint(rect, NSMakePoint(_ep1[0], _ep1[1]))
        _tp2 = self.nudgePoint(rect, NSMakePoint(_ep2[0], _ep2[1]))
        _path.moveToPoint_(_tp1)
        _path.lineToPoint_(_tp2)
        _path.stroke()
        #
        # draw endpoints
        #
        _p1, _p2 = _crossbar.getCrossbarPoints()
        _mp1 = NSMakePoint(_p1[0], _p1[1])
        _mp2 = NSMakePoint(_p2[0], _p2[1])
        _etype = dim.getEndpointType()
        _dia_mode = dim.getDiaMode()
        if (_etype == PythonCAD.Generic.dimension.Dimension.ARROW or
            _etype == PythonCAD.Generic.dimension.Dimension.FILLED_ARROW or
            _etype == PythonCAD.Generic.dimension.Dimension.SLASH):
            _epts = _crossbar.getMarkerPoints()
            assert len(_epts) == 4, "Unexpect endpoint length: %d" % len(_epts)
            if _dia_mode:
                self._drawLineEndpoints(_etype, _epts[0:2], _mp1)
            self._drawLineEndpoints(_etype, _epts[2:4], _mp2)

        elif _etype == PythonCAD.Generic.dimension.Dimension.CIRCLE:
            _size = dim.getEndpointSize()
            if _dia_mode:
                self._drawCircleEndpoints(_mp1, _size)
            self._drawCircleEndpoints(_mp2, _size)
        
        else:
            pass 

        self._drawDimensionText(dim)
        
            
    def _drawAngularDimension(self, dim, rect, active):
        _path = NSBezierPath.bezierPath()
        _path.setLineWidth_(0)
        _path.setLineJoinStyle_(NSMiterLineJoinStyle)
        _path.setLineCapStyle_(NSButtLineCapStyle)
        if active:
            _color = dim.getColor()
            self.getNSColor(_color).set()
        if dim.isModified():
            dim.calcDimValues()
            dim.reset()
        _bar1, _bar2 = dim.getDimBars()
        _crossarc = dim.getDimCrossarc()
        #
        # draw dimension lines
        #
        _ep1, _ep2 = _bar1.getEndpoints()
        _tp1 = self.nudgePoint(rect, NSMakePoint(_ep1[0], _ep1[1]))
        _tp2 = self.nudgePoint(rect, NSMakePoint(_ep2[0], _ep2[1]))
        _path.moveToPoint_(_tp1)
        _path.lineToPoint_(_tp2)
        _ep1, _ep2 = _bar2.getEndpoints()
        _tp1 = self.nudgePoint(rect, NSMakePoint(_ep1[0], _ep1[1]))
        _tp2 = self.nudgePoint(rect, NSMakePoint(_ep2[0], _ep2[1]))
        _path.moveToPoint_(_tp1)
        _path.lineToPoint_(_tp2)
        _path.stroke()
        _path.removeAllPoints()
        #
        # draw dimension arc
        #
        _vx, _vy = dim.getVertexPoint().getCoords()
        _sa = _crossarc.getStartAngle()
        _ea = _crossarc.getEndAngle()
        _rad = _crossarc.getRadius()
        _point = self.nudgePoint(rect, NSMakePoint(_vx, _vy))
        _path.appendBezierPathWithArcWithCenter_radius_startAngle_endAngle_clockwise_(_point, _rad, _sa, _ea, False)
        _path.stroke()
        #
        # draw endpoints
        #
        _p1, _p2 = _crossarc.getCrossbarPoints()
        _mp1 = NSMakePoint(_p1[0], _p1[1])
        _mp2 = NSMakePoint(_p2[0], _p2[1])
        _etype = dim.getEndpointType()
        if (_etype == PythonCAD.Generic.dimension.Dimension.ARROW or
            _etype == PythonCAD.Generic.dimension.Dimension.FILLED_ARROW or
            _etype == PythonCAD.Generic.dimension.Dimension.SLASH):
            _epts = _crossarc.getMarkerPoints()
            assert len(_epts) == 4, "Unexpect endpoint length: %d" % len(_epts)
            self._drawLineEndpoints(_etype, _epts[0:2], _mp1)
            self._drawLineEndpoints(_etype, _epts[2:4], _mp2)
        elif _etype == PythonCAD.Generic.dimension.Dimension.CIRCLE:
            _size = dim.getEndpointSize()
            self._drawCircleEndpoints(_mp1, _size)
            self._drawCircleEndpoints(_mp2, _size)
        else:
            pass 

        self._drawDimensionText(dim)
                                     
           
    def _drawCircleEndpoints(self, mp, size):         
            _path = NSBezierPath.bezierPath()
            _path.setLineWidth_(0)
            _path.setLineJoinStyle_(NSMiterLineJoinStyle)
            _path.setLineCapStyle_(NSButtLineCapStyle)
            _rad = size * 0.5
            _rect = NSMakeRect(mp.x - _rad , mp.y - _rad, size, size)
            _path.appendBezierPathWithOvalInRect_(_rect)
            _path.stroke()
            _path.fill()
      
    def _drawLineEndpoints(self, etype, ep, mp):
            _path = NSBezierPath.bezierPath()
            _path.setLineWidth_(0)
            _path.setLineJoinStyle_(NSMiterLineJoinStyle)
            _path.setLineCapStyle_(NSButtLineCapStyle)                
            if etype == PythonCAD.Generic.dimension.Dimension.ARROW:
                    for _i in range(2):
                        _ep = ep[_i]
                        _tep = NSMakePoint(_ep[0], _ep[1])
                        _path.moveToPoint_(_tep)
                        _path.lineToPoint_(mp)
            elif etype == PythonCAD.Generic.dimension.Dimension.FILLED_ARROW:
                    _ep = ep[0]
                    _tep = NSMakePoint(_ep[0], _ep[1])
                    _path.moveToPoint_(_tep)
                    _ep = ep[1]
                    _tep = NSMakePoint(_ep[0], _ep[1])
                    _path.lineToPoint_(_tep)
                    _path.lineToPoint_(mp)
                    _path.closePath()
            elif etype == PythonCAD.Generic.dimension.Dimension.SLASH:
                    _ep = ep[0]
                    _tep = NSMakePoint(_ep[0], _ep[1])
                    _path.moveToPoint_(_tep)
                    _ep = ep[1]
                    _tep = NSMakePoint(_ep[0], _ep[1])
                    _path.lineToPoint_(_tep)               
            else:
                pass
            _path.stroke()
            _path.fill()
                            
    
    def _drawText(self, obj, rect):
        _gc = NSGraphicsContext.currentContext()
        _gc.setShouldAntialias_(True)
        _attrs = self.formatDictionary(obj, False)
        _x, _y = obj.getLocation()
        _point = self.nudgePoint(rect, NSMakePoint(_x, _y))
        _font = _attrs[NSFontAttributeName]
        _lineHeight = _font.defaultLineHeightForFont()
        _text = obj.getText().splitlines()
        for _str in _text:
            _as = NSAttributedString.alloc().initWithString_attributes_(_str, _attrs)
            _as.drawAtPoint_(_point)
            _point.y = _point.y - _lineHeight
        _gc.setShouldAntialias_(False)

    def _drawDimensionText(self, dim):
        _gc = NSGraphicsContext.currentContext()
        _gc.setShouldAntialias_(True)
        _x, _y = dim.getLocation()
        _dlen = dim.calculate()
        _hlen = self.getDocument().getImage().scaleLength(_dlen)
        _dims = dim.getDimensions(_hlen)
        _pds = dim.getPrimaryDimstring()
        _pdsAttr = self.formatDictionary(_pds, True)
        _dim1 = NSAttributedString.alloc().initWithString_attributes_(_dims[0], _pdsAttr)
        _dim1Size = _dim1.size()
        _dual_mode = dim.getDualDimMode()
        if _dual_mode:
            _sds = dim.getSecondaryDimstring()
            _sdsAttr = self.formatDictionary(_sds, True)
            _dim2 = NSAttributedString.alloc().initWithString_attributes_(_dims[1], _sdsAttr)
            _dim2Size = _dim2.size()
            _width = max(_dim1Size.width, _dim2Size.width) * 0.5
            # sep line & fill
            _gc.saveGraphicsState()
            _ngc = NSGraphicsContext.currentContext()
            _color = self.getDocument().getOption('BACKGROUND_COLOR')
            self.getNSColor(_color).set()
            NSRectFill(NSMakeRect((_x - _width), (_y - 2), _width * 2.0, 5))
            _ngc.restoreGraphicsState()
            _path = NSBezierPath.bezierPath()
            _path.setLineWidth_(0)
            _point = NSMakePoint((_x - _width), _y)
            _path.moveToPoint_(_point)
            _point = NSMakePoint((_x + _width), _y)
            _path.lineToPoint_(_point)
            _path.stroke()
            # prim dim
            _point = NSMakePoint((_x - _dim1Size.width * 0.5), (_y + 2)) # a little padding on the height
            _dim1.drawAtPoint_(_point)   
            # sec dim
            _point = NSMakePoint((_x - _dim2Size.width * 0.5), (_y - _dim2Size.height - 2))
            _dim2.drawAtPoint_(_point)
        else:
            _point = NSMakePoint((_x - _dim1Size.width*0.5), (_y - _dim1Size.height* 0.5))
            _dim1.drawAtPoint_(_point)
        _gc.setShouldAntialias_(False)
                 
    def pointSize(self):
        _defsize = NSMakeSize(10, 10)
        _size = self.getTransform().transformSize_(_defsize) 
        return _size

    
    def formatDictionary(self, style, db):
        """ returns attribute dictionary for NSAttributedString
        
formatDictionary(styleObj, drawsBackground):
        """
        _fm = NSFontManager.sharedFontManager()
        _family = style.getFamily()
        _style = style.getStyle()
        _weight = style.getWeight()
        _size = ceil(style.getSize() * self.__y_scale)
        if _size < 2:
            _size = 2
        _fontkey = str(_family)+str(_style)+str(_weight)+str(_size)
        if PythonCAD.Generic.globals.NSFonts.has_key(_fontkey):
            _font = PythonCAD.Generic.globals.NSFonts[_fontkey]
        else:
            _traits = 0
            if PythonCAD.Generic.text.TextStyle.FONT_ITALIC == _style:
                _traits = _traits | NSItalicFontMask
            if PythonCAD.Generic.text.TextStyle.WEIGHT_LIGHT == _weight:
                _weight = 3
            if PythonCAD.Generic.text.TextStyle.WEIGHT_NORMAL == _weight:
                _weight = 5
            elif PythonCAD.Generic.text.TextStyle.WEIGHT_BOLD == _weight:
                _weight = 9
            elif PythonCAD.Generic.text.TextStyle.WEIGHT_HEAVY == _weight:
                _weight = 11
            _font = _fm.fontWithFamily_traits_weight_size_(_family, _traits, _weight, _size)
            if _font is None:
                _font = NSFont.userFixedPitchFontOfSize_(_size)
                if PythonCAD.Generic.text.TextSTyle.FONT_ITALIC == _style:
                    _font = _fm.convertFont_toHaveTrait_(_font, NSItalicFontMask)
                if _weight > 5:
                    _font = _fm.convertWeight_ofFont_(True, _font)
                elif _weight < 5:
                    _font = _fm.convertWeight_ofFont_(False, _font)
            PythonCAD.Generic.globals.NSFonts[_fontkey] = _font
        _attrs = {}
        _attrs[NSFontAttributeName] = _font
        if _size < 4:
            _attrs[NSKernAttributeName] = 0.3
        _color = style.getColor()
        _attrs[NSForegroundColorAttributeName] = self.getNSColor(_color)
        if db:
            _color = self.getDocument().getOption('BACKGROUND_COLOR')
            _attrs[NSBackgroundColorAttributeName] = self.getNSColor(_color)
        return _attrs 
    
    
    def nudgePoint(self, rect, point):
        """ we give the points a nudge to get a single pixel line
        
nudgePoint(point)

Returns an NSPoint 
        """
        _nudge = self.__x_scale * 0.5
        _xoffset = round((point.x - rect.origin.x)/self.__x_scale)
        point.x = rect.origin.x + self.__x_scale*_xoffset + _nudge
        _nudge = self.__y_scale * 0.5
        _yoffset = round((point.y - rect.origin.y)/self.__y_scale)
        point.y = rect.origin.y + self.__y_scale*_yoffset + _nudge
        return point
       
    def translateSize(self, size):
        return self.__trans.transformSize_(size)
        
    def setTransform(self):
        _trans = NSAffineTransform.transform()
        _bounds = self.bounds()
        _frame = self.frame()
        _xs = _bounds.size.width / _frame.size.width
        _ys = _bounds.size.height / _frame.size.height
#        _xt = _bounds.origin.x * _xs
#        _yt = _bounds.origin.y * _ys
#        _trans.translateXBy_yBy_(_xt, _yt)
        _trans.scaleXBy_yBy_(_xs, _ys)
        self.__trans = _trans
        self.__x_scale = _xs
        self.__y_scale = _ys
        
    def getTransform(self):
        if self.__trans is None:
            self.setTransform()
        return self.__trans
        
 
    def rectToCoordTransform(self, rect):
        """ Converts NSRect rect into x-y coordinates of ImageDocument 
        
rectToCoordTransform(rect)

returns (xmin, ymin, xmax, ymax)
        """
        return (NSMinX(rect), NSMinY(rect), NSMaxX(rect), NSMaxY(rect))
        
    def getNSColor(self, color):
        """Retrieves an NSColor for a Color object.

getNSColor(color)

Argument "color" must be a Color object. This method returns an 
equivalent NSColor object, allocating it if necessary
        """
        if not isinstance(color, PythonCAD.Generic.color.Color):
            raise TypeError, "Invalid Color object: " + `color`
        if PythonCAD.Generic.globals.NSColors.has_key(color):
            _val = PythonCAD.Generic.globals.NSColors[color]
        else:
            (_r, _g, _b) = color.getColors()
            _val = NSColor.colorWithCalibratedRed_green_blue_alpha_(_r/255.0, _g/255.0, _b/255.0, 1.0)
            PythonCAD.Generic.globals.NSColors[color] = _val
        return _val
        

            

        
            
        
        
       

        
        
    
        
        
            
