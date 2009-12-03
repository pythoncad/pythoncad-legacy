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

import pygtk
pygtk.require('2.0')
import gtk
import gtk.keysyms

#from PythonCAD.Interface.Gtk.gtkimage import GTKImage

from PythonCAD.Interface.Gtk import gtkprefs
from PythonCAD.Interface.Gtk import gtkmodify
from PythonCAD.Interface.Gtk import gtktext
from PythonCAD.Interface.Gtk import gtkprinting
from PythonCAD.Interface.Gtk import gtkactions
from PythonCAD.Generic import globals
from PythonCAD.Generic import fileio
from PythonCAD.Generic import imageio
from PythonCAD.Generic import tools
from PythonCAD.Generic import plotfile
from PythonCAD.Generic import text
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import dimension
from PythonCAD.Generic import extFormat

from PythonCAD.Generic.image import Image
from PythonCAD.Interface.Gtk import gtkdimprefs
from PythonCAD.Interface.Gtk import gtktextprefs
from PythonCAD.Interface.Gtk import gtkstyleprefs
from PythonCAD.Interface.Gtk import gtkdialog as gtkDialog

from PythonCAD.Interface.Menu.basemenu import IBaseMenu


#############################################################################
#
# callbacks for the menu items
#
#############################################################################

def zoom_cb(menuitem, gtkimage):
    _tool = tools.ZoomTool()
    gtkimage.getImage().setTool(_tool)
    

def zoom_in_cb(menuitem, gtkimage):
    #_xmin, _ymin, _xmax, _ymax = gtkimage.getView()
    #_scale = gtkimage.getUnitsPerPixel()
    #_xdiff = abs(_xmax - _xmin)
    #_ydiff = abs(_ymax - _ymin)
    #_xmin = (_xmin + _xmax)/2.0 - _xdiff/4.0
    #_ymin = (_ymin + _ymax)/2.0 - _ydiff/4.0
    #gtkimage.setView(_xmin, _ymin, (_scale/2.0))
    ActiveScale = gtkimage.getUnitsPerPixel()
    ActiveScale = ActiveScale*0.5 #This Value here could be a global variable to put in the application option
    gtkimage.ZoomScale(ActiveScale)
    
    
def zoom_out_cb(menuitem, gtkimage):
    #_xmin, _ymin, _xmax, _ymax = gtkimage.getView()
    #_scale = gtkimage.getUnitsPerPixel()
    #_xdiff = abs(_xmax - _xmin)
    #_ydiff = abs(_ymax - _ymin)
    #_xmin = (_xmin + _xmax)/2.0 - _xdiff
    #_ymin = (_ymin + _ymax)/2.0 - _ydiff
    #gtkimage.setView(_xmin, _ymin, (_scale * 2.0))
    ActiveScale = gtkimage.getUnitsPerPixel()
    ActiveScale = ActiveScale*2 #This Value here could be a global variable to put in the application option
    gtkimage.ZoomScale(ActiveScale)
    
    
def zoom_fit_cb(menuitem, gtkimage):
    gtkimage.fitImage()
    
    
def zoom_pan_cb(menuitem, gtkimage):
    _tool = tools.ZoomPan()
    gtkimage.getImage().setTool(_tool)

    
    
#############################################################################
#
# class IViewMenu
#
#############################################################################

class IViewMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IViewMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('View')
        self.gtkimage.addGroup(group)
        action = gtk.Action('ViewMenu', _('_View'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "ViewMenu object.")


#----------------------------------------------------------------------------------------------
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ZoomIn', _('_Zoom In'), None, gtk.STOCK_ZOOM_IN)
        _act.connect('activate', zoom_in_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('ZoomOut', _('Zoom _Out'), None, gtk.STOCK_ZOOM_OUT)
        _act.connect('activate', zoom_out_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('ZoomFit', _('Zoom _Fit'), None, gtk.STOCK_ZOOM_FIT)
        _act.connect('activate', zoom_fit_cb, self.gtkimage)
        _act.set_accel_group(_accel)
        actiongroup.add_action_with_accel(_act, None)
        _item = _act.create_menu_item()
        if isinstance(_act, gtkactions.stdAction):
            _add_accelerators(_act, _item, _accel)
        _menu.append(_item)
        #
        _act = gtk.Action('ZoomPan', _('Zoom _Pan'), None, None)
        _act.connect('activate', zoom_pan_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ZoomWindow', _('Zoom _Window'), None, None)
        _act.connect('activate', zoom_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        return _menu

        

#############################################################################
#
# callbacks for the menu
#
#############################################################################

#----------------------------------------------------------------------------------------------
    def __menu_init_cb(self, menuitem):
        _group = self.gtkimage.getGroup('View')
        if _group is not None:
            _image = self.gtkimage.getImage()
            _active = _image.getActiveLayer()
            _act = _group.get_action('ZoomFit')
            if _act is not None:
                _act.set_property('sensitive', _active.hasEntities())
               
               