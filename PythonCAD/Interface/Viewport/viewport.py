#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
# Copyright (c) 2009 Matteo Boscolo, Gertwin Groen
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

import math
import types
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

import cairo

#from PythonCAD.Generic.image import Image
#from PythonCAD.Generic.layer import Layer
#from PythonCAD.Interface.Entities.ipoint import IPoint
#from PythonCAD.Interface.Viewport.viewportdraw import ViewportDraw

from PythonCAD.Generic import point
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import segjoint
#from PythonCAD.Generic import conobject
from PythonCAD.Generic import hcline
from PythonCAD.Generic import vcline
from PythonCAD.Generic import acline
from PythonCAD.Generic import cline
from PythonCAD.Generic import ccircle
from PythonCAD.Generic import text
from PythonCAD.Generic import dimension
from PythonCAD.Generic.layer import Layer
from PythonCAD.Generic.color import Color
from PythonCAD.Generic.conobject import ConstructionObject

from PythonCAD.Generic.Tools import tools


# draw imports
from PythonCAD.Interface.Viewport.aclinedraw import _draw_acline, _erase_acline, _sample_acline
from PythonCAD.Interface.Viewport.arcdraw import _draw_arc, _erase_arc, _sample_arc
from PythonCAD.Interface.Viewport.circledraw import _draw_circle, _erase_circle, _sample_circle
from PythonCAD.Interface.Viewport.ccircledraw import _draw_ccircle,_erase_ccircle
from PythonCAD.Interface.Viewport.chamferdraw import _draw_chamfer, _erase_chamfer
from PythonCAD.Interface.Viewport.clinedraw import _draw_cline, _erase_cline
from PythonCAD.Interface.Viewport.dimdraw import _draw_ldim, _draw_rdim, _draw_adim, _draw_markers, _draw_dimstrings, _erase_dim
from PythonCAD.Interface.Viewport.filletdraw import _draw_fillet, _erase_fillet
from PythonCAD.Interface.Viewport.hclinedraw import _draw_hcline, _erase_hcline
from PythonCAD.Interface.Viewport.leaderdraw import _draw_leader, _erase_leader
from PythonCAD.Interface.Viewport.pointdraw import _draw_point, _erase_point
from PythonCAD.Interface.Viewport.polylinedraw import _draw_polyline, _erase_polyline, _sample_polyline
from PythonCAD.Interface.Viewport.polygondraw import _sample_polygon
from PythonCAD.Interface.Viewport.segmentdraw import _draw_segment, _erase_segment, _sample_segment
from PythonCAD.Interface.Viewport.textblockdraw import _draw_textblock, _erase_textblock, _format_layout
from PythonCAD.Interface.Viewport.vclinedraw import _draw_vcline, _erase_vcline

from PythonCAD.Interface.Viewport.inputhandler import IInputHandler
#from PythonCAD.Interface.Viewport.zoomtool import ZoomTool






class IViewport(IInputHandler):

#---------------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IViewport, self).__init__(parent)
        # pixmap
        self.__pixmap = None
        # cairo context
        self.__ctx = None
        # 2pi
        self.__2pi = 2.0 * math.pi
        # angle deg => rad
        self.__deg2rad = math.pi / 180.0
        # initialize entity drawing methods
        self.__init_draw_methods()
        # initialize tools drawing methods
        self.__init_sample_methods()
        # pan translation
        self.__pan_dx = 0
        self.__pan_dy = 0
        ## zoom tool
        #self.__zoom_tool = ZoomTool(self)
        # temporary object to sample
        self.__tool_to_sample = None

