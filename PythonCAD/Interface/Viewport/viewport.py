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

import types
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

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

# draw imports
from PythonCAD.Interface.Viewport.aclinedraw import _draw_acline, _erase_acline
from PythonCAD.Interface.Viewport.arcdraw import _draw_arc, _erase_arc
from PythonCAD.Interface.Viewport.circledraw import _draw_circle,_erase_circle
from PythonCAD.Interface.Viewport.ccircledraw import _draw_ccircle,_erase_ccircle
from PythonCAD.Interface.Viewport.chamferdraw import _draw_chamfer, _erase_chamfer
from PythonCAD.Interface.Viewport.clinedraw import _draw_cline, _erase_cline
from PythonCAD.Interface.Viewport.dimdraw import _draw_ldim, _draw_rdim, _draw_adim, _draw_dimstrings, _erase_dim
from PythonCAD.Interface.Viewport.filletdraw import _draw_fillet, _erase_fillet
from PythonCAD.Interface.Viewport.hclinedraw import _draw_hcline, _erase_hcline
from PythonCAD.Interface.Viewport.leaderdraw import _draw_leader, _erase_leader
from PythonCAD.Interface.Viewport.pointdraw import _draw_point, _erase_point
from PythonCAD.Interface.Viewport.polylinedraw import _draw_polyline, _erase_polyline
from PythonCAD.Interface.Viewport.segmentdraw import _draw_segment, _erase_segment
from PythonCAD.Interface.Viewport.textblockdraw import _draw_textblock, _erase_textblock, _format_layout
from PythonCAD.Interface.Viewport.vclinedraw import _draw_vcline, _erase_vcline




class IViewport(gtk.DrawingArea):

#---------------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IViewport, self).__init__()
        #
        self.__gtkimage = parent
        self.__image = self.__gtkimage.getImage()
        # view window size
        self.__vxmin = 0
        self.__vymin = 0
        self.__vxmax = 0
        self.__vymax = 0
        self.__vwidth = 0
        self.__vheight = 0
        # world window size
        self.__wxmin = 0
        self.__wymin = 0
        self.__wxmax = 0
        self.__wymax = 0
        self.__wwidth = 0
        self.__wheight = 0
        # draw properties
        self.__need_redraw = True
        # graphics context
        self.__gc = None
        self.__ctx = None
        # pixmap
        self.__pixmap = None
        # pixmap scale factor (1=viewport size, 2=twice the size, 3=even larger)
        self.__px_scale_factor = 2
        # cairo translate factors
        self.__dx = 0.0
        self.__dy = 0.0
        # cairo scale factors
        self.__sx = 1.0
        self.__sy = 1.0
        # initialize entity drawing methods
        self.__init_draw_methods()

#        black = gtk.gdk.color_parse('black')
#        self.__da.modify_fg(gtk.STATE_NORMAL, black)
#        self.__da.modify_bg(gtk.STATE_NORMAL, black)
#        pane.pack2(self.__da, True, False)
#        self.__da.set_flags(gtk.CAN_FOCUS)
        self.connect("event", self.__daEvent)
        self.connect("expose_event", self.__exposeEvent)
        self.connect("realize", self.__realizeEvent)

#        self.__da.connect("configure_event", self.__configureEvent)
#        # self.__da.connect("focus_in_event", self.__focusInEvent)
#        # self.__da.connect("focus_out_event", self.__focusOutEvent)
#
        self.set_events(gtk.gdk.EXPOSURE_MASK |
                             gtk.gdk.LEAVE_NOTIFY_MASK |
                             gtk.gdk.BUTTON_PRESS_MASK |
                             gtk.gdk.BUTTON_RELEASE_MASK |
                             gtk.gdk.ENTER_NOTIFY_MASK|
                             gtk.gdk.LEAVE_NOTIFY_MASK|
                             gtk.gdk.KEY_PRESS_MASK |
                             gtk.gdk.KEY_RELEASE_MASK |
                             gtk.gdk.FOCUS_CHANGE_MASK |
                             gtk.gdk.POINTER_MOTION_MASK)


        # event handlers

