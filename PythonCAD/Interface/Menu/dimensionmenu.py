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

#from PythonCAD.Interface.Gtk.self.gtkimage import GTKImage
from PythonCAD.Interface.Gtk import gtkentities
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
from PythonCAD.Interface.Gtk import gtkDialog

from PythonCAD.Interface.Menu.basemenu import IBaseMenu


#############################################################################
#
# callbacks for the menu items
#
#############################################################################

def dimension_linear_cb(menuitem, gtkimage):
    _tool = tools.LinearDimensionTool()
    gtkimage.getImage().setTool(_tool)

    
def dimension_horizontal_cb(menuitem, gtkimage):
    _tool = tools.HorizontalDimensionTool()
    gtkimage.getImage().setTool(_tool)

    
def dimension_vertical_cb(menuitem, gtkimage):
    _tool = tools.VerticalDimensionTool()
    gtkimage.getImage().setTool(_tool)

    
def dimension_radial_cb(menuitem, gtkimage):
    _tool = tools.RadialDimensionTool()
    gtkimage.getImage().setTool(_tool)

    
def dimension_angular_cb(menuitem, gtkimage):
    _tool = tools.AngularDimensionTool()
    gtkimage.getImage().setTool(_tool)

    
#############################################################################
#
# class IDimensionMenu
#
#############################################################################

class IDimensionMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IDimensionMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Dimension')
        self.gtkimage.addGroup(group)
        action = gtk.Action('DimensionMenu', _('_Dimension'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "DimensionMenu object.")


#----------------------------------------------------------------------------------------------
#############################################################################
#   Top level snap menu
#############################################################################
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        _act = gtk.Action('Linear', _('_Linear'), None, None)
        _act.connect('activate', dimension_linear_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        _act = gtk.Action('Horizontal', _('_Horizontal'), None, None)
        _act.connect('activate', dimension_horizontal_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        _act = gtk.Action('Vertical', _('_Vertical'), None, None)
        _act.connect('activate', dimension_vertical_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        _act = gtk.Action('Radial', _('_Radial'), None, None)
        _act.connect('activate', dimension_radial_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        _act = gtk.Action('Angular', _('_Angular'), None, None)
        _act.connect('activate', dimension_angular_cb, self.gtkimage)
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
        _group = self.gtkimage.getGroup('Dimension')
        if _group is not None:
            _ldim = _hdim = _vdim = _rdim = _adim = False
            _count = 0
            _layers = [self.gtkimage.image.getTopLayer()]
            for _layer in _layers:
                _pc = _layer.getEntityCount('point')
                if _pc > 0:
                    _count = _count + _pc
                    if _count > 1:
                        _ldim = _hdim = _vdim = True
                    if _count > 2:
                        _adim = True
                if _layer.getEntityCount('circle') > 0:
                    _rdim = True
                if _layer.getEntityCount('arc') > 0:
                    _rdim = _adim = True
                if _ldim and _hdim and _vdim and _rdim and _adim:
                    break
                _layers.extend(_layer.getSublayers())
            _act = _group.get_action('Linear')
            if _act is not None:
                _act.set_property('sensitive', _ldim)
            _act = _group.get_action('Horizontal')
            if _act is not None:
                _act.set_property('sensitive', _hdim)
            _act = _group.get_action('Vertical')
            if _act is not None:
                _act.set_property('sensitive', _vdim)
            _act = _group.get_action('Radial')
            if _act is not None:
                _act.set_property('sensitive', _rdim)
            _act = _group.get_action('Angular')
            if _act is not None:
                _act.set_property('sensitive', _adim)
    
               
               