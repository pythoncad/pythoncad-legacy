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
# Application Controller Object (& app delegate)
#
# P.L.V. nov 23 05
# import adjustment

from math import hypot, pi, atan2

import objc

import PythonCAD.Generic.tools
import PythonCAD.Interface.Cocoa.CocoaConobjs
import PythonCAD.Interface.Cocoa.CocoaEntities
import PythonCAD.Interface.Cocoa.CocoaModify
import PythonCAD.Interface.Cocoa.CocoaText
import PythonCAD.Interface.Cocoa.CocoaDimensions
from PyObjCTools import NibClassBuilder
from Foundation import *
from AppKit import NSDocumentController, NSSavePanel, NSOKButton, NSCancelButton, NSPanel, NSWindowController, NSApplication, NSTextView

#
# Define True & False if this is Python < 2.2.1
#
try:
    True, False
except NameError:
    True, False = 1, 0
    
ZOOM = 2.0
    

NibClassBuilder.extractClasses("MainMenu")

class AppController(NibClassBuilder.AutoBaseClass):
    """ PythonCad application menu controller
    
    
Passes menu commands to the appropriate handlers
    """

#
# File menu
#
    def saveLayerAs_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return  # this is odd
        _sp = NSSavePanel.savePanel()
        _sp.setTitle_("Save Layer")
        _sp.setRequiredFileType_("xml.gz")
        _layer = _doc.getImage().getActiveLayer()
        _win = _doc.windowForSheet()
        _name = _layer.getName()
        _sp.beginSheetForDirectory_file_modalForWindow_modalDelegate_didEndSelector_contextInfo_(None, _name, _win, self, "savePanelDidEnd:returnCode:contextInfo:", 0)
        
    def savePanelDidEnd_returnCode_contextInfo_(self, sp, code, info):
        if NSOKButton == code:
            print "wahoo, we're saving the layer!"
        elif NSCancelButton == code:
            print "funk that - don't save the layer"
            
         
    savePanelDidEnd_returnCode_contextInfo_ = objc.selector(savePanelDidEnd_returnCode_contextInfo_, signature="v@:@ii")

#
# Edit menu commands
#
    def undo_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _doc.getImage().undo()
        _doc.getDA().setNeedsDisplay_(True)
                        
    def redo_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _doc.getImage().redo()    
        _doc.getDA().setNeedsDisplay_(True)
#
# Draw Basic Menu commands
#
    def drawPoint_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.PointTool()
        _doc.setTool(_tool)
        CocoaEntities.point_mode_init(_doc, _tool)
            
    def drawRect_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.RectangleTool()
        _doc.setTool(_tool)
        CocoaEntities.rectangle_mode_init(_doc, _tool)
    
    def drawSegment_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.SegmentTool()
        _doc.setTool(_tool)
        CocoaEntities.segment_mode_init(_doc, _tool)
    
    def drawCircleCentered_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.CircleTool()
        _doc.setTool(_tool)
        CocoaEntities.circle_center_mode_init(_doc, _tool)
    
    def drawCircle2Point_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.TwoPointCircleTool()
        _doc.setTool(_tool)
        CocoaEntities.circle_tp_mode_init(_doc, _tool)

    def drawArc_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.ArcTool()
        _doc.setTool(_tool)
        CocoaEntities.arc_center_mode_init(_doc, _tool)

#
# Draw Construction Line commands
#
    def drawHCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.HCLineTool()
        _doc.setTool(_tool)
        CocoaConobjs.hcline_mode_init(_doc, _tool)

    def drawVCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.VCLineTool()
        _doc.setTool(_tool)
        CocoaConobjs.vcline_mode_init(_doc, _tool)

    def drawACLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.ACLineTool()
        _doc.setTool(_tool)
        CocoaConobjs.acline_mode_init(_doc, _tool)
    
    def drawParallelCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.ParallelOffsetTool()
        _doc.setTool(_tool)
        CocoaConobjs.cline_par_mode_init(_doc, _tool)

    def drawPerpendicularCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.Tool()
        _doc.setTool(_tool)
        CocoaConobjs.cline_perp_mode_init(_doc, _tool)

    def drawTanCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.Tool()
        _doc.setTool(_tool)
        CocoaConobjs.cline_tan_mode_init(_doc, _tool)
    
    def drawTan2CircleCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.CCircleTangentLineTool()
        _doc.setTool(_tool)
        CocoaConobjs.cline_tan_2circ_mode_init(_doc, _tool)

    def draw2PointCLine_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.CLineTool()
        _doc.setTool(_tool)
        CocoaConobjs.cline_tp_mode_init(_doc, _tool)

