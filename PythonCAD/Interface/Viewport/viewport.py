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


# draw imports
from PythonCAD.Interface.Viewport.aclinedraw import _draw_acline, _erase_acline
from PythonCAD.Interface.Viewport.arcdraw import _draw_arc, _erase_arc
from PythonCAD.Interface.Viewport.circledraw import _draw_circle,_erase_circle
from PythonCAD.Interface.Viewport.ccircledraw import _draw_ccircle,_erase_ccircle
from PythonCAD.Interface.Viewport.chamferdraw import _draw_chamfer, _erase_chamfer
from PythonCAD.Interface.Viewport.clinedraw import _draw_cline, _erase_cline
from PythonCAD.Interface.Viewport.dimdraw import _draw_ldim, _draw_rdim, _draw_adim, _draw_markers, _draw_dimstrings, _erase_dim
from PythonCAD.Interface.Viewport.filletdraw import _draw_fillet, _erase_fillet
from PythonCAD.Interface.Viewport.hclinedraw import _draw_hcline, _erase_hcline
from PythonCAD.Interface.Viewport.leaderdraw import _draw_leader, _erase_leader
from PythonCAD.Interface.Viewport.pointdraw import _draw_point, _erase_point
from PythonCAD.Interface.Viewport.polylinedraw import _draw_polyline, _erase_polyline
from PythonCAD.Interface.Viewport.segmentdraw import _draw_segment, _erase_segment
from PythonCAD.Interface.Viewport.textblockdraw import _draw_textblock, _erase_textblock, _format_layout
from PythonCAD.Interface.Viewport.vclinedraw import _draw_vcline, _erase_vcline

from PythonCAD.Interface.Viewport.inputhandler import IInputHandler






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
        
#        _class = layer.Layer
#        _class.draw = types.MethodType(_draw_layer, None, _class)
#        _class.erase = types.MethodType(_erase_layer, None, _class)

#---------------------------------------------------------------------------------------------------
    def zoom_fit(self):
        print "IViewport.zoom_fit()"
        # world dimension
        self._wxmin, self._wymin, self._wxmax, self._wymax = self._image.getExtents()
        # modify to view a little margin
        margin = (self._wxmax - self._wxmin) / 100.0
        self._wxmin -= margin
        self._wxmax += margin
        self._wymin -= margin
        self._wymax += margin
        print "world (Xmin, Xmax): ", self._wxmin, self._wxmax
        print "world (Ymin, Ymax): ", self._wymin, self._wymax
        # set the view translation and scale factors
        self._calc_viewfactors()

#---------------------------------------------------------------------------------------------------
    def __zoom_scale(self, scale):
        print "IViewport.zoom_in()"
        # modify world window
        self._wxmin = self._cur_wx - (self._cur_wx - self._wxmin) * scale
        self._wxmax = self._cur_wx + (self._wxmax - self._cur_wx) * scale
        self._wymin = self._cur_wy - (self._cur_wy - self._wymin) * scale
        self._wymax = self._cur_wy + (self._wymax - self._cur_wy) * scale
        # set the view translation and scale factors
        self._calc_viewfactors()

#---------------------------------------------------------------------------------------------------
    def zoom_in(self):
        print "IViewport.zoom_in()"
        self.__zoom_scale(0.75)

#---------------------------------------------------------------------------------------------------
    def zoom_out(self):
        print "IViewport.zoom_out()"
        self.__zoom_scale(1.25)

#---------------------------------------------------------------------------------------------------
    def refresh(self):
        print "IViewport.refresh()"
        # viewport must have a sizxe
        if self._vwidth > 0 and self._vheight > 0:        
            # redraw the scene
            self.redraw()
            ## show the scene/pixmap
            #if self._gc is not None and self.__pixmap is not None:
                #self.window.draw_drawable(self._gc, self.__pixmap, 0, 0, 0, 0, self._vwidth, self._vheight)

#---------------------------------------------------------------------------------------------------
    def __get_ctx(self):
        return self.__ctx

    cairo_context = property(__get_ctx, None, None, "cairo context")