#----------------------------------------------------------------------------------------------------
    def __init_draw_methods(self):
        """
        Add draw methods to the entity classes
        """
        _class = point.Point
        _class.draw = types.MethodType(_draw_point, None, _class)
        _class.erase = types.MethodType(_erase_point, None, _class)
        _class = segment.Segment
        _class.draw = types.MethodType(_draw_segment, None, _class)
        _class.erase = types.MethodType(_erase_segment, None, _class)
        _class = circle.Circle
        _class.draw = types.MethodType(_draw_circle, None, _class)
        _class.erase = types.MethodType(_erase_circle, None, _class)
        _class = arc.Arc
        _class.draw = types.MethodType(_draw_arc, None, _class)
        _class.erase = types.MethodType(_erase_arc, None, _class)
        _class = leader.Leader
        _class.draw = types.MethodType(_draw_leader, None, _class)
        _class.erase = types.MethodType(_erase_leader, None, _class)
        _class = polyline.Polyline
        _class.draw = types.MethodType(_draw_polyline, None, _class)
        _class.erase = types.MethodType(_erase_polyline, None, _class)
        _class = segjoint.Chamfer
        _class.draw = types.MethodType(_draw_chamfer, None, _class)
        _class.erase = types.MethodType(_erase_chamfer, None, _class)
        _class = segjoint.Fillet
        _class.draw = types.MethodType(_draw_fillet, None, _class)
        _class.erase = types.MethodType(_erase_fillet, None, _class)
        _class = hcline.HCLine
        _class.draw = types.MethodType(_draw_hcline, None, _class)
        _class.erase = types.MethodType(_erase_hcline, None, _class)
        _class = vcline.VCLine
        _class.draw = types.MethodType(_draw_vcline, None, _class)
        _class.erase = types.MethodType(_erase_vcline, None, _class)
        _class = acline.ACLine
        _class.draw = types.MethodType(_draw_acline, None, _class)
        _class.erase = types.MethodType(_erase_acline, None, _class)
        _class = cline.CLine
        _class.draw = types.MethodType(_draw_cline, None, _class)
        _class.erase = types.MethodType(_erase_cline, None, _class)
        _class = ccircle.CCircle
        _class.draw = types.MethodType(_draw_ccircle, None, _class)
        _class.erase = types.MethodType(_erase_ccircle, None, _class)
        _class = text.TextBlock
        _class._formatLayout = types.MethodType(_format_layout, None, _class)
        _class.draw = types.MethodType(_draw_textblock, None, _class)
        _class.erase = types.MethodType(_erase_textblock, None, _class)
        _class = dimension.LinearDimension
        _class.draw = types.MethodType(_draw_ldim, None, _class)
        _class = dimension.RadialDimension
        _class.draw = types.MethodType(_draw_rdim, None, _class)
        _class = dimension.AngularDimension
        _class.draw = types.MethodType(_draw_adim, None, _class)
        _class = dimension.Dimension
        _class.erase = types.MethodType(_erase_dim, None, _class)
        _class._drawDimStrings = types.MethodType(_draw_dimstrings, None, _class)
#        _class = layer.Layer
#        _class.draw = types.MethodType(_draw_layer, None, _class)
#        _class.erase = types.MethodType(_erase_layer, None, _class)

#---------------------------------------------------------------------------------------------------
    def __realizeEvent(self, widget, data=None):
        print "IViewport.__realizeEvent()"
        # create a graphic context if not exists
        self.__gc = self.window.new_gc()

#---------------------------------------------------------------------------------------------------
    def __daEvent(self, widget, event, data=None):
        _rv = False