#----------------------------------------------------------------------------------------------------
    def __init_draw_methods(self):
        """
        Add draw methods to the entity classes
        """
        # point draw
        _class = point.Point
        _class.draw = types.MethodType(_draw_point, None, _class)
        _class.erase = types.MethodType(_erase_point, None, _class)
        # segment draw
        _class = segment.Segment
        _class.draw = types.MethodType(_draw_segment, None, _class)
        _class.erase = types.MethodType(_erase_segment, None, _class)
        # circle draw
        _class = circle.Circle
        _class.draw = types.MethodType(_draw_circle, None, _class)
        _class.erase = types.MethodType(_erase_circle, None, _class)
        # arc draw
        _class = arc.Arc
        _class.draw = types.MethodType(_draw_arc, None, _class)
        _class.erase = types.MethodType(_erase_arc, None, _class)
        # leader draw
        _class = leader.Leader
        _class.draw = types.MethodType(_draw_leader, None, _class)
        _class.erase = types.MethodType(_erase_leader, None, _class)
        # polyline draw
        _class = polyline.Polyline
        _class.draw = types.MethodType(_draw_polyline, None, _class)
        _class.erase = types.MethodType(_erase_polyline, None, _class)
        # chamfer draw
        _class = segjoint.Chamfer
        _class.draw = types.MethodType(_draw_chamfer, None, _class)
        _class.erase = types.MethodType(_erase_chamfer, None, _class)
        # fillet draw
        _class = segjoint.Fillet
        _class.draw = types.MethodType(_draw_fillet, None, _class)
        _class.erase = types.MethodType(_erase_fillet, None, _class)
        # hcline draw
        _class = hcline.HCLine
        _class.draw = types.MethodType(_draw_hcline, None, _class)
        _class.erase = types.MethodType(_erase_hcline, None, _class)
        # vcline draw
        _class = vcline.VCLine
        _class.draw = types.MethodType(_draw_vcline, None, _class)
        _class.erase = types.MethodType(_erase_vcline, None, _class)
        # acline draw
        _class = acline.ACLine
        _class.draw = types.MethodType(_draw_acline, None, _class)
        _class.erase = types.MethodType(_erase_acline, None, _class)
        # cline draw
        _class = cline.CLine
        _class.draw = types.MethodType(_draw_cline, None, _class)
        _class.erase = types.MethodType(_erase_cline, None, _class)
        # ccircle draw
        _class = ccircle.CCircle
        _class.draw = types.MethodType(_draw_ccircle, None, _class)
        _class.erase = types.MethodType(_erase_ccircle, None, _class)
        # text draw
        _class = text.TextBlock
        _class._formatLayout = types.MethodType(_format_layout, None, _class)
        _class.draw = types.MethodType(_draw_textblock, None, _class)
        _class.erase = types.MethodType(_erase_textblock, None, _class)
        # linear dimension draw
        _class = dimension.LinearDimension
        _class.draw = types.MethodType(_draw_ldim, None, _class)
        _class.draw_markers = types.MethodType(_draw_markers, None, _class)
        # radial dimension draw
        _class = dimension.RadialDimension
        _class.draw = types.MethodType(_draw_rdim, None, _class)
        _class.draw_markers = types.MethodType(_draw_markers, None, _class)
        # angular dimension draw
        _class = dimension.AngularDimension
        _class.draw = types.MethodType(_draw_adim, None, _class)
        _class.draw_markers = types.MethodType(_draw_markers, None, _class)
        # dimension draw
        _class = dimension.Dimension
        _class.erase = types.MethodType(_erase_dim, None, _class)
        _class._drawDimStrings = types.MethodType(_draw_dimstrings, None, _class)
        
#----------------------------------------------------------------------------------------------------
    def __init_sample_methods(self):
        """
        Add draw methods to the tools classes
        """
##        # point sample
##        _class = tools.PointTool
##        _class.sample = types.MethodType(_sample_point, None, _class)
        # segment sample
        _class = tools.SegmentTool
        _class.sample = types.MethodType(_sample_segment, None, _class)
        # circle sample
        _class = tools.TwoPointCircleTool
        _class.sample = types.MethodType(_sample_circle, None, _class)
        #
        _class = tools.CircleTool
        _class.sample = types.MethodType(_sample_circle, None, _class)
        #
        _class = tools.TangentCCircleTool
        _class.sample = types.MethodType(_sample_circle, None, _class)
        #
        _class = tools.TwoPointTangentCCircleTool
        _class.sample = types.MethodType(_sample_circle, None, _class)
        # arc sample
        _class = tools.ArcTool
        _class.sample = types.MethodType(_sample_arc, None, _class)
##        # leader sample
##        _class = tools.LeaderTool
##        _class.sample = types.MethodType(_sample_leader, None, _class)
        # polyline sample
        _class = tools.PolylineTool
        _class.sample = types.MethodType(_sample_polyline, None, _class)
        # polygon sample
        _class = tools.PolygonTool
        _class.sample = types.MethodType(_sample_polygon, None, _class)

##        # chamfer sample
##        _class = tools.ChamferTool
##        _class.sample = types.MethodType(_sample_chamfer, None, _class)
##        # fillet sample
##        _class = tools.FilletTool
##        _class.sample = types.MethodType(_sample_fillet, None, _class)
##        # hcline sample
##        _class = tools.HCLineTool
##        _class.sample = types.MethodType(_sample_hcline, None, _class)
##        # vcline sample
##        _class = tools.VCLineTool
##        _class.sample = types.MethodType(_sample_vcline, None, _class)
        # acline sample
        _class = tools.ACLineTool
        _class.sample = types.MethodType(_sample_acline, None, _class)
