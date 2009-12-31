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
import os
import pygtk
pygtk.require('2.0')
import gtk
from gtk import gdk

from PythonCAD.Generic.point import Point
from PythonCAD.Interface.Viewport.viewstate import ViewState
from PythonCAD.Interface.Viewport.zoomtool import ZoomTool

pix_data = """/* XPM */
static char * invisible_xpm[] = {
"1 1 1 1",
"       c None",
" "};"""

#pix_data = []
#pix_data.append("1 1 1 1")
#pix_data.append("       c None")
#pix_data.append(" ")




class IInputHandler(gtk.DrawingArea):

#---------------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IInputHandler, self).__init__()
        # parent is gtk image
        self._gtkimage = parent
        self._image = self._gtkimage.getImage()
        # state of the view (what to draw)
        self._view_state = ViewState()
        # zoom tool
        self._zoom_tool = ZoomTool(self)
        # current position in view coordinates
        self._cur_vx = 0.0
        self._cur_vy = 0.0
        # current position in world coordinates
        self._cur_wx = 0.0
        self._cur_wy = 0.0
        # view window size
        self._vxmin = 0
        self._vymin = 0
        self._vxmax = 0
        self._vymax = 0
        self._vwidth = 0
        self._vheight = 0
        # world window size
        self._wxmin = 0
        self._wymin = 0
        self._wxmax = 1
        self._wymax = 1
        self._wwidth = 1
        self._wheight = 1
        # graphics context
        self._gc = None
        # pixmap scale factor (1=viewport size, 2=twice the size, 3=even larger)
        self.__px_scale_factor = 2
        # cairo translate factors
        self.__dx = 0.0
        self.__dy = 0.0
        # cairo scale factors
        self.__sx = 1.0
        self.__sy = 1.0
        # vertical exaggeration
        self.__vert_exaggeration = 1.0
        # event handlers
        self.connect("event", self.__input_event)
        self.connect("expose_event", self.__expose_event)
        self.connect("realize", self.__realize_event)
        # events masks
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

#---------------------------------------------------------------------------------------------------
    def __get_gtk_image(self):
        return self._gtkimage
    
    gtk_image = property(__get_gtk_image, None, None, "Get the GtkImage class")

#---------------------------------------------------------------------------------------------------
    def __get_image(self):
        return self._image
    
    image = property(__get_image, None, None, "Get the Image class")

#---------------------------------------------------------------------------------------------------
    def __get_view_state(self):
        return self._view_state
    
    view_state = property(__get_view_state, None, None, "Get the view state")

#---------------------------------------------------------------------------------------------------
    def __get_zoom_tool(self):
        return self._zoom_tool

    zoom_tool = property(__get_zoom_tool, None, None, "Get the zoom tool")
    
#---------------------------------------------------------------------------------------------------
    def __get_cur_world_pos(self):
        return Point(self._cur_wx, self._cur_wy)
    
    world_pos = property(__get_cur_world_pos, None, None, "Get the pointer position")

#---------------------------------------------------------------------------------------------------
    def __realize_event(self, widget, data=None):
        # create a graphic context if not exists
        self._gc = self.window.new_gc()
        
#---------------------------------------------------------------------------------------------------
    def __expose_event(self, widget, event, data=None):
        # view dimension
        self._vxmin, self._vymin, width, height = event.area
        self._vxmax = self._vxmin + width
        self._vymax = self._vymin + height
        # if expose is called for the first time then do a fit
        if not self._view_state.initialized:
            self._zoom_tool.zoom_fit()
            self._view_state.initialized = True
        else:
            self._refresh()
        return True

#---------------------------------------------------------------------------------------------------
    def __input_event(self, widget, event, data=None):
        retval = False
        event_type = event.type
        tool = self._image.getTool()

        if event_type == 31:
            if event.direction == gtk.gdk.SCROLL_UP:
                self._zoom_tool.zoom_wheel_in()
            if event.direction == gtk.gdk.SCROLL_DOWN:
                self._zoom_tool.zoom_wheel_out()
                
        if event_type == 12:
            pass
        
        if event_type == gtk.gdk.BUTTON_PRESS:
            self._set_tool_point(event.x, event.y)
            _button = event.button
            if _button == 1:
                if tool is not None and tool.hasHandler("button_press"):
                    retval = tool.getHandler("button_press")(self._gtkimage, widget, event, tool)
            #self.__Move(widget, event)

        elif event_type == gtk.gdk.BUTTON_RELEASE:
            self._set_tool_point(event.x, event.y)
            _button = event.button
            if _button == 1:
                if tool is not None and tool.hasHandler("button_release"):
                    retval = tool.getHandler("button_release")(self._gtkimage, widget, event, tool)
            #self._gtkimage.__Move(widget, event)
        # mouse move
        elif event_type == gtk.gdk.MOTION_NOTIFY:
            # update point in current tool
            self._set_tool_point(event.x, event.y)
            # motion update for tool
            if tool is not None and tool.hasHandler("motion_notify"):
                retval = tool.getHandler('motion_notify')(self._gtkimage, widget, event, tool)
