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

from PythonCAD.Interface.Gtk import gtkprefs
from PythonCAD.Interface.Gtk import gtkmodify
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
import  PythonCAD.Interface.Command as cmd

#############################################################################
#
# callbacks for the menu items
#
#############################################################################

def draw_point_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.PointTool()
    gtkimage.getImage().setTool(_tool)

def draw_segment_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.SegmentTool()
    gtkimage.getImage().setTool(_tool)

def draw_rectangle_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.RectangleTool()
    gtkimage.getImage().setTool(_tool)

def draw_circle_center_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_circle_tp_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TwoPointCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_arc_center_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ArcTool()
    gtkimage.getImage().setTool(_tool)

def draw_hcl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_vcl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.VCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_acl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ACLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_cl_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_perpendicular_cline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.PerpendicularCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_cline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TangentCLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_two_ccircles_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CCircleTangentLineTool()
    gtkimage.getImage().setTool(_tool)

def draw_poffset_cline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ParallelOffsetTool()
    gtkimage.getImage().setTool(_tool)

def draw_ccirc_cp_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.CCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_ccirc_tp_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TwoPointCCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_single_conobj_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TangentCCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_tangent_two_conobjs_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TwoPointTangentCCircleTool()
    gtkimage.getImage().setTool(_tool)

def draw_chamfer_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.ChamferTool()
    gtkimage.getImage().setTool(_tool)

def draw_fillet_cb(menuitem, gtkimage):
    """
        Start Point fillet comand
    """
    gtkimage.activateSnap()
    _tool = tools.FilletTool()
    gtkimage.getImage().setTool(_tool)
def draw_fillet_two_cb(menuitem, gtkimage):
    """
        Start two line fillet comand
    """
    _tool = tools.FilletTwoLineTool()
    gtkimage.getImage().setTool(_tool)
def draw_hatch_cb(menuitem,gtkimage):
    """
        Start the hatch command
    """
    _tool = tools.HatchTool()
    gtkimage.getImage().setTool(_tool)
    
def draw_leader_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.LeaderTool()
    gtkimage.getImage().setTool(_tool)

def draw_polyline_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.PolylineTool()
    gtkimage.getImage().setTool(_tool)