##        # cline sample
##        _class = tools.CLineTool
##        _class.sample = types.MethodType(_sample_cline, None, _class)
##        # ccircle sample
##        _class = tools.CCircleTool
##        _class.sample = types.MethodType(_sample_ccircle, None, _class)
##        # text sample
##        _class = tools.TextTool
##        _class._formatLayout = types.MethodType(_format_layout, None, _class)
##        _class.sample = types.MethodType(_sample_textblock, None, _class)
##        # linear dimension sample
##        _class = tools.LinearDimensionTool
##        _class.sample = types.MethodType(_sample_ldim, None, _class)
##        _class.draw_markers = types.MethodType(_draw_markers, None, _class)
##        # radial dimension sample
##        _class = tools.RadialDimensionTool
##        _class.sample = types.MethodType(_sample_rdim, None, _class)
##        _class.draw_markers = types.MethodType(_draw_markers, None, _class)
##        # angular dimension sample
##        _class = tools.AngularDimensionTool
##        _class.sample = types.MethodType(_sample_adim, None, _class)
##        _class.draw_markers = types.MethodType(_draw_markers, None, _class)
##        # dimension sample
##        _class = tools.DimensionTool
##        _class._drawDimStrings = types.MethodType(_sample_dimstrings, None, _class)
        
#---------------------------------------------------------------------------------------------------
    def _refresh(self):
        # viewport must have a sizxe
        if self._vwidth > 0 and self._vheight > 0:     
            # redraw the scene
            self.__redraw()

#---------------------------------------------------------------------------------------------------
    def __get_ctx(self):
        return self.__ctx

    cairo_context = property(__get_ctx, None, None, "cairo context")

#---------------------------------------------------------------------------------------------------
    def regenerate(self):
        # calculate new display factors
        self._calc_viewfactors()
        
#---------------------------------------------------------------------------------------------------
    def draw_object(self, object):
        # copy object to a temp var for later use
        self.__temp_object = object
        # set state to draw a single object
        self._view_state.current = self._view_state.DrawObject
        self.invalidate()

#---------------------------------------------------------------------------------------------------
    def __redraw(self):
        # viewport must have a size
        if self._vwidth > 0 and self._vheight > 0:
            # what to redraw
            if self._view_state.current == self._view_state.CursorMotion:
                # redraw cursor
                self.__redraw_cursor()
                self._view_state.reset()
            # pan the scene
            elif self._view_state.current == self._view_state.ZoomPan:
                # redraw pan translation
                self._zoom_tool.pan_drag()
                # update zoom window
            elif self._view_state.current == self._view_state.ZoomWindow:
                # redraw zoom window
                self._zoom_tool.window_drag()
            # redraw the visible scene
            elif self._view_state.current == self._view_state.DrawScene:
                # regenerate scene
                self.__redraw_scene()
                self._view_state.reset()
            # redraw a single object
            elif self._view_state.current == self._view_state.DrawObject:
                self.__redraw_object()
                self._view_state.reset()
            # sample/rubberband a tool
            elif self._view_state.current == self._view_state.SampleTool:
                self.__sample_tool()
                self._view_state.reset()
            # if no action is defined used show the scene
            else:
                self.show_scene()


#---------------------------------------------------------------------------------------------------
    def __clear(self, ctx):
        # draw background
        color = self._image.getOption('BACKGROUND_COLOR')
        r, g, b = color.getColors()
        ctx.set_source_rgb((r / 255.0), (g / 255.0), (b / 255.0))
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.rectangle(0, 0, self._vwidth, self._vheight)
        ctx.fill()

#---------------------------------------------------------------------------------------------------
    def show_scene(self, x = 0, y = 0):
        # create a cairo context for the background
        ctx = self.window.cairo_create()
        self.__clear(ctx)
        # move picture of scene
        if self._gc is not None and self.__pixmap is not None:
            self.window.draw_drawable(self._gc, self.__pixmap, 0, 0, x, y, self._vwidth, self._vheight)

