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


from PythonCAD.Interface.Preferences import gtkprefs
from PythonCAD.Interface.Gtk import gtkmodify
from PythonCAD.Interface.Gtk import gtkprinting
from PythonCAD.Interface.Gtk import gtkactions
from PythonCAD.Generic import globals
from PythonCAD.Generic import fileio
from PythonCAD.Generic import imageio
from PythonCAD.Generic.Tools import *
from PythonCAD.Generic import plotfile
from PythonCAD.Generic import text
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import dimension
from PythonCAD.Generic import extFormat

from PythonCAD.Generic.image import Image
from PythonCAD.Interface.Preferences import gtkdimprefs
from PythonCAD.Interface.Preferences import gtktextprefs
from PythonCAD.Interface.Preferences import gtkstyleprefs
from PythonCAD.Interface.Gtk import gtkdialog as gtkDialog

from PythonCAD.Interface.Menu.basemenu import IBaseMenu


#############################################################################
#
# local functions
#
#############################################################################


#############################################################################
#
# callback functions
#
#############################################################################

def move_horizontal_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HorizontalMoveTool()
    gtkimage.getImage().setTool(_tool)

def move_vertical_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.VerticalMoveTool()
    gtkimage.getImage().setTool(_tool)

def move_twopoint_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.MoveTool()
    gtkimage.getImage().setTool(_tool)

def stretch_horiz_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.HorizontalStretchTool()
    gtkimage.getImage().setTool(_tool)

def stretch_vert_cb(menuitem, gtkimage):
    _tool = tools.VerticalStretchTool()
    gtkimage.getImage().setTool(_tool)

def stretch_twopoint_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.StretchTool()
    gtkimage.getImage().setTool(_tool)

def transfer_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.TransferTool()
    gtkimage.getImage().setTool(_tool)

def rotate_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.RotateTool()
    gtkimage.getImage().setTool(_tool)
    
def split_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.SplitTool()
    gtkimage.getImage().setTool(_tool)

def mirror_object_cb(menuitem, gtkimage):
    gtkimage.activateSnap()
    _tool = tools.MirrorTool()
    gtkimage.getImage().setTool(_tool)

def delete_cb(menuitem, gtkimage):
    _tool = tools.DeleteTool()
    gtkimage.getImage().setTool(_tool)

def change_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_style_dialog(gtkimage)
    if _st is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setStyle')
        _tool.setValue(_st)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_style_init(gtkimage)

def change_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_color_dialog(gtkimage)
    if _color is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setColor')
        _tool.setValue(_color)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_color_init(gtkimage)

def change_linetype_cb(menuitem, gtkimage):
    _lt = gtkmodify.change_linetype_dialog(gtkimage)
    if _lt is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setLinetype')
        _tool.setValue(_lt)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_linetype_init(gtkimage)

def change_thickness_cb(menuitem, gtkimage):
    _t = gtkmodify.change_thickness_dialog(gtkimage)
    if _t is not None:
        _tool = tools.GraphicObjectTool()
        _tool.setAttribute('setThickness')
        _tool.setValue(_t)
        _tool.setObjtype(graphicobject.GraphicObject)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_thickness_init(gtkimage)

def change_textblock_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_textblock_style_dialog(gtkimage, 'FONT_STYLE')
    if _st is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setStyle')
        _tool.setValue(_st)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_style_init(gtkimage)

def change_textblock_weight_cb(menuitem, gtkimage):
    _w = gtkmodify.change_textblock_weight_dialog(gtkimage, 'FONT_WEIGHT')
    if _w is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setWeight')
        _tool.setValue(_w)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_weight_init(gtkimage)

def change_textblock_alignment_cb(menuitem, gtkimage):
    _align = gtkmodify.change_textblock_alignment_dialog(gtkimage, 'TEXT_ALIGNMENT')
    if _align is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setAlignment')
        _tool.setValue(_align)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_alignment_init(gtkimage)