def _get_polygon_side_count(gtkimage):
    gtkimage.activateSnap()
    _sides = 0
    _window = gtkimage.getWindow()
    _dialog = gtk.Dialog(_('Polygon Sides'), _window,
                         gtk.DIALOG_MODAL,
                         (gtk.STOCK_OK, gtk.RESPONSE_OK,
                          gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
    _hbox = gtk.HBox(False, 10)
    _hbox.set_border_width(10)
    _dialog.vbox.pack_start(_hbox, False, False, 0)
    _stock = gtk.image_new_from_stock(gtk.STOCK_DIALOG_QUESTION,
                                      gtk.ICON_SIZE_DIALOG)
    _hbox.pack_start(_stock, False, False, 0)
    _label = gtk.Label(_('Number of sides:'))
    _hbox.pack_start(_label, False, False, 0)
    _adj = gtk.Adjustment(3, 3, 3600, 1, 1, 1) # arbitrary max ...
    _sb = gtk.SpinButton(_adj)
    _sb.set_numeric(True)
    _hbox.pack_start(_sb, True, True, 0)
    _dialog.show_all()
    _response = _dialog.run()
    if _response == gtk.RESPONSE_OK:
        _sides = _sb.get_value()
    _dialog.destroy()
    return _sides

def draw_polygon_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _sides = _get_polygon_side_count(gtkimage)
    if _sides > 0:
        _tool = tools.PolygonTool()
        _tool.setSideCount(_sides)
        gtkimage.getImage().setTool(_tool)

def draw_ext_polygon_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _sides = _get_polygon_side_count(gtkimage)
    if _sides > 0:
        _tool = tools.PolygonTool()
        _tool.setExternal()
        _tool.setSideCount(_sides)
        gtkimage.getImage().setTool(_tool)

def draw_set_style_cb(menuitem, gtkimage):
    cmd.set_active_style(gtkimage)

def draw_set_linetype_cb(menuitem, gtkimage):
    cmd.set_active_linetype(gtkimage)

def draw_set_color_cb(menuitem, gtkimage):
    cmd.set_active_color(gtkimage)

def draw_set_thickness_cb(menuitem, gtkimage):
    cmd.set_line_thickness(gtkimage)

def draw_text_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _text = cmd.text_add_dialog(gtkimage)
    if _text is not None:
        _tool = tools.TextTool()
        _tool.setText(_text)
        gtkimage.getImage().setTool(_tool)

def colors_cb(menuitem, gtkimage):
    cmd.set_colors_dialog(gtkimage)
        
        
def sizes_cb(menuitem, gtkimage):
    cmd.set_sizes_dialog(gtkimage)
    
def style_cb(menuitem, gtkimage):
    gtkstyleprefs.style_dialog(gtkimage, globals.prefs['STYLES'],
                               globals.prefs['LINETYPES'])
    
def textstyle_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    gtktextprefs.textstyle_dialog(gtkimage, globals.prefs['TEXTSTYLES'])

def dimstyle_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    gtkdimprefs.dimstyle_dialog(gtkimage, globals.prefs['DIMSTYLES'])

def toggle_cb(menuitem, gtkimage):
    cmd.set_toggle_dialog(gtkimage)
    
def units_cb(menuitem, gtkimage):
    cmd.set_units_dialog(gtkimage)
    
    
#############################################################################
#
# class IDrawMenu
#
#############################################################################

class IDrawMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IDrawMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Draw')
        self.gtkimage.addGroup(group)
        action = gtk.Action('DrawMenu', _('_Draw'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "DrawMenu object.")

#----------------------------------------------------------------------------------------------
    def __create_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('Basic', _('_Basic'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_draw_basic_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('ConLines', _('Con. _Lines'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_draw_conlines_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('ConCircs', _('Con. _Circs.'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_draw_concircs_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('Chamfers', _('Cha_mfer'), None, None)
        _act.connect('activate', draw_chamfer_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Fillets', _('_Fillets'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_draw_fillets_menu(actiongroup))
        _menu.append(_item)
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Hatch', _('Hatch'), None, None)
        _act.connect('activate', draw_hatch_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        #
        _act = gtk.Action('Leaders', _('Lea_der'), None, None)
        _act.connect('activate', draw_leader_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Polylines', _('_Polyline'), None, None)
        _act.connect('activate', draw_polyline_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('InternalPolygon', _('Poly_gon (Int.)'), None, None)
        _act.connect('activate', draw_polygon_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ExternalPolygon', _('Polygon (E_xt.)'), None, None)
        _act.connect('activate', draw_ext_polygon_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Textblocks', _('_Text'), None, None)
        _act.connect('activate', draw_text_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('SetProperties', _('_Set ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_draw_set_menu(actiongroup))
        _menu.append(_item)
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('AddNew', _('Add _New ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_add_new_menu(actiongroup))
        _menu.append(_item)
        #
        return _menu


    #############################################################################
    #  Draw -> basic sub-menu
    #############################################################################
    def __create_draw_basic_menu(self, actiongroup):
        # _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        #
        _act = gtk.Action('Points', _('_Point'), None, None)
        _act.connect('activate', draw_point_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Segments', _('_Segment'), None, None)
        _act.connect('activate', draw_segment_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Rectangles', _('_Rectangle'), None, None)
        _act.connect('activate', draw_rectangle_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Circles', _('_Circle'), None, None)
        _act.connect('activate', draw_circle_center_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('CirclesTwoPoints', _('Circle (_2 Pts)'), None, None)
        _act.connect('activate', draw_circle_tp_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Arcs', _('_Arc'), None, None)
        _act.connect('activate', draw_arc_center_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu


    #############################################################################
    #  Draw -> lines sub-menu
    #############################################################################
    def __create_draw_conlines_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('HCLines', _('_Horizontal'), None, None)
        _act.connect('activate', draw_hcl_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('VCLines', _('_Vertical'), None, None)
        _act.connect('activate', draw_vcl_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ACLines', _('_Angled'), None, None)
        _act.connect('activate', draw_acl_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('CLines', _('_Two-Point'), None, None)
        _act.connect('activate', draw_cl_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('PerpConLines', _('Per_pendicular'), None, None)
        _act.connect('activate', draw_perpendicular_cline_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ParallelConLines', _('Para_llel'), None, None)
        _act.connect('activate', draw_poffset_cline_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('TangentConLines', _('_Tangent'), None, None)
        _act.connect('activate', draw_tangent_cline_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('TangentTwoCirclesConLines', _('Tangent _2 Circ'),
                          None, None)
        _act.connect('activate', draw_tangent_two_ccircles_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu


    #############################################################################
    #  Draw -> concentric circles sub-menu
    #############################################################################
    def __create_draw_concircs_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('CCircles', _('_Center Pt.'), None, None)
        _act.connect('activate', draw_ccirc_cp_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('CCirclesTwoPoints', _('_Two Pts.'), None, None)
        _act.connect('activate', draw_ccirc_tp_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('CCircleTangentSingle', _('_Single Tangency'),
                          None, None)
        _act.connect('activate', draw_tangent_single_conobj_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('CCircleTangentDual', _('_Dual Tangency'), None, None)
        _act.connect('activate', draw_tangent_two_conobjs_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu


    #############################################################################
    #  Draw set style sub-menu
    #############################################################################
    def __create_draw_set_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        # _act = gtk.Action('SetStyle', _('_Style'), None, None)
        # _act.connect('activate', draw_set_style_cb, self.gtkimage)
        # actiongroup.add_action(_act)
        # _menu.append(_act.create_menu_item())
        #
        # _act = gtk.Action('SetLinetype', _('_Linetype'), None, None)
        # _act.connect('activate', draw_set_linetype_cb, self.gtkimage)
        # actiongroup.add_action(_act)
        # _menu.append(_act.create_menu_item())
        #
        # _act = gtk.Action('SetColor', _('_Color'), None, None)
        # _act.connect('activate', draw_set_color_cb, self.gtkimage)
        # actiongroup.add_action(_act)
        # _menu.append(_act.create_menu_item())
        #
        # _act = gtk.Action('SetThickness', _('_Thickness'), None, None)
        # _act.connect('activate', draw_set_thickness_cb, self.gtkimage)
        # actiongroup.add_action(_act)
        # _menu.append(_act.create_menu_item())
        #
        # _item = gtk.SeparatorMenuItem()
        # _item.show()
        # _menu.append(_item)
        #
        _act = gtk.Action('SetImageColors', _('_Colors'), None, None)
        _act.connect('activate', colors_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('SetImageSizes', _('_Sizes'), None, None)
        _act.connect('activate', sizes_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('SetGraphicsStyle', _('_Style'), None, None)
        _act.connect('activate', style_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('SetTextStyle', _('_TextStyle'), None, None)
        _act.connect('activate', textstyle_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('SetDimStyle', _('_DimStyle'), None, None)
        _act.connect('activate', dimstyle_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('SetImageOps', _('_Display'), None, None)
        _act.connect('activate', toggle_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        _act = gtk.Action('SetImageUnits', _('_Units'), None, None)
        _act.connect('activate', units_cb, self.gtkimage)
        _item = _act.create_menu_item()
        _menu.append(_item)
        #
        return _menu


    #############################################################################
    #  Draw-> Fillet sub menu .  .
    #############################################################################
    def __create_draw_fillets_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('PointFillet', _('_Point..'), None, None)
        _act.connect('activate', draw_fillet_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('TwoLineFillet', _('_Two Line'), None, None)
        _act.connect('activate', draw_fillet_two_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        return _menu


    #############################################################################
    #  Draw . . .  .
    #############################################################################
    def __create_add_new_menu(self, actiongroup):
        #
        # These currently do nothing but are present to encourage
        # the development of code to make the ability to add and
        # save new styles and linetypes in drawings ...
        #
        _menu = gtk.Menu()
        #
        _act = gtk.Action('AddStyle', _('Style'), None, None)
        _act.set_property('sensitive', False)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('AddLinetype', _('Linetype'), None, None)
        _act.set_property('sensitive', False)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu




#############################################################################
#
# callbacks for the menu
#
#############################################################################

#----------------------------------------------------------------------------------------------
    def __menu_init_cb(self, menuitem):
        pass


