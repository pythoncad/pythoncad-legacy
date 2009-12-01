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
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

#from PythonCAD.Generic.image import Image
from PythonCAD.Generic.layer import Layer
from PythonCAD.Interface.Entities.ipoint import IPoint


class IViewport(gtk.DrawingArea):

#---------------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IViewport, self).__init__()
        #
        self.__gtkimage = parent
        self.__image = self.__gtkimage.getImage()
        self.__need_redraw = True
        # graphics context
        self.__gc = None
        # pixmap
        self.__pixmap = None
        # pixmap scale factor (1=viewport size, 2=twice the size, 3=even larger)
        self.__px_scale_factor = 2
        # cairo translate factors
        self.__cr_translate_x = 0.0
        self.__cr_translate_y = 0.0
        # cairo scale factors
        self.__cr_scale_x = 1.0
        self.__cr_scale_y = 1.0

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
        # window dimension
        _, _, vp_width, vp_height = event.area
        print vp_width, vp_height
        # need to redraw the scene
        if self.__pixmap == None:
            print "need_redraw"
            self.__need_redraw = True
        else:
            px_width, px_height = self.__pixmap.get_size()
            if (px_width < vp_width) or (px_height < vp_height):
                print "need_redraw"
                self.__need_redraw = True
        # refresh
        self.refresh()
        return True
<<<<<<< HEAD

#---------------------------------------------------------------------------------------------------
    def zoom_fit(self):
        print "IViewport.zoom_fit()"
        #mtrx = cairo.Matrix(1,0,0,1,dx,dy)
        #mtrx = cairo.Matrix(fx,0,0,fy,0,0)
        # view extents
        alloc = self.get_allocation()
        vp_width = alloc.width
        vp_height = alloc.height
        print "Viewport: ", vp_width, vp_height
        # image extents
        xmin, ymin, xmax, ymax = self.__image.getExtents()
        # image size
        img_width = xmax - xmin
        img_height = ymax - ymin
        print "Image: ", img_width, img_height
        # set cairo transformation matrix
        self.__cr_translate_x = min(img_width, img_height) / 2.0
        self.__cr_translate_y = self.__cr_translate_x
        print "Translate: ", self.__cr_translate_x, self.__cr_translate_y
        # cairo scale factors
        self.__cr_scale_x = min(vp_width / img_width, vp_height / img_height)
        self.__cr_scale_y = self.__cr_scale_x
        print "Scale: ", self.__cr_scale_x, self.__cr_scale_y
        # redraw
        self.__need_redraw = True
        self.invalidate()

#---------------------------------------------------------------------------------------------------
=======

#---------------------------------------------------------------------------------------------------
    def zoom_fit(self):
        print "IViewport.zoom_fit()"
        #mtrx = cairo.Matrix(1,0,0,1,dx,dy)
        #mtrx = cairo.Matrix(fx,0,0,fy,0,0)
        # view extents
        alloc = self.get_allocation()
        vp_width = alloc.width
        vp_height = alloc.height
        print "Viewport: ", vp_width, vp_height
        # image extents
        xmin, ymin, xmax, ymax = self.__image.getExtents()
        # image size
        img_width = xmax - xmin
        img_height = ymax - ymin
        print "Image: ", img_width, img_height
        # set cairo transformation matrix
        self.__cr_translate_x = min(img_width, img_height) / 2.0
        self.__cr_translate_y = self.__cr_translate_x
        print "Translate: ", self.__cr_translate_x, self.__cr_translate_y
        # cairo scale factors
        self.__cr_scale_x = min(vp_width / img_width, vp_height / img_height)
        self.__cr_scale_y = self.__cr_scale_x
        print "Scale: ", self.__cr_scale_x, self.__cr_scale_y
        # redraw
        self.__need_redraw = True
        self.invalidate()