#            self._gtkimage.__MakeMove(widget,event)
#            self._gtkimage.__ActiveSnapEvent(widget,event)
#
#            if self._view_state.current == self._view_state.Pan:
#                self._do_pan(event.x, event.y)
#            else:
#                self._set_tool_point(event.x, event.y)
        
        elif event_type == gtk.gdk.KEY_PRESS:
            _key = event.keyval
            if (_key == gtk.keysyms.Page_Up or
                _key == gtk.keysyms.Page_Down or
                _key == gtk.keysyms.Left or
                _key == gtk.keysyms.Right or
                _key == gtk.keysyms.Up or
                _key == gtk.keysyms.Down):
                #KeyMoveDrawing(_key) # Matteo Boscolo 12-05-2009
                pass # handle moving the drawing in some fashion ...
            elif _key == gtk.keysyms.Escape:
                self.reset()
                retval = True
            elif tool is not None and tool.hasHandler("key_press"):
                retval = tool.getHandler("key_press")(self._gtkimage, widget, event, tool)
            else:
                _entry = self.__entry
                _entry.grab_focus()
                if _key == gtk.keysyms.Tab:
                    retval = True
                else:
                    retval = _entry.event(event)
        elif event_type == gtk.gdk.ENTER_NOTIFY:
            self._set_tool_point(event.x, event.y)
            retval = True
        elif event_type == gtk.gdk.LEAVE_NOTIFY:
            self._set_tool_point(event.x, event.y)
            retval = True
        else:
            pass
        return retval

#---------------------------------------------------------------------------------------------------
    def __get_wxmin(self):
        return self._wxmin

    def __set_wxmin(self, value):
        self._wxmin = value

    world_x_min = property(__get_wxmin, __set_wxmin, None, "World x-min point")

#---------------------------------------------------------------------------------------------------
    def __get_wxmax(self):
        return self._wxmax

    def __set_wxmax(self, value):
        self._wxmax = value

    world_x_max = property(__get_wxmax, __set_wxmax, None, "World x-max point")

#---------------------------------------------------------------------------------------------------
    def __get_wymin(self):
        return self._wymin

    def __set_wymin(self, value):
        self._wymin = value

    world_y_min = property(__get_wymin, __set_wymin, None, "World y-min point")

#---------------------------------------------------------------------------------------------------
    def __get_wymax(self):
        return self._wymax

    def __set_wymax(self, value):
        self._wymax = value

    world_y_max = property(__get_wymax, __set_wymax, None, "World y-max point")

#---------------------------------------------------------------------------------------------------
    def __get_image(self):
        return self._image

    gimage = property(__get_image, None, None, "Generic Image")
    
#---------------------------------------------------------------------------------------------------
    def _set_tool_point(self, x, y):
        #print "IInputHandler._set_tool_point"
        # view position
        self._cur_vx = x
        self._cur_vy = y
        # world position
        self._cur_wx, self._cur_wy = self.view_to_world(self._cur_vx, self._cur_vy)
        self._image.setCurrentPoint(self._cur_wx, self._cur_wy)
        # if the state is None redraw the cursor
        if self._view_state.current == self._view_state.None:
            # redraw cursor
            self._view_state.current = self._view_state.CursorMotion
            self.invalidate()
        
#---------------------------------------------------------------------------------------------------
    def _calc_viewfactors(self):
        # viewport width and height
        self._vwidth = self._vxmax - self._vxmin
        self._vheight = self._vymax - self._vymin
        if self._vwidth > 0 and self._vheight > 0:
            # world width and height
            self._wwidth = self._wxmax - self._wxmin
            self._wheight = self._wymax - self._wymin
            # translation
            self.__dx = self._wxmin
            self.__dy = self._wymin
            # scale factor
            sx = 1.0 * self._vwidth / self._wwidth
            sy = 1.0 * self._vheight / self._wheight
            self.__sx = min(sx, sy)
            self.__sy = self.__sx * self.__vert_exaggeration
            # visible world area
            self._wxmax = self._wxmin + self.size_view_to_world(self._vwidth)
            self._wymax = self._wymin + self.size_view_to_world(self._vheight)
            # redraw
            self._view_state.current = self._view_state.DrawScene
            self.invalidate()

#---------------------------------------------------------------------------------------------------
    def world_to_view(self, x, y):
        ##print "Point (world): ", x, y
        _x = (x - self.__dx) * self.__sx
        _y = self._vheight - ((y - self.__dy) * self.__sy)
        ##print "Point (view): ", _x, _y
        return _x, _y

#---------------------------------------------------------------------------------------------------
    def view_to_world(self, x, y):
        ##print "Point (view): ", x, y
        _x = (x / self.__sx) + self.__dx
        _y = ((self._vheight - y) / self.__sy) + self.__dy
        ##print "Point (world): ", _x, _y
        return _x, _y

#---------------------------------------------------------------------------------------------------
    def size_world_to_view(self, size):
        ##print "Size (world): ", size
        _size = size * self.__sx
        return _size
    
#---------------------------------------------------------------------------------------------------
    def size_view_to_world(self, size):
        ##print "Size (view): ", size
        _size = size / self.__sx
        return _size
            
#---------------------------------------------------------------------------------------------------
    def invalidate(self):
        ##print "IViewport.invalidate()"
        if self.window:
            alloc = self.get_allocation()
            rect = gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)
            self.window.process_updates(True)
            
#---------------------------------------------------------------------------------------------------
    def _do_pan(self, x, y):
        #print "IInputHandler._do_pan()"
        pass
      
#---------------------------------------------------------------------------------------------------
    def _refresh(self):
        pass