#---------------------------------------------------------------------------------------------------
    def redraw(self):
        # viewport must have a sizxe
        if self._vwidth > 0 and self._vheight > 0:
            # what to redraw
            if self._view_state.current == self._view_state.CursorMotion:
                self.redraw_cursor()
            elif self._view_state.current == self._view_state.DrawScene:
                self.redraw_scene()
            
#---------------------------------------------------------------------------------------------------
    def redraw_cursor(self):
        # viewport must have a sizxe
        if self._vwidth > 0 and self._vheight > 0:
            # show the current scene
            if self._gc is not None and self.__pixmap is not None:
                self.window.draw_drawable(self._gc, self.__pixmap, 0, 0, 0, 0, self._vwidth, self._vheight)
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
    
#---------------------------------------------------------------------------------------------------
    def redraw_scene(self):
        # viewport must have a sizxe
        if self._vwidth > 0 and self._vheight > 0:
            # create new pixmap area
            self.__pixmap = gtk.gdk.Pixmap(self.window, self._vwidth, self._vheight)
            # create a cairo context for the pixmap
            self.__ctx = self.__pixmap.cairo_create()
            self.__ctx.set_antialias(cairo.ANTIALIAS_NONE)
            #self.__ctx = self.window.cairo_create()
            # draw background
            color = self._image.getOption('BACKGROUND_COLOR')
            r, g, b = color.getColors()
            self.__ctx.set_source_rgb((r / 255.0), (g / 255.0), (b / 255.0))
            self.__ctx.set_source_rgb(0.5, 0.5, 0.5)
            self.__ctx.rectangle(0, 0, self._vwidth, self._vheight)
            self.__ctx.fill()
            # draw the scene
            self.draw()
            # show the scene
            if self._gc is not None and self.__pixmap is not None:
                self.window.draw_drawable(self._gc, self.__pixmap, 0, 0, 0, 0, self._vwidth, self._vheight)
            # update point
            #self._set_tool_point(self._cur_vx, self._cur_vy)

#---------------------------------------------------------------------------------------------------
    def draw(self):
        print "ViewportDraw.__draw()"
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
        print "ViewportDraw.__draw_layer()"
#        # is it a layer object
#        if not isinstance(layer, Layer):
#            raise TypeError, "Invalid layer type: " + `type(layer)`
#        # layer must belong to the image
#        if layer.getParent() is not self.__image:
#            raise ValueError, "Layer not found in Image"
#        # only draw visible layers
#        if layer.isVisible():
#            color = self.__image.getOption('INACTIVE_LAYER_COLOR')
#            if layer is self.__image.getActiveLayer():
#                color = None
#            # draw the points
#            for obj in layer.getLayerEntities("point"):
#                if obj.isVisible():
#                    iobj = IPoint(ctx, obj)
#                    iobj.draw(color)
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
        print "ViewportDraw.draw_set_properties()"
        if color is not None:
            # set color property
            r, g, b = color.getColors()
            print "color: ", r, g, b
            self.__ctx.set_source_rgb((r / 255.0), (g / 255.0), (b / 255.0))
        # set linestyle property
        if linestyle is not None:
            self.__ctx.set_dash(linestyle)
            print "linestyle: ", linestyle
        # set lineweight property
        if lineweight is not None and lineweight > 0.0:
            self.__ctx.set_line_width(lineweight)
            print "lineweight: ", lineweight
        
#---------------------------------------------------------------------------------------------------
    def draw_linestring(self, color, lineweight, linestyle, points):
        print "ViewportDraw.draw_linestring()"
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
        print "ViewportDraw.draw_linestring()"
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
        print "ViewportDraw.draw_arc()"
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
        print "ViewportDraw.draw_arc()"
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
        print "ViewportDraw.draw_text()"
        # return values
        width = 0
        height = 0
        # use cairo
        if self.__ctx is not None:
            #begin
            self.__ctx.save()
            # set color property
            r, g, b = color.getColors()
            print "color: ", r, g, b
            self.__ctx.set_source_rgb((r / 255.0), (g / 255.0), (b / 255.0))
            # position
            x = location[0]
            y = location[1]
            vx, vy = self.world_to_view(x, y)
            self.__ctx.move_to(vx, vy)
            self.__ctx.show_layout(layout)
            self.__ctx.restore()    

#---------------------------------------------------------------------------------------------------
