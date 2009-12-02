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

def one_shot_mid_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap mid
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('mid')
    
    
def one_shot_end_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap end
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('end')
    
    
def one_shot_intersection_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap intersection
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('intersection')
    
    
def one_shot_origin_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap origin
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('origin')
    

def one_shot_perpendicular_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap Perpendicular
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('perpendicular')
    
    
def one_shot_tangent_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap Tangent
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('tangent')
    
    
def one_shot_point_snap_cb(menuitem, gtkimage):
    """
        Activate one shot snap Point
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('point')

    
def one_shot_center_snap_cb(menuitem, gtkimage):
    """
        Activate one shut snap Center
    """
    gtkimage.image.snapProvider.setOneTemporarySnap('center')

    
    
#############################################################################
#
# class ISnapMenu
#
#############################################################################

class ISnapMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(ISnapMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Snap')
        self.gtkimage.addGroup(group)
        action = gtk.Action('SnapMenu', _('_Snap'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "SnapMenu object.")


#----------------------------------------------------------------------------------------------
#############################################################################
#   Top level snap menu
#############################################################################
    def __create_menu(self, actiongroup):
        _group = self.gtkimage.getGroup('Snap')
        _menu = gtk.Menu()
        #
        _act = gtk.Action('OneShotSnap', _('_One Shot Snap'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_snap_oneshot_menu(actiongroup))
        _menu.append(_item)
        return _menu

    
    def __create_snap_oneshot_menu(self, actiongroup):
        _group = self.gtkimage.getGroup('SnapOneShot')
        _menu = gtk.Menu()
        #
        _act = gtk.Action('MidPoint', _('_Mid Point'), None, None)
        _act.connect('activate', one_shot_mid_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('Point', _('_Point'), None, None)
        _act.connect('activate', one_shot_point_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('Center', _('_Center'), None, None)
        _act.connect('activate', one_shot_center_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)    
        #
        _act = gtk.Action('EndPoint', _('_End Point'), None, None)
        _act.connect('activate', one_shot_end_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('IntersectionPoint', _('_Intersection Point'), None, None)
        _act.connect('activate', one_shot_intersection_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('OriginPoint', _('_Origin Point'), None, None)
        _act.connect('activate', one_shot_origin_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('PerpendicularPoint', _('_Perpendicular Point'), None, None)
        _act.connect('activate', one_shot_perpendicular_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('TangentPoint', _('_Tangent Point'), None, None)
        _act.connect('activate', one_shot_tangent_snap_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _menu.append(_item)    
        return _menu
    
        

#############################################################################
#
# callbacks for the menu
#
#############################################################################

#----------------------------------------------------------------------------------------------
    def __menu_init_cb(self, menuitem):
        pass
               
               