def change_textblock_size_cb(menuitem, gtkimage):
    _size = gtkmodify.change_textblock_size_dialog(gtkimage, 'TEXT_SIZE')
    if _size is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setSize')
        _tool.setValue(_size)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_size_init(gtkimage)

def change_textblock_family_cb(menuitem, gtkimage):
    _family = gtkmodify.change_textblock_family_dialog(gtkimage, 'FONT_FAMILY')
    if _family is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setFamily')
        _tool.setValue(_family)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_family_init(gtkimage)

def change_textblock_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_textblock_color_dialog(gtkimage, 'FONT_COLOR')
    if _color is not None:
        _tool = tools.TextTool()
        _tool.setAttribute('setColor')
        _tool.setValue(_color)
        _tool.setObjtype(text.TextBlock)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_textblock_color_init(gtkimage)

def change_dim_endpoint_cb(menuitem, gtkimage):
    _et = gtkmodify.change_dim_endpoint_dialog(gtkimage)
    if _et is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setEndpointType')
        _tool.setValue(_et)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_endpoint_init(gtkimage)

def change_dim_endpoint_size_cb(menuitem, gtkimage):
    _es = gtkmodify.change_dim_endpoint_size_dialog(gtkimage)
    if _es is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setEndpointSize')
        _tool.setValue(_es)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_endpoint_size_init(gtkimage)

def change_dim_offset_cb(menuitem, gtkimage):
    _offset = gtkmodify.change_dim_offset_dialog(gtkimage)
    if _offset is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setOffset')
        _tool.setValue(_offset)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_offset_init(gtkimage)

def change_dim_extension_cb(menuitem, gtkimage):
    _ext = gtkmodify.change_dim_extension_dialog(gtkimage)
    if _ext is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setExtension')
        _tool.setValue(_ext)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_extension_init(gtkimage)

def change_dim_dual_mode_cb(menuitem, gtkimage):
    _ddm = gtkmodify.change_dim_dual_mode_dialog(gtkimage)
    if _ddm is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setDualDimMode')
        _tool.setValue(_ddm)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_dual_mode_init(gtkimage)

def change_dim_dual_mode_offset_cb(menuitem, gtkimage):
    _dmo = gtkmodify.change_dim_dual_mode_offset_dialog(gtkimage)
    if _dmo is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setDualModeOffset')
        _tool.setValue(_dmo)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_dual_mode_offset_init(gtkimage)

def change_dim_thickness_cb(menuitem, gtkimage):
    _t = gtkmodify.change_dim_thickness_dialog(gtkimage)
    if _t is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setThickness')
        _tool.setValue(_t)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_thickness_init(gtkimage)

def change_dim_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_dim_color_dialog(gtkimage)
    if _color is not None:
        _tool = tools.EditDimensionTool()
        _tool.setAttribute('setColor')
        _tool.setValue(_color)
        _tool.setObjtype(dimension.Dimension)
        gtkimage.getImage().setTool(_tool)
        gtkmodify.change_dim_color_init(gtkimage)

def _change_dimstring_style_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setStyle')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_style_init(gtkimage)

def change_dim_primary_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_textblock_style_dialog(gtkimage, 'DIM_PRIMARY_FONT_STYLE')
    if _st is not None:
        _change_dimstring_style_cb(gtkimage, _st, True)

def change_dim_secondary_style_cb(menuitem, gtkimage):
    _st = gtkmodify.change_textblock_style_dialog(gtkimage, 'DIM_SECONDARY_FONT_STYLE')
    if _st is not None:
        _change_dimstring_style_cb(gtkimage, _st, False)

def _change_dimstring_family_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setFamily')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_family_init(gtkimage)

def change_dim_primary_family_cb(menuitem, gtkimage):
    _family = gtkmodify.change_textblock_family_dialog(gtkimage, 'DIM_PRIMARY_FONT_FAMILY')
    if _family is not None:
        _change_dimstring_family_cb(gtkimage, _family, True)

