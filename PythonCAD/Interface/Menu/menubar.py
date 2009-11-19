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

from PythonCAD.Interface.Menu.filemenu import IFileMenu
from PythonCAD.Interface.Menu.editmenu import IEditMenu
from PythonCAD.Interface.Menu.drawmenu import IDrawMenu
from PythonCAD.Interface.Menu.modifymenu import IModifyMenu
from PythonCAD.Interface.Menu.viewmenu import IViewMenu
from PythonCAD.Interface.Menu.snapmenu import ISnapMenu
from PythonCAD.Interface.Menu.dimensionmenu import IDimensionMenu
from PythonCAD.Interface.Menu.debugmenu import IDebugMenu



#############################################################################
#
# local functions
#
#############################################################################



#############################################################################
#
# class IMenuBar
#
#############################################################################

class IMenuBar(object):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        self.__gtkimage = parent
        self.__create_menubar()
        
        
    def __create_menubar(self):
        self.__mb = gtk.MenuBar()
        # File menu
        self.__file_menu = IFileMenu(self.__gtkimage)
        self.__mb.append(self.__file_menu.GtkMenu)
        # Edit menu
        self.__edit_menu = IEditMenu(self.__gtkimage)
        self.__mb.append(self.__edit_menu.GtkMenu)
        # Draw menu
        self.__draw_menu = IDrawMenu(self.__gtkimage)
        self.__mb.append(self.__draw_menu.GtkMenu)
        # Modify menu
        self.__modify_menu = IModifyMenu(self.__gtkimage)
        self.__mb.append(self.__modify_menu.GtkMenu)
        # View menu
        self.__view_menu = IViewMenu(self.__gtkimage)
        self.__mb.append(self.__view_menu.GtkMenu)
        # Snap menu
        self.__snap_menu = ISnapMenu(self.__gtkimage)
        self.__mb.append(self.__snap_menu.GtkMenu)
        # Dimension menu
        self.__dim_menu = IDimensionMenu(self.__gtkimage)
        self.__mb.append(self.__dim_menu.GtkMenu)
        # Debug menu
        self.__debug_menu = IDebugMenu(self.__gtkimage)
        self.__mb.append(self.__debug_menu.GtkMenu)
        
        
    # properties
    def __get_menubar(self):
        return self.__mb

    GtkMenuBar = property(__get_menubar, None, None, "MenuBar object.")
        
        
        