#
# Draw construction circle commands
#
    def drawCCircleCenter_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.CCircleTool()
        _doc.setTool(_tool)
        CocoaConobjs.ccircle_center_mode_init(_doc, _tool)
    
    def drawCCircle2Point_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.TwoPointCCircleTool()
        _doc.setTool(_tool)
        CocoaConobjs.ccircle_tp_mode_init(_doc, _tool)

    def drawCCircle1Tan_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.TangentCCircleTool()
        _doc.setTool(_tool)
        CocoaConobjs.ccircle_tan1_mode_init(_doc, _tool)

    def drawCCircle2Tan_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.TwoPointTangentCCircleTool()
        _doc.setTool(_tool)
        CocoaConobjs.ccircle_tan2_mode_init(_doc, _tool)
        
#
# Draw more complicated things commands
#
    def drawChamfer_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.Tool()
        _doc.setTool(_tool)
        CocoaEntities.chamfer_mode_init(_doc, _tool)

    def drawFillet_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.Tool()
        _doc.setTool(_tool)
        CocoaEntities.fillet_mode_init(_doc, _tool)

    def drawLeader_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.LeaderTool()
        _doc.setTool(_tool)
        CocoaEntities.leader_mode_init(_doc, _tool)

    def drawPolyline_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.PolylineTool()
        _doc.setTool(_tool)
        CocoaEntities.polyline_mode_init(_doc, _tool)

    def drawPolygon_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.PolygonTool()
        _doc.setTool(_tool)
        self.openPolygonPanel()
        CocoaEntities.polygon_mode_init(_doc, _tool)

    def drawPolygonExternal_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.PolygonTool()
        _tool.setExternal()
        _doc.setTool(_tool)
        self.openPolygonPanel()
        CocoaEntities.polygon_mode_init(_doc, _tool)

    def drawText_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _win = _doc.windowForSheet()
        _app = NSApplication.sharedApplication()
        _app.beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(self.textSheet, _win, None, None, 0)
        _tool = tools.TextTool()
        _doc.setTool(_tool)
        _textview = self.textSheet.initialFirstResponder()
        if isinstance(_textview, NSTextView):
            CocoaText.textview_format_setup(_doc, _textview)
        
    def drawTextSheetOK_(self, sender):
        _win = sender.window()
        _app = NSApplication.sharedApplication()
        _app.endSheet_(_win)
        _win.orderOut_(_win)
        _textview = _win.initialFirstResponder()
        if not isinstance(_textview, NSTextView):
            return
        _text = _textview.string()
        if not len(_text) > 0:
            return
        _doc = self.getCurrentDocument()
        _tool = _doc.getTool()
        if not isinstance(_tool, tools.TextTool):
            return
        _tool.setText(_text)
        CocoaText.text_entered(_doc, _tool, _textview)
    
    def drawTextSheetCancel_(self, sender):
        _win = sender.window()
        _app = NSApplication.sharedApplication()
        _app.endSheet_(_win)
        _win.orderOut_(_win)
        _textview = _win.initialFirstResponder()
        if not isinstance(_textview, NSTextView):
            return
        _textview.setString_("")

#
# Format menu 
#

#
# Modify menu
#
    def modifyMoveHorizontal_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.HorizontalMoveTool()
        _doc.setTool(_tool)
        CocoaModify.move_horizontal_init(_doc, _tool)

    def modifyMoveVertical_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.VerticalMoveTool()
        _doc.setTool(_tool)
        CocoaModify.move_vertical_init(_doc, _tool)

    def modifyMoveFree_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.MoveTool()
        _doc.setTool(_tool)
        CocoaModify.move_free_init(_doc, _tool)

    def modifyStretchHorizontal_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.HorizontalStretchTool()
        _doc.setTool(_tool)
        CocoaModify.stretch_horizontal_init(_doc, _tool)

    def modifyStretchVertical_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.VerticalStretchTool()
        _doc.setTool(_tool)
        CocoaModify.stretch_vertical_init(_doc, _tool)

    def modifyStretchFree_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.StretchTool()
        _doc.setTool(_tool)
        CocoaModify.stretch_free_init(_doc, _tool)

        
    def modifySplit_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.SplitTool()
        _doc.setTool(_tool)
        CocoaModify.split_init(_doc, _tool)
    
    def modifyMirror_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.MirrorTool()
        _doc.setTool(_tool)
        CocoaModify.mirror_init(_doc, _tool)
    
    def modifyTransfer_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.Tool()
        _doc.setTool(_tool)
        CocoaModify.transfer_init(_doc, _tool)