def change_dim_secondary_family_cb(menuitem, gtkimage):
    _family = gtkmodify.change_textblock_family_dialog(gtkimage, 'DIM_SECONDARY_FONT_FAMILY')
    if _family is not None:
        _change_dimstring_family_cb(gtkimage, _family, False)

def _change_dimstring_weight_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setWeight')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_weight_init(gtkimage)

def change_dim_primary_weight_cb(menuitem, gtkimage):
    _weight = gtkmodify.change_textblock_weight_dialog(gtkimage, 'DIM_PRIMARY_FONT_WEIGHT')
    if _weight is not None:
        _change_dimstring_weight_cb(gtkimage, _weight, True)

def change_dim_secondary_weight_cb(menuitem, gtkimage):
    _weight = gtkmodify.change_textblock_weight_dialog(gtkimage, 'DIM_SECONDARY_FONT_WEIGHT')
    if _weight is not None:
        _change_dimstring_weight_cb(gtkimage, _weight, False)

def _change_dimstring_size_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setSize')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_size_init(gtkimage)

def change_dim_primary_size_cb(menuitem, gtkimage):
    _size = gtkmodify.change_textblock_size_dialog(gtkimage, 'DIM_PRIMARY_TEXT_SIZE')
    if _size is not None:
        _change_dimstring_size_cb(gtkimage, _size, True)

def change_dim_secondary_size_cb(menuitem, gtkimage):
    _size = gtkmodify.change_textblock_size_dialog(gtkimage, 'DIM_SECONDARY_TEXT_SIZE')
    if _size is not None:
        _change_dimstring_size_cb(gtkimage, _size, False)

def _change_dimstring_color_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setColor')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_color_init(gtkimage)

def change_dim_primary_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_textblock_color_dialog(gtkimage, 'DIM_PRIMARY_FONT_COLOR')
    if _color is not None:
        _change_dimstring_color_cb(gtkimage, _color, True)

def change_dim_secondary_color_cb(menuitem, gtkimage):
    _color = gtkmodify.change_textblock_color_dialog(gtkimage, 'DIM_SECONDARY_FONT_COLOR')
    if _color is not None:
        _change_dimstring_color_cb(gtkimage, _color, False)

def _change_dimstring_alignment_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setAlignment')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_alignment_init(gtkimage)

def change_dim_primary_alignment_cb(menuitem, gtkimage):
    _align = gtkmodify.change_textblock_alignment_dialog(gtkimage, 'DIM_PRIMARY_TEXT_ALIGNMENT')
    if _align is not None:
        _change_dimstring_alignment_cb(gtkimage, _align, True)

def change_dim_secondary_alignment_cb(menuitem, gtkimage):
    _align = gtkmodify.change_textblock_alignment_dialog(gtkimage, 'DIM_SECONDARY_TEXT_ALIGNMENT')
    if _align is not None:
        _change_dimstring_alignment_cb(gtkimage, _align, False)

def _change_dimstring_prefix_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrefix')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)

def change_ldim_pds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'DIM_PRIMARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, True)
        gtkmodify.change_ldimstr_prefix_init(gtkimage)

def change_ldim_sds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'DIM_SECONDARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, False)
        gtkmodify.change_ldimstr_prefix_init(gtkimage)

def change_rdim_pds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'RADIAL_DIM_PRIMARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, True)
        gtkmodify.change_rdimstr_prefix_init(gtkimage)

def change_rdim_sds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'RADIAL_DIM_SECONDARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, False)
        gtkmodify.change_rdimstr_prefix_init(gtkimage)

def change_adim_pds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'ANGULAR_DIM_PRIMARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, True)
        gtkmodify.change_adimstr_prefix_init(gtkimage)

def change_adim_sds_prefix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_prefix_dialog(gtkimage, 'ANGULAR_DIM_SECONDARY_PREFIX')
    if _text is not None:
        _change_dimstring_prefix_cb(gtkimage, _text, False)
        gtkmodify.change_adimstr_prefix_init(gtkimage)