#        _type = event.type
#        debug_print("__daEvent(): Event type: %d" % _type)
#        _tool = self.__image.getTool()
#        if _type==31:
#            debug_print("if 31")
#            if event.direction == gtk.gdk.SCROLL_UP:
#                debug_print("BUTTON_PRESSS CROLL_UP")
#                self.ZoomIn()
#            if event.direction == gtk.gdk.SCROLL_DOWN:
#                debug_print("BUTTON_PRESSS SCROLL_DOWN")
#                self.ZoomOut()
#        if _type == 12:
#            debug_print("if 12")
#        if _type == gtk.gdk.BUTTON_PRESS:
#            debug_print("gtk.gdk.BUTTON_PRESS")
#            self.setToolpoint(event)
#            _button = event.button
#            if _button == 1:
#                if _tool is not None and _tool.hasHandler("button_press"):
#                    _rv = _tool.getHandler("button_press")(self, widget,
#                                                           event, _tool)
#            debug_print("__Move BUTTON_PRESS")
#            self.__Move(widget, event)
#        elif _type == gtk.gdk.BUTTON_RELEASE:
#            debug_print("gtk.gdk.BUTTON_RELEASE")
#            self.setToolpoint(event)
#            _button = event.button
#            if _button == 1:
#                if _tool is not None and _tool.hasHandler("button_release"):
#                    _rv =_tool.getHandler("button_release")(self, widget,
#                                                            event, _tool)
#            debug_print("__Move BUTTON_RELEASE")
#            self.__Move(widget, event)
#        elif _type == gtk.gdk.MOTION_NOTIFY:
#            debug_print("gtk.gdk.MOTION_NOTIFY")
#            self.setToolpoint(event)
#            if _tool is not None and _tool.hasHandler("motion_notify"):
#                _rv = _tool.getHandler('motion_notify')(self, widget,
#                                                        event, _tool)
#            debug_print("__Move MOTION_NOTIFY")
#            self.__MakeMove(widget,event)
#            self.__ActiveSnapEvent(widget,event)
#        elif _type == gtk.gdk.KEY_PRESS:
#            debug_print("In __daEvent(), got key press!")
#            _key = event.keyval
#            if (_key == gtk.keysyms.Page_Up or
#                _key == gtk.keysyms.Page_Down or
#                _key == gtk.keysyms.Left or
#                _key == gtk.keysyms.Right or
#                _key == gtk.keysyms.Up or
#                _key == gtk.keysyms.Down):
#                debug_print("Got Arrow/PageUp/PageDown key")
#                #KeyMoveDrawing(_key) # Matteo Boscolo 12-05-2009
#                pass # handle moving the drawing in some fashion ...
#            elif _key == gtk.keysyms.Escape:
#                debug_print("Got escape key")
#                self.reset()
#                _rv = True
#            elif _tool is not None and _tool.hasHandler("key_press"):
#                debug_print("gtk.gdk.MOTION_NOTIFY")
#                _rv = _tool.getHandler("key_press")(self, widget,
#                                                    event, _tool)
#            else:
#                debug_print("ELSE")
#                _entry = self.__entry
#                _entry.grab_focus()
#                if _key == gtk.keysyms.Tab:
#                    _rv = True
#                else:
#                    _rv = _entry.event(event)
#        elif _type == gtk.gdk.ENTER_NOTIFY:
#            debug_print("gtk.gdk.ENTER_NOTIFY")
#            self.setToolpoint(event)
#            _rv = True
#        elif _type == gtk.gdk.LEAVE_NOTIFY:
#            debug_print("gtk.gdk.LEAVE_NOTIFY")
#            self.setToolpoint(event)
#            _rv = True
#        else:
#            debug_print("Got type %d" % _type)
#            pass
        return _rv

#---------------------------------------------------------------------------------------------------
    def __exposeEvent(self, widget, event, data=None):
        print "IViewport.__exposeEvent()"
        # view dimension
        self.__vxmin, self.__vymin, width, height = event.area
        self.__vxmax = self.__vxmin + width
        self.__vymax = self.__vymin + height
        print "viewport (Xmin, Xmax)", self.__vxmin, self.__vxmax
        print "viewport (Ymin, Ymax)", self.__vymin, self.__vymax

#        _, _, vp_width, vp_height = event.area
#        print vp_width, vp_height
#        # need to redraw the scene
#        if self.__pixmap == None:
#            print "need_redraw"
#            self.__need_redraw = True
#        else:
#            px_width, px_height = self.__pixmap.get_size()
#            if (px_width < vp_width) or (px_height < vp_height):
#                print "need_redraw"
#                self.__need_redraw = True
        # refresh
        self.__need_redraw = True
        self.refresh()
        return True

#---------------------------------------------------------------------------------------------------
    def __calc_viewfactors(self):
        print "IViewport.__calc_viewfactors()"
        # viewport width and height
        self.__vwidth = self.__vxmax - self.__vxmin
        self.__vheight = self.__vymax - self.__vymin
        # world width and height
        self.__wwidth = self.__wxmax - self.__wxmin
        self.__wheight = self.__wymax - self.__wymin
        print "World (w, h):", self.__wwidth, self.__wheight
        print "View (w, h):", self.__vwidth, self.__vheight
        # translation
        self.__dx = self.__wxmin
        self.__dy = self.__wymin
        print "Translate: ", self.__dx, self.__dy
        # scale factor
        sx = 1.0 * self.__vwidth / self.__wwidth
        sy = 1.0 * self.__vheight / self.__wheight
        self.__sx = sx
        self.__sy = sy
        print "Scale: ", self.__sx, self.__sy

#---------------------------------------------------------------------------------------------------
    def zoom_fit(self):
        print "IViewport.zoom_fit()"
        # world dimension
        self.__wxmin, self.__wymin, self.__wxmax, self.__wymax = self.__image.getExtents()
        # modify to view a little margin
        decrement = (self.__wxmax - self.__wxmin) / -100.0
        self.__wxmin += decrement
        self.__wxmax -= decrement
        self.__wymin += decrement
        self.__wymax -= decrement
        print "world (Xmin, Xmax): ", self.__wxmin, self.__wxmax
        print "world (Ymin, Ymax): ", self.__wymin, self.__wymax
        # set the view translation and scale factors
        self.__calc_viewfactors()
        # redraw
        self.__need_redraw = True
        self.invalidate()