#
# Dimensions menu
#
    def dimensionLinear_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.LinearDimensionTool()
        _doc.setTool(_tool)
        CocoaDimensions.ldim_mode_init(_doc, _tool)
    
    def dimensionHorizontal_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.HorizontalDimensionTool()
        _doc.setTool(_tool)
        CocoaDimensions.ldim_mode_init(_doc, _tool)
   
    def dimensionVertical_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.VerticalDimensionTool()
        _doc.setTool(_tool)
        CocoaDimensions.ldim_mode_init(_doc, _tool)

    def dimensionRadial_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.RadialDimensionTool()
        _doc.setTool(_tool)
        CocoaDimensions.radial_mode_init(_doc, _tool)

    def dimensionAngular_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.AngularDimensionTool()
        _doc.setTool(_tool)
        CocoaDimensions.angular_mode_init(_doc, _tool)
#
# Window menu
#
    def windowZoom_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _tool = tools.RectangleTool()
        _doc.setTool(_tool)
        CocoaModify.zoom_mode_init(_doc, _tool)
        
    def windowZoomIn_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _da = _doc.getDA()
        _visRect = _da.visibleRect()
        _xinset = NSWidth(_visRect) / (ZOOM*2)
        _yinset = NSHeight(_visRect) / (ZOOM*2)
        _zoomRect = NSInsetRect(_visRect, _xinset, _yinset)
        _da.zoomToRect(_zoomRect)
        
    def windowZoomOut_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _da = _doc.getDA()
        _visRect = _da.visibleRect()
        _xinset = NSWidth(_visRect) / ZOOM
        _yinset = NSHeight(_visRect) / ZOOM
        _zoomRect = NSInsetRect(_visRect, -_xinset, -_yinset)
        _da.zoomToRect(_zoomRect)
    
    def windowZoomFit_(self, sender):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return
        _da = _doc.getDA()
        _da.fitImage()

#
# etc
#
    __polyPanelWindowController = None
    def openPolygonPanel(self):
        if self.__polyPanelWindowController is None:
            _wc = NSWindowController.alloc().initWithWindow_(self.polygonPanel)
            self.__polyPanelWindowController = _wc
        self.__polyPanelWindowController.showWindow_(self)
        
        
    def windowDidResignKey_(self, note):
        _win = note.object()
        if _win is self.polygonPanel:
            _doc = self.getCurrentDocument()
            if _doc is None:
                return
            _tool = _doc.getTool()
            if isinstance(_tool, tools.PolygonTool):
                _textField = _win.initialFirstResponder()
                _int = _textField.intValue()
                _tool.setSideCount(_int)
            
        
    def getCurrentDocument(self):
        _dc = NSDocumentController.sharedDocumentController()
        _doc = _dc.currentDocument()
        return _doc

    def validateMenuItem_(self, menuItem):
        _doc = self.getCurrentDocument()
        if _doc is None:
            return False
        _action = menuItem.action()
        _image = _doc.getImage()
        _layer = _image.getActiveLayer()
        # 
        # checks
        #
        if (_action == "undo:"):
            return _image.canUndo()
        
        elif (_action == "redo:"):
            return _image.canRedo()
        
        elif ((_action == "drawParallelCLine:") or
              (_action == "modifyMirror:")):
            _objs = _layer.getChildren()
            for _obj in _objs:
                if isinstance(_obj, (Generic.hcline.HCLine,
                                     Generic.vcline.VCLine,
                                     Generic.acline.ACLine,
                                     Generic.cline.CLine)):
                    return True
            return False
            
        elif (_action == "drawPerpendicularCLine:"):
            return _layer.hasChildren()
            
        elif (_action == "drawTanCLine:"):
            _circles = (_layer.getLayerEntities("circle") +
                        _layer.getLayerEntities("ccircle") +
                        _layer.getLayerEntities("arc"))
            if len(_circles) == 0:
                return False
            else:
                return True
                
        elif (_action == "drawTan2CircleCLine:"):
            _circles = _layer.getLayerEntities("ccircle")
            if len(_circles) < 2:
                return False
            return True
        
        elif (_action == "drawCCircle1Tan:"):
            _objs = _layer.getChildren()
            for _obj in _objs:
                if isinstance(_obj, Generic.conobject.ConstructionObject):
                    return True
            return False
        
        elif (_action == "drawCCircle2Tan:"):
            _ccircles = len(_layer.getLayerEntities("ccircle"))
            _cobjs = len(_layer.getLayerEntities("hcline") +
                      _layer.getLayerEntities("vcline") +
                      _layer.getLayerEntities("acline") +
                      _layer.getLayerEntities("cline"))
            if _cobjs == 0:
                return False
            elif (_ccircles + _cobjs) < 2:
                return False
            return True
            
        elif (_action == "modifyTransfer:"):
            _top = _image.getTopLayer()
            if len(_top.getSublayers()):
                return True
            return False
            
        elif (_action == "modifySplit:"):
            _objs = _layer.getChildren()
            for _obj in _objs:
                if isinstance(_obj, (Generic.segment.Segment,
                                     Generic.arc.Arc,
                                     Generic.circle.Circle,
                                     Generic.polyline.Polyline)):
                    return True
            return False
        
        return True