def _change_dimstring_suffix_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setSuffix')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)

def change_ldim_pds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'DIM_PRIMARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, True)
        gtkmodify.change_ldimstr_suffix_init(gtkimage)

def change_ldim_sds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'DIM_SECONDARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, False)
        gtkmodify.change_ldimstr_suffix_init(gtkimage)

def change_rdim_pds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'RADIAL_DIM_PRIMARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, True)
        gtkmodify.change_rdimstr_suffix_init(gtkimage)

def change_rdim_sds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'RADIAL_DIM_SECONDARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, False)
        gtkmodify.change_rdimstr_suffix_init(gtkimage)

def change_adim_pds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'ANGULAR_DIM_PRIMARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, True)
        gtkmodify.change_adimstr_suffix_init(gtkimage)

def change_adim_sds_suffix_cb(menuitem, gtkimage):
    _text = gtkmodify.change_dimstr_suffix_dialog(gtkimage, 'ANGULAR_DIM_SECONDARY_SUFFIX')
    if _text is not None:
        _change_dimstring_suffix_cb(gtkimage, _text, False)
        gtkmodify.change_adimstr_suffix_init(gtkimage)

def _change_dimstring_precision_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrecision')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_precision_init(gtkimage)

def change_dim_primary_precision_cb(menuitem, gtkimage):
    _prec = gtkmodify.change_dimstr_precision_dialog(gtkimage, 'DIM_PRIMARY_PRECISION')
    if _prec is not None:
        _change_dimstring_precision_cb(gtkimage, _prec, True)

def change_dim_secondary_precision_cb(menuitem, gtkimage):
    _prec = gtkmodify.change_dimstr_precision_dialog(gtkimage, 'DIM_SECONDARY_PRECISION')
    if _prec is not None:
        _change_dimstring_precision_cb(gtkimage, _prec, False)

def _change_dimstring_units_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setUnits')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_units_init(gtkimage)

def change_dim_primary_units_cb(menuitem, gtkimage):
    _unit = gtkmodify.change_dimstr_units_dialog(gtkimage, 'DIM_PRIMARY_UNITS')
    if _unit is not None:
        _change_dimstring_units_cb(gtkimage, _unit, True)

def change_dim_secondary_units_cb(menuitem, gtkimage):
    _unit = gtkmodify.change_dimstr_units_dialog(gtkimage, 'DIM_SECONDARY_UNITS')
    if _unit is not None:
        _change_dimstring_units_cb(gtkimage, _unit, False)

def _change_dimstring_print_zero_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrintZero')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_print_zero_init(gtkimage)

def change_dim_primary_print_zero_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_zero_dialog(gtkimage, 'DIM_PRIMARY_LEADING_ZERO')
    if _flag is not None:
        _change_dimstring_print_zero_cb(gtkimage, _flag, True)

def change_dim_secondary_print_zero_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_zero_dialog(gtkimage, 'DIM_SECONDARY_LEADING_ZERO')
    if _flag is not None:
        _change_dimstring_print_zero_cb(gtkimage, _flag, False)

def _change_dimstring_print_decimal_cb(gtkimage, val, flag):
    _tool = tools.EditDimStringTool()
    _tool.setAttribute('setPrintDecimal')
    _tool.setValue(val)
    _tool.setPrimary(flag)
    _tool.setObjtype(dimension.DimString)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_dimstr_print_decimal_init(gtkimage)

def change_dim_primary_print_decimal_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_decimal_dialog(gtkimage, 'DIM_PRIMARY_TRAILING_DECIMAL')
    if _flag is not None:
        _change_dimstring_print_decimal_cb(gtkimage, _flag, True)

def change_dim_secondary_print_decimal_cb(menuitem, gtkimage):
    _flag = gtkmodify.change_dimstr_print_decimal_dialog(gtkimage, 'DIM_SECONDARY_TRAILING_DECIMAL')
    if _flag is not None:
        _change_dimstring_print_decimal_cb(gtkimage, _flag, False)