#---------------------------------------------------------------------------------------------------
    def __redraw_cursor(self):
        # show current scene
        self.show_scene()
        # create a cairo context for the cursor
        ctx = self.window.cairo_create()
        # white cursor
        ctx.set_source_rgb(1.0, 1.0, 1.0)
        ctx.set_line_width(1.0)
        # draw cursor horizontal line
        ctx.move_to(self._cur_vx, 0)
        ctx.line_to(self._cur_vx, self._vheight)
        # draw cursor vertical line
        ctx.move_to(0, self._cur_vy)
        ctx.line_to(self._vwidth, self._cur_vy)
        # draw rectangle
        ctx.rectangle((self._cur_vx - 5), (self._cur_vy - 5), 10, 10)
        # end
        ctx.stroke()
        # reset view draw state
        self._view_state.reset()
    
#---------------------------------------------------------------------------------------------------
    def __redraw_object(self):
        # temp object must exist
        if self.__temp_object is not None:
            # if the pixmap not exist create one
            if self.__pixmap is None:
                self.__pixmap = gtk.gdk.Pixmap(self.window, self._vwidth, self._vheight)
            # create a cairo context for the pixmap
            self.__ctx = self.__pixmap.cairo_create()
            self.__ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
            # draw the object
            self.__temp_object.draw(self)
            # show the updated scene
            self.show_scene()
            # reset temp object
            self.__temp_object = None

#---------------------------------------------------------------------------------------------------
    def __redraw_scene(self):
        # create new pixmap area
        self.__pixmap = gtk.gdk.Pixmap(self.window, self._vwidth, self._vheight)
        # create a cairo context for the pixmap
        self.__ctx = self.__pixmap.cairo_create()
        self.__ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
        # clear viewport
        self.__clear(self.__ctx)
        # draw the scene
        self.__draw()
        # show the scene
        self.show_scene()
        # reset view draw state
        self._view_state.reset()

#---------------------------------------------------------------------------------------------------
    def __draw(self):
        #print "ViewportDraw.__draw()"
        #
        active_layer = self._image.getActiveLayer()
        # stack of layers
        layers = [self._image.getTopLayer()]
        # iterate over stack of layers
        while (len(layers)):
            layer = layers.pop()
            if layer is not active_layer:
                # draw inactive layer
                self.__draw_layer(layer)
            # add sublayers to the layer stack
            layers.extend(layer.getSublayers())
        # at last draw the active layer
        self.__draw_layer(active_layer)
        #
        # redraw selected entities
        #
        color = Color('#ff7733')
        for obj in self._image.getSelectedObjects(False):
            obj.draw(self, color)

#---------------------------------------------------------------------------------------------------
    def __draw_layer(self, layer):
        if not isinstance(layer, Layer):
            raise TypeError, "Invalid layer type: " + `type(layer)`
        #
        if layer.getParent() is not self._image:
            raise ValueError, "Layer not found in Image"
        #
        if layer.isVisible():
            color = self._image.getOption('INACTIVE_LAYER_COLOR')
            if layer is self._image.getActiveLayer():
                color = None
            # lists with objects to draw
            _cobjs = []
            _objs = []
            _pts = []
            # select intities within the visible region
            for _obj in layer.objsInRegion(self._wxmin, self._wymin, self._wxmax, self._wymax):
                if _obj.isVisible():
                    if isinstance(_obj, point.Point):
                        _pts.append(_obj)
                    elif isinstance(_obj, ConstructionObject):
                        _cobjs.append(_obj)
                    else:
                        _objs.append(_obj)
            # draw the entities
            for _obj in _cobjs:
                _obj.draw(self, color)
            for _obj in _pts:
                _obj.draw(self, color)
            for _obj in _objs:
                _obj.draw(self, color)

#---------------------------------------------------------------------------------------------------
    def __set_draw_properties(self, color, lineweight, linestyle):
        #print "ViewportDraw.draw_set_properties()"
        if color is not None:
            # set color property
            r, g, b = color.getColors()
            #print "color: ", r, g, b
            self.__ctx.set_source_rgb((r / 255.0), (g / 255.0), (b / 255.0))
        # set linestyle property
        if linestyle is not None:
            self.__ctx.set_dash(linestyle)
            ##print "linestyle: ", linestyle
        # set lineweight property
        if lineweight is not None and lineweight > 0.0:
            self.__ctx.set_line_width(lineweight)
            #print "lineweight: ", lineweight
        