#---------------------------------------------------------------------------------------------------
>>>>>>> ee1bf5e10f88608da6191a17e1f65ffeec3d3ca1
    def zoom_in(self):
        print "IViewport.zoom_in()"
        # cairo scale factors
        self.__cr_scale_x *= 2.0
        self.__cr_scale_y = self.__cr_scale_x
        # redraw
        self.__need_redraw = True
        self.invalidate()

#---------------------------------------------------------------------------------------------------
    def zoom_out(self):
        print "IViewport.zoom_out()"
        # cairo scale factors
        self.__cr_scale_x *= 0.5
        self.__cr_scale_y = self.__cr_scale_x
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
        # viewport size
        alloc = self.get_allocation()
        # need to draw the scene?
        if self.__need_redraw or self.__pixmap == None:
            # redraw the scene
            self.redraw()
            self.__need_redraw = False
        # show the scene/pixmap
        #self.window.draw_drawable(self.__gc, self.__pixmap, 0, 0, 0, 0, alloc.width, alloc.height)

#---------------------------------------------------------------------------------------------------
    def redraw(self):
        print "IViewport.redraw()"
        # viewport size
        alloc = self.get_allocation()
        # pixmap size = area size * scale factor
        width = alloc.width * self.__px_scale_factor
        height = alloc.height * self.__px_scale_factor
        # create new pixmap area
        #self.__pixmap = gtk.gdk.Pixmap(self.window, width, height)
        # create a cairo context for the pixmap
        #ctx = self.__pixmap.cairo_create()
        ctx = self.window.cairo_create()
        # draw background
        ctx.set_source_rgb(0.5, 0.5, 0.5)
        ctx.rectangle(0, 0, width, height)
        ctx.fill()
        # draw the scene
<<<<<<< HEAD
        self.__draw(ctx)
        
=======
        self.__test(ctx)
        #self.__draw(ctx)
        
        
#---------------------------------------------------------------------------------------------------
    def __test(self, ctx):
        ctx.set_line_width(1.0)
        ctx.set_source_rgb(1, 0, 0)
        ctx.rectangle(1.0, 1.0, 100.0, 100.0)
        ctx.stroke()
        
>>>>>>> ee1bf5e10f88608da6191a17e1f65ffeec3d3ca1
#---------------------------------------------------------------------------------------------------
    def __draw(self, ctx):
        print "IViewport.__draw()"
        # set transformations
        ctx.translate(self.__cr_translate_x, self.__cr_translate_y)
        print self.__cr_translate_x, self.__cr_translate_y
        ctx.scale(self.__cr_scale_x, self.__cr_scale_y)
        print self.__cr_scale_x, self.__cr_scale_y
        #
        active_layer = self.__image.getActiveLayer()
        # stack of layers
        layers = [self.__image.getTopLayer()]
        # iterate over stack of layers
        while (len(layers)):
            layer = layers.pop()
            if layer is not active_layer:
                # draw inactive layer
                self.__draw_layer(layer, ctx)
            # add sublayers to the layer stack
            layers.extend(layer.getSublayers())
        # at last draw the active layer
        self.__draw_layer(active_layer, ctx)
        #
        # redraw selected entities
        #
#        color = Color('#ff7733')
#        for obj in self.__image.getSelectedObjects(False):
#            obj.draw(self, color)
#        self.refresh()

#---------------------------------------------------------------------------------------------------
    def __draw_layer(self, layer, ctx):
        print "IViewport.__draw_layer()"
        # is it a layer object
        if not isinstance(layer, Layer):
            raise TypeError, "Invalid layer type: " + `type(layer)`
        # layer must belong to the image
        if layer.getParent() is not self.__image:
            raise ValueError, "Layer not found in Image"
        # only draw visible layers
        if layer.isVisible():
            color = self.__image.getOption('INACTIVE_LAYER_COLOR')
            if layer is self.__image.getActiveLayer():
                color = None
            # draw the points
            for obj in layer.getLayerEntities("point"):
                if obj.isVisible():
                    iobj = IPoint(ctx, obj)
                    iobj.draw(color)

    
#---------------------------------------------------------------------------------------------------