def change_rdim_dia_mode_cb(menuitem, gtkimage):
    _tool = tools.EditDimensionTool()
    _tool.setObjtype(dimension.RadialDimension)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.change_rdim_dia_mode_init(gtkimage)

def change_adim_invert_cb(menuitem, gtkimage):
    _tool = tools.EditDimensionTool()
    _tool.setObjtype(dimension.AngularDimension)
    gtkimage.getImage().setTool(_tool)
    gtkmodify.invert_adim_init(gtkimage)



#############################################################################
#
# class IModifyMenu
#
#############################################################################

class IModifyMenu(IBaseMenu):

#----------------------------------------------------------------------------------------------
    def __init__(self, parent):
        super(IModifyMenu, self).__init__(parent)
        # create action group
        group = gtk.ActionGroup('Modify')
        self.gtkimage.addGroup(group)
        action = gtk.Action('ModifyMenu', _('_Modify'), None, None)
        group.add_action(action)
        self.__item = gtk.MenuItem()
        action.connect_proxy(self.__item)
        action.connect('activate', self.__menu_init_cb)
        # create menu
        self.__item.set_submenu(self.__create_menu(group))


    # properties
    def __get_menu(self):
        return self.__item

    GtkMenu = property(__get_menu, None, None, "ModifyMenu object.")