#---------------------------------------------------------------------------------------------------
    def draw_linestring(self, color, lineweight, linestyle, points):
        ##print "ViewportDraw.draw_linestring()"
        # use cairo
        if self.__ctx is not None:
            first_point = True
            #begin
            self.__ctx.save()
            # set properties
            self.__set_draw_properties(color, lineweight, linestyle)
            # draw the points
            for point in points:
                # transform to display coordinates
                x, y = point.getCoords()
                px, py = self.world_to_view(x, y)
                if first_point:
                    self.__ctx.move_to(px, py)
                    first_point = False
                else:
                    self.__ctx.line_to(px, py)
            # end
            self.__ctx.stroke()
            self.__ctx.restore()

#---------------------------------------------------------------------------------------------------
    def draw_polygon(self, color, lineweight, linestyle, points, fill):
        ##print "ViewportDraw.draw_linestring()"
        # use cairo
        if self.__ctx is not None:
            first_point = True
            #begin
            self.__ctx.save()
            # set properties
            self.__set_draw_properties(color, lineweight, linestyle)
            # draw the points
            for point in points:
                # transform to display coordinates
                x, y = point.getCoords()
                px, py = self.world_to_view(x, y)
                if first_point:
                    self.__ctx.move_to(px, py)
                    first_point = False
                else:
                    self.__ctx.line_to(px, py)
            # close
            self.__ctx.close_path()
            # fill?
            if fill:
                self.__ctx.fill()
            # end
            self.__ctx.stroke()
            self.__ctx.restore()

#---------------------------------------------------------------------------------------------------
    def draw_arc(self, color, lineweight, linestyle, center, radius, start, end):
        ##print "ViewportDraw.draw_arc()"
        # use cairo
        if self.__ctx is not None:
            #begin
            self.__ctx.save()
            # set properties
            self.__set_draw_properties(color, lineweight, linestyle)
            # what is this: internal presentation of an arc in degrees??
            rstart = start * self.__deg2rad
            rend = end * self.__deg2rad
            # transform to display coordinates
            x, y = center.getCoords()
            vx, vy = self.world_to_view(x, y)
            vradius = self.size_world_to_view(radius)
            # arc drawing relies on Cairo transformations
            self.__ctx.scale(1.0, -1.0)
            self.__ctx.translate(vx, -(vy))
            # draw the arc
            self.__ctx.new_sub_path()
            self.__ctx.arc(0.0, 0.0, vradius, rstart, rend)
            # end
            self.__ctx.stroke()
            self.__ctx.restore()
            
#---------------------------------------------------------------------------------------------------
    def draw_circle(self, color, lineweight, linestyle, center, radius, fill = False):
        ##print "ViewportDraw.draw_arc()"
        # use cairo
        if self.__ctx is not None:
            #begin
            self.__ctx.save()
            # set properties
            self.__set_draw_properties(color, lineweight, linestyle)
            # transform to display coordinates
            x, y = center.getCoords()
            vx, vy = self.world_to_view(x, y)
            vradius = self.size_world_to_view(radius)
            # arc drawing relies on Cairo transformations
            self.__ctx.scale(1.0, -1.0)
            self.__ctx.translate(vx, -(vy))
            # draw the arc
            self.__ctx.arc(0.0, 0.0, vradius, 0, self.__2pi)
            # fill the circle?
            if fill:
                self.__ctx.close_path()
                self.__ctx.fill()
            # end
            self.__ctx.stroke()
            self.__ctx.restore()

#---------------------------------------------------------------------------------------------------
    def draw_text(self, color, location, layout):
        ##print "ViewportDraw.draw_text()"
        # return values
        #width = 0
        #height = 0
        # use cairo
        if self.__ctx is not None:
            #begin
            self.__ctx.save()
            # set color property
            r, g, b = color.getColors()
            #print "color: ", r, g, b
            self.__ctx.set_source_rgb((r / 255.0), (g / 255.0), (b / 255.0))
            # position
            x = location[0]
            y = location[1]
            vx, vy = self.world_to_view(x, y)
            self.__ctx.move_to(vx, vy)
            self.__ctx.show_layout(layout)
            self.__ctx.restore()    

#---------------------------------------------------------------------------------------------------
# tool sample functions
#---------------------------------------------------------------------------------------------------
    def sample(self, tool):
        # copy object to a temp var for later use
        self.__tool_to_sample = tool
        # set state to draw a single object
        self._view_state.current = self._view_state.SampleTool
        self.invalidate()

#---------------------------------------------------------------------------------------------------
    def __sample_tool(self):
        if self.__tool_to_sample is not None:
            # show current scene
            self.show_scene()
            # create a cairo context for the sample
            self.__ctx = self.window.cairo_create()
            # sample color
            color = Color(255, 255, 255)
            self.__tool_to_sample.sample(self, color)
            