#---------------------------------------------------------------------------------------------------
    def zoom_in(self):
        print "IViewport.zoom_in()"
        # modify world window
        dx = (self.__wxmax - self.__wxmin) / 4.0
        dy = (self.__wymax - self.__wymin) / 4.0
        self.__wxmin += dx
        self.__wxmax -= dx
        self.__wymin += dy
        self.__wymax -= dy
        # set the view translation and scale factors
        self.__calc_viewfactors()
        # redraw
        self.__need_redraw = True
        self.invalidate()

#---------------------------------------------------------------------------------------------------
    def zoom_out(self):
        print "IViewport.zoom_out()"
        # modify world window
        dx = (self.__wxmax - self.__wxmin) / 4.0
        dy = (self.__wymax - self.__wymin) / 4.0
        self.__wxmin -= dx
        self.__wxmax += dx
        self.__wymin -= dy
        self.__wymax += dy      
        # set the view translation and scale factors
        self.__calc_viewfactors()
        # redraw
        self.__need_redraw = True
        self.invalidate()

#---------------------------------------------------------------------------------------------------
    def invalidate(self):
        print "IViewport.invalidate()"
        if self.window:
            alloc = self.get_allocation()
            rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)

#---------------------------------------------------------------------------------------------------
    def refresh(self):
        print "IViewport.refresh()"
        # need to draw the scene?
        if self.__need_redraw or self.__pixmap == None:
            # redraw the scene
            self.redraw()
            self.__need_redraw = False
        # show the scene/pixmap
        #self.window.draw_drawable(self.__gc, self.__pixmap, 0, 0, 0, 0, alloc.width, alloc.height)

#---------------------------------------------------------------------------------------------------
    def __get_image(self):
        return self.__image

    Image = property(__get_image, None, None, "Generic Image")

#---------------------------------------------------------------------------------------------------
    def __get_ctx(self):
        return self.__ctx

    CairoContext = property(__get_ctx, None, None, "cairo context")

#---------------------------------------------------------------------------------------------------
    def redraw(self):
        print "IViewport.redraw()"
        # create new pixmap area
        #self.__pixmap = gtk.gdk.Pixmap(self.window, width, height)
        # create a cairo context for the pixmap
        #ctx = self.__pixmap.cairo_create()
        self.__ctx = self.window.cairo_create()
        # draw background
        self.__ctx.set_source_rgb(0.5, 0.5, 0.5)
        self.__ctx.rectangle(0, 0, self.__vwidth, self.__vheight)
        self.__ctx.fill()
        # draw the scene
        self.draw()

#---------------------------------------------------------------------------------------------------
    def WorldToViewport(self, x, y):
        print "Point (world): ", x, y
        _x = (x - self.__dx) * self.__sx
        _y = self.__vheight - ((y - self.__dy) * self.__sy)
        print "Point (view): ", _x, _y
        return _x, _y

#---------------------------------------------------------------------------------------------------
    def ViewportToWorld(self, x, y):
        print "Point (view): ", x, y
        _x = (x / self.__sx) + self.__dx
        _y = ((self.__vheight - y) / self.__sy) + self.__dy
        print "Point (world): ", _x, _y
        return _x, _y

#---------------------------------------------------------------------------------------------------
    def draw(self):
        print "ViewportDraw.__draw()"
        #
        active_layer = self.__image.getActiveLayer()
        # stack of layers
        layers = [self.__image.getTopLayer()]
        # iterate over stack of layers
        while (len(layers)):
            layer = layers.pop()
            if layer is not active_layer:
                # draw inactive layer
                self.__draw_layer(layer, self.__ctx)
            # add sublayers to the layer stack
            layers.extend(layer.getSublayers())
        # at last draw the active layer
        self.__draw_layer(active_layer)
        #
        # redraw selected entities
        #
        color = Color('#ff7733')
        for obj in self.__image.getSelectedObjects(False):
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
        if layer.getParent() is not self.__image:
            raise ValueError, "Layer not found in Image"
        #
        if layer.isVisible():
            color = self.__image.getOption('INACTIVE_LAYER_COLOR')
            if layer is self.__image.getActiveLayer():
                color = None
            # lists with objects to draw
            _cobjs = []
            _objs = []
            _pts = []
            # select intities within the visible region
            for _obj in layer.objsInRegion(self.__wxmin, self.__wymin, self.__wxmax, self.__wymax):
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