#----------------------------------------------------------------------------------------------
    def __create_menu(self, actiongroup):
        _accel = self.gtkimage.accel
        _menu = gtk.Menu()
        #
        _act = gtk.Action('Move', _('_Move ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_modify_move_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('Stretch', _('S_tretch ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_modify_stretch_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('Split', _('S_plit'), None, None)
        _act.connect('activate', split_object_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Mirror', _('_Mirror'), None, None)
        _act.connect('activate', mirror_object_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('Transfer', _('Trans_fer'), None, None)
        _act.connect('activate', transfer_object_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Rotate', _('_Rotate'), None, None)
        _act.connect('activate', rotate_object_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Delete', _('_Delete'), None, None)
        _act.connect('activate', delete_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('Change', _('_Change'), None, None)
        _act.connect('activate', self.__menu_change_init_cb)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_modify_change_menu(actiongroup))
        _menu.append(_item)
        return _menu

    
    #############################################################################
    #  Modify -> move sub-menu
    #############################################################################
    def __create_modify_move_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('MoveHoriz', _('_Horizontal'), None, None)
        _act.connect('activate', move_horizontal_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('MoveVert', _('_Vertical'), None, None)
        _act.connect('activate', move_vertical_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('MoveTwoPt', _('_Two-Point Move'), None, None)
        _act.connect('activate', move_twopoint_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu
    
    #############################################################################
    #  Modify -> stretch sub-menu
    #############################################################################
    def __create_modify_stretch_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('StretchHoriz', _('_Horizontal'), None, None)
        _act.connect('activate', stretch_horiz_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('StretchVert', _('_Vertical'), None, None)
        _act.connect('activate', stretch_vert_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('StretchTwoPt', _('_Two-Point Stretch'), None, None)
        _act.connect('activate', stretch_twopoint_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu
    
    
    #############################################################################
    #  Modify -> change sub-menu 
    #############################################################################
    def __create_modify_change_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangeStyle', _('_Style'), None, None)
        _act.connect('activate', change_style_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeLinetype', _('_Linetype'), None, None)
        _act.connect('activate', change_linetype_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeColor', _('_Color'), None, None)
        _act.connect('activate', change_color_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeThickness', _('_Thickness'), None, None)
        _act.connect('activate', change_thickness_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeTextMenu', _('Text_Block ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_change_text_menu(actiongroup))
        _menu.append(_item)
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeDimMenu', _('_Dimension ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_change_dimension_menu(actiongroup))
        _menu.append(_item)
        #
        return _menu
    
    
    #############################################################################
    #  Modify -> change sub-sub-menu 
    #############################################################################
    def __create_change_text_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangeTextBlockFamily', _('_Family'), None, None)
        _act.connect('activate', change_textblock_family_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeTextBlockWeight', _('_Weight'), None, None)
        _act.connect('activate', change_textblock_weight_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeTextBlockStyle', _('_Style'), None, None)
        _act.connect('activate', change_textblock_style_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeTextBlockColor', _('_Color'), None, None)
        _act.connect('activate', change_textblock_color_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeTextBlockSize', _('Si_ze'), None, None)
        _act.connect('activate', change_textblock_size_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeTextBlockAlignment', _('_Alignment'), None, None)
        _act.connect('activate', change_textblock_alignment_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu
    
    #############################################################################
    #  Modify -> change -> dimension sub-sub-menu 
    #############################################################################
    def __create_change_dimension_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangeDimEndpointType', _('Endpoint _Type'), None, None)
        _act.connect('activate', change_dim_endpoint_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimEndpointSize', _('Endpoint _Size'), None, None)
        _act.connect('activate', change_dim_endpoint_size_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimOffset', _('_Offset Length'), None, None)
        _act.connect('activate', change_dim_offset_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimExtension', _('E_xtension Length'), None, None)
        _act.connect('activate', change_dim_extension_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimDualMode', _('_Dual Mode'), None, None)
        _act.connect('activate', change_dim_dual_mode_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimDualModeOffset', _('Dual Mode O_ffset'),
                          None, None)
        _act.connect('activate', change_dim_dual_mode_offset_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimThickness', _('_Thickness'), None, None)
        _act.connect('activate', change_dim_thickness_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeDimColor', _('_Color'), None, None)
        _act.connect('activate', change_dim_color_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangePDimStrMenu', _('_Primary DimString'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_change_primary_dimstring_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeSDimStrMenu', _('_Secondary DimString'), None, None)
        actiongroup.add_action(_act)
    
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_change_secondary_dimstring_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeRDimMenu', _('RadialDim ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_change_rdim_menu(actiongroup))
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeADimMenu', _('AngularDim ...'), None, None)
        actiongroup.add_action(_act)
        _item = _act.create_menu_item()
        _item.set_submenu(self.__create_change_adim_menu(actiongroup))
        _menu.append(_item)
        #
        # _act = gtk.Action('ChangeDimPrimaryDS', '_Primary DimString', None, None)
        # _act.connect('activate', change_primary_dim_cb, gtkimage)
        # actiongroup.add_action(_act)
        # _menu.append(_act.create_menu_item())
        #
        # _act = gtk.Action('ChangeDimSecondaryDS', '_Secondary DimString', None, None)
        # _act.connect('activate', change_secondary_dim_cb, gtkimage)
        # actiongroup.add_action(_act)
        # _menu.append(_act.create_menu_item())
        #
        return _menu
    

    def __create_change_rdim_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangeRDimPDSPrefix', _('Primary Prefix'), None, None)
        _act.connect('activate', change_rdim_pds_prefix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeRDimPDSSuffix', _('Primary Suffix'), None, None)
        _act.connect('activate', change_rdim_pds_suffix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeRDimSDSPrefix', _('Secondary Prefix'), None, None)
        _act.connect('activate', change_rdim_sds_prefix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeRDimSDSSuffix', _('Secondary Suffix'), None, None)
        _act.connect('activate', change_rdim_sds_suffix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeRDimDiaMode', _('Dia. Mode'), None, None)
        _act.connect('activate', change_rdim_dia_mode_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu
    
    
    def __create_change_adim_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangeADimPDSPrefix', _('Primary Prefix'), None, None)
        _act.connect('activate', change_adim_pds_prefix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeADimPDSSuffix', _('Primary Suffix'), None, None)
        _act.connect('activate', change_adim_pds_suffix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeADimSDSPrefix', _('Secondary Prefix'), None, None)
        _act.connect('activate', change_adim_sds_prefix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeADimSDSSuffix', _('Secondary Suffix'), None, None)
        _act.connect('activate', change_adim_sds_suffix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _item = gtk.SeparatorMenuItem()
        _item.show()
        _menu.append(_item)
        #
        _act = gtk.Action('ChangeADimInvert', _('Invert'), None, None)
        _act.connect('activate', change_adim_invert_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu

    
    #############################################################################
    #  Modify -> change -> Dimension -> Primary DimString sub-sub-menu 
    #############################################################################
    def __create_change_primary_dimstring_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangePDimStringFamily', _('Family'), None, None)
        _act.connect('activate', change_dim_primary_family_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringWeight', _('Weight'), None, None)
        _act.connect('activate', change_dim_primary_weight_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringStyle', _('Style'), None, None)
        _act.connect('activate', change_dim_primary_style_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringSize', _('Size'), None, None)
        _act.connect('activate', change_dim_primary_size_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringColor', _('Color'), None, None)
        _act.connect('activate', change_dim_primary_color_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringAlignment', _('Alignment'), None, None)
        _act.connect('activate', change_dim_primary_alignment_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringPrefix', _('Prefix'), None, None)
        _act.connect('activate', change_ldim_pds_prefix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringSuffix', _('Suffix'), None, None)
        _act.connect('activate', change_ldim_pds_suffix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringPrecision', _('Precision'), None, None)
        _act.connect('activate', change_dim_primary_precision_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringUnits', _('Units'), None, None)
        _act.connect('activate', change_dim_primary_units_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringPrintZero', _('Print Zero'), None, None)
        _act.connect('activate', change_dim_primary_print_zero_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangePDimStringPrintDecimal', _('Print Decimal'), None, None)
        _act.connect('activate', change_dim_primary_print_decimal_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        return _menu
    
    #############################################################################
    #  Modify -> change -> Dimension -> Secondary DimString sub-sub-menu 
    #############################################################################
    def __create_change_secondary_dimstring_menu(self, actiongroup):
        _menu = gtk.Menu()
        #
        _act = gtk.Action('ChangeSDimStringFamily', _('Family'), None, None)
        _act.connect('activate', change_dim_secondary_family_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringWeight', _('Weight'), None, None)
        _act.connect('activate', change_dim_secondary_weight_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringStyle', _('Style'), None, None)
        _act.connect('activate', change_dim_secondary_style_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringSize', _('Size'), None, None)
        _act.connect('activate', change_dim_secondary_size_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringColor', _('Color'), None, None)
        _act.connect('activate', change_dim_secondary_color_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringAlignment', _('Alignment'), None, None)
        _act.connect('activate', change_dim_secondary_alignment_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringPrefix', _('Prefix'), None, None)
        _act.connect('activate', change_ldim_sds_prefix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringSuffix', _('Suffix'), None, None)
        _act.connect('activate', change_ldim_sds_suffix_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringPrecision', _('Precision'), None, None)
        _act.connect('activate', change_dim_secondary_precision_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringUnits', _('Units'), None, None)
        _act.connect('activate', change_dim_secondary_units_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringPrintZero', _('Print Zero'), None, None)
        _act.connect('activate', change_dim_secondary_print_zero_cb, self.gtkimage)
        actiongroup.add_action(_act)
        _menu.append(_act.create_menu_item())
        #
        _act = gtk.Action('ChangeSDimStringPrintDecimal', _('Print Decimal'),
                          None, None)
        _act.connect('activate', change_dim_secondary_print_decimal_cb, self.gtkimage)
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
        _group = self.gtkimage.getGroup('Modify')
        if _group is not None:
            _image = self.gtkimage.getImage()
            _active = _image.getActiveLayer()
            _act = _group.get_action('Move')
            if _act is not None:
                _act.set_property('sensitive', (_active.hasEntities() or
                                                _image.hasSelection()))
            _act = _group.get_action('Stretch')
            if _act is not None:
                _act.set_property('sensitive', _active.hasEntities())
            _act = _group.get_action('Split')
            if _act is not None:
                _flag = ((_active.getEntityCount('segment') > 0) or
                         (_active.getEntityCount('circle') > 0) or
                         (_active.getEntityCount('arc') > 0) or
                         (_active.getEntityCount('polyline') > 0))
                _act.set_property('sensitive', _flag)
            _act = _group.get_action('Mirror')
            if _act is not None:
                _flag = ((_active.hasEntities() or _image.hasSelection()) and
                         ((_active.getEntityCount('hcline') > 0) or
                          (_active.getEntityCount('vcline') > 0) or
                          (_active.getEntityCount('acline') > 0) or
                          (_active.getEntityCount('cline') > 0)))
                _act.set_property('sensitive', _flag)
            _act = _group.get_action('Transfer')
            if _act is not None:
                _flag = False
                _layers = [_image.getTopLayer()]
                while len(_layers):
                    _layer = _layers.pop()
                    if _layer is not _active:
                        _flag = _layer.hasEntities()
                    if _flag:
                        break
                    _layers.extend(_layer.getSublayers())
                _act.set_property('sensitive', _flag)
            _act = _group.get_action('Rotate')
            if _act is not None:
                _act.set_property('sensitive', (_active.hasEntities() or
                                                _image.hasSelection()))
            _act = _group.get_action('Delete')
            if _act is not None:
                _act.set_property('sensitive', _active.hasEntities())
            _act = _group.get_action('Change')
            if _act is not None:
                _act.set_property('sensitive', (_image.hasSelection() or
                                                _active.hasEntities()))
            _act = _group.get_action('ZoomFit')
            if _act is not None:
                _act.set_property('sensitive', _active.hasEntities())
            _group = self.gtkimage.getGroup('File')
            if _group is not None:
                _act = _group.get_action('SaveLayerAs')
                if _act is not None:
                    _act.set_property('sensitive', False)


    #############################################################################
    #  Initialize Modify -> change sub menu
    #############################################################################
    def __menu_change_init_cb(self, menuitem):
        # print "_change_menu_init()"
        _group = self.gtkimage.getGroup('Modify')
        if _group is not None:
            _image = self.gtkimage.getImage()
            _objlist = []
            _active = _image.getActiveLayer()
            _gflag = _tflag = _dflag = False
            for _obj in _image.getSelectedObjects(False):
                if isinstance(_obj, graphicobject.GraphicObject):
                    _goflag = True
                    continue
                if isinstance(_obj, text.TextBlock):
                    _tflag = True
                    continue
                if isinstance(_obj, dimension.Dimension):
                    _dflag = True
                if _gflag and _tflag and _dflag:
                    break
            if not _gflag or not _tflag or not _dflag:
                for _obj in _active.getChildren():
                    if not _gflag and isinstance(_obj,
                                                 graphicobject.GraphicObject):
                        _gflag = True
                        continue
                    if not _tflag and isinstance(_obj, text.TextBlock):
                        _tflag = True
                        continue
                    if not _dflag and isinstance(_obj, dimension.Dimension):
                        _dflag = True
                    if _gflag and _tflag and _dflag:
                        break
            _act = _group.get_action('ChangeStyle')
            if _act is not None:
                _act.set_property('sensitive', _gflag)
            _act = _group.get_action('ChangeLinetype')
            if _act is not None:
                _act.set_property('sensitive', _gflag)
            _act = _group.get_action('ChangeColor')
            if _act is not None:
                _act.set_property('sensitive', _gflag)
            _act = _group.get_action('ChangeThickness')
            if _act is not None:
                _act.set_property('sensitive', _gflag)
            _act = _group.get_action('ChangeTextMenu')
            if _act is not None:
                _act.set_property('sensitive', _tflag)
            _act = _group.get_action('ChangeDimMenu')
            if _act is not None:
                _act.set_property('sensitive', _dflag)
