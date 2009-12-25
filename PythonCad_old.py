#
# Copyright (c) 2002-2004 Art Haas
#
# This file is part of PythonCAD.
# 
# PythonCAD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
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
# main routine to start Cocoa-based PythonCad
#

import getopt
import sys
import os

import PythonCAD.Generic.image
import PythonCAD.Generic.imageio
import PythonCAD.Generic.fileio
import PythonCAD.Generic.selections
import PythonCAD.Generic.preferences
import PythonCAD.Generic.color
import PythonCAD.Generic.linetype
import PythonCAD.Generic.style
import PythonCAD.Generic.segment
import PythonCAD.Generic.circle
import PythonCAD.Generic.leader
import PythonCAD.Generic.polyline
import PythonCAD.Generic.segjoint
import PythonCAD.Generic.conobject
import PythonCAD.Generic.baseobject
import PythonCAD.Generic.dimension
import PythonCAD.Generic.units
import PythonCAD.Interface.Cocoa.ImageDocument 
import PythonCAD.Interface.Cocoa.CADView
import PythonCAD.Interface.Cocoa.AppController

from PyObjCTools import NibClassBuilder, AppHelper

#Initialize NIB
NibClassBuilder.extractClasses("ImageDocument")

#
# set up global variables ...
#

PythonCAD.Generic.globals.prefs = PythonCAD.Generic.baseobject.LockedDict(str)
PythonCAD.Generic.globals.colors = PythonCAD.Generic.baseobject.TypedDict(PythonCAD.Generic.color.Color,
                                                      PythonCAD.Generic.color.Color)
PythonCAD.Generic.globals.linetypes = PythonCAD.Generic.baseobject.TypedDict(PythonCAD.Generic.linetype.Linetype, PythonCAD.Generic.linetype.Linetype)
PythonCAD.Generic.globals.styles = PythonCAD.Generic.baseobject.TypedDict(PythonCAD.Generic.style.Style,
                                                      PythonCAD.Generic.style.Style)
PythonCAD.Generic.globals.dimstyles = []

PythonCAD.Generic.globals.selectobj = PythonCAD.Generic.selections.Selection()


def _initialize_booleans():
    PythonCAD.Generic.globals.prefs['HIGHLIGHT_POINTS'] = True
    PythonCAD.Generic.globals.prefs['AUTOSPLIT'] = False

def _initialize_sizes():
    PythonCAD.Generic.globals.prefs['CHAMFER_LENGTH'] = 1.0
    PythonCAD.Generic.globals.prefs['FILLET_RADIUS'] = 1.0
    PythonCAD.Generic.globals.prefs['UNITS'] = PythonCAD.Generic.units.MILLIMETERS
    PythonCAD.Generic.globals.prefs['LEADER_ARROW_SIZE'] = 1.0

def _initialize_image_colors():
    _color = PythonCAD.Generic.color.get_color(80, 140, 210) # blueish/purpleish
    PythonCAD.Generic.globals.prefs['INACTIVE_LAYER_COLOR'] = _color
    _color = PythonCAD.Generic.color.get_color(0, 0, 0) # black
    PythonCAD.Generic.globals.prefs['BACKGROUND_COLOR'] = _color
    _color = PythonCAD.Generic.color.get_color(255, 255, 0) #yellow
    PythonCAD.Generic.globals.prefs['SINGLE_POINT_COLOR'] = _color
    _color = PythonCAD.Generic.color.get_color(0, 255, 255) #cyan
    PythonCAD.Generic.globals.prefs['MULTI_POINT_COLOR'] = _color

def _initialize_styles():
    _color = PythonCAD.Generic.color.get_color(0xff, 0xff, 0xff) # white
    _lt = PythonCAD.Generic.linetype.get_linetype_by_dashes(None)
    _style = PythonCAD.Generic.style.Style(u'Solid White Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    PythonCAD.Generic.globals.prefs['LINE_STYLE'] = _style
    PythonCAD.Generic.globals.prefs['LINE_COLOR'] = _style.getColor()
    PythonCAD.Generic.globals.prefs['LINE_TYPE'] = _style.getLinetype()
    PythonCAD.Generic.globals.prefs['LINE_THICKNESS'] = _style.getThickness()
    #
    # set this style as the class default for the "real" drawing entities
    #
    # fixme: this should be done with a classmethod or some sort of
    # function ...
    #
    PythonCAD.Generic.segment.Segment.__defstyle = _style
    PythonCAD.Generic.circle.Circle.__defstyle = _style
    PythonCAD.Generic.leader.Leader.__defstyle = _style
    PythonCAD.Generic.polyline.Polyline.__defstyle = _style
    PythonCAD.Generic.segjoint.SegJoint.__defstyle = _style
    #
    _color = PythonCAD.Generic.color.get_color(0, 0, 0) # black
    _style = PythonCAD.Generic.style.Style(u'Solid Black Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    _color = PythonCAD.Generic.color.get_color(0xff, 0, 0) # red
    _lt = PythonCAD.Generic.linetype.get_linetype_by_dashes([4, 1])
    _style = PythonCAD.Generic.style.Style(u'Dashed Red Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    _color = PythonCAD.Generic.color.get_color(0, 0xff, 0) # green
    _style = PythonCAD.Generic.style.Style(u'Dashed Green Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    _color = PythonCAD.Generic.color.get_color(0, 0, 0xff) # blue
    _style = PythonCAD.Generic.style.Style(u'Dashed Blue Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    _color = PythonCAD.Generic.color.get_color(0xff, 0xff, 0) # yellow
    _lt = PythonCAD.Generic.linetype.get_linetype_by_dashes([8, 2])
    _style = PythonCAD.Generic.style.Style(u'Dashed Yellow Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    _color = PythonCAD.Generic.color.get_color(0xff, 0, 0xff) # violet
    _style = PythonCAD.Generic.style.Style(u'Dashed Violet Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    _color = PythonCAD.Generic.color.get_color(0, 0xff, 0xff) # cyan
    _style = PythonCAD.Generic.style.Style(u'Dashed Cyan Line', _lt, _color, 1.0)
    PythonCAD.Generic.globals.styles[_style] = _style
    #
    # define and set a construction line style
    #
    _color = PythonCAD.Generic.color.get_color(0xff, 0, 0) # red
    _lt = PythonCAD.Generic.linetype.Linetype(u'Construction Lines', [2, 2])
    _style = PythonCAD.Generic.style.Style(u'Construction Objects', _lt, _color, 0.0)
    PythonCAD.Generic.conobject.ConstructionObject.__defstyle = _style
    #
    # define and add the default text style and use values in the
    # text style to define various global key/value pairs
    #
    _white = PythonCAD.Generic.color.get_color(0xff, 0xff, 0xff)
    _ts = PythonCAD.Generic.text.TextStyle(u'Default Text Style', color=_white)
    PythonCAD.Generic.globals.prefs['TEXT_STYLE'] = _ts
    PythonCAD.Generic.globals.prefs['FONT_COLOR'] = _ts.getColor()
    PythonCAD.Generic.globals.prefs['FONT_SIZE'] = _ts.getSize()
    PythonCAD.Generic.globals.prefs['FONT_WEIGHT'] = _ts.getWeight()
    PythonCAD.Generic.globals.prefs['FONT_STYLE'] = _ts.getStyle()
    PythonCAD.Generic.globals.prefs['FONT_FAMILY'] = _ts.getFamily()
    #
    # define and add the default dimension style and use the
    # values in that style to define various global preference
    # key/value pairs
    #
    _dsdict = {}
    _dsdict['DIM_PRIMARY_FONT_COLOR'] = _white
    _dsdict['DIM_SECONDARY_FONT_COLOR'] = _white
    _dimcolor = PythonCAD.Generic.color.get_color(255, 165, 0) # orangeish
    _dsdict['DIM_COLOR'] = _dimcolor
    _ds = PythonCAD.Generic.dimension.DimStyle(u'Default DimStyle', _dsdict)
    PythonCAD.Generic.globals.dimstyles.append(_ds)
    PythonCAD.Generic.globals.prefs['DIM_STYLE'] = _ds
    for _key in _ds.getOptions():
        _value = _ds.getOption(_key)
        PythonCAD.Generic.globals.prefs[_key] = _value
    
    
def _initialize_linetypes():
    _lt = PythonCAD.Generic.linetype.Linetype(u'Solid') # solid
    PythonCAD.Generic.globals.linetypes[_lt] = _lt
    _lt = PythonCAD.Generic.linetype.Linetype(u'Dash1', [4, 1]) # dashed line
    PythonCAD.Generic.globals.linetypes[_lt] = _lt
    _lt = PythonCAD.Generic.linetype.Linetype(u'Dash2', [8, 2]) # dashed line
    PythonCAD.Generic.globals.linetypes[_lt] = _lt
    _lt = PythonCAD.Generic.linetype.Linetype(u'Dash3', [12, 2]) # dashed line
    PythonCAD.Generic.globals.linetypes[_lt] = _lt
    _lt = PythonCAD.Generic.linetype.Linetype(u'Dash4', [10, 2, 2, 2]) # dashed line
    PythonCAD.Generic.globals.linetypes[_lt] = _lt
    _lt = PythonCAD.Generic.linetype.Linetype(u'Dash5', [15, 5, 5, 5]) # dashed line
    PythonCAD.Generic.globals.linetypes[_lt] = _lt

def _initialize_colors():
    _color = PythonCAD.Generic.color.Color(255, 0, 0) # red
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(0, 255, 0) # green
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(0, 0, 255) # blue
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(255, 0, 255) # violet
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(255, 255, 0) # yellow
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(0, 255, 255) # cyan
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(255, 255, 255) # white
    PythonCAD.Generic.globals.colors[_color] = _color
    _color = PythonCAD.Generic.color.Color(0, 0, 0) # black
    PythonCAD.Generic.globals.colors[_color] = _color

def _initialize_globals():
    _initialize_colors()
    _initialize_linetypes()
    _initialize_styles()
    _initialize_image_colors()
    _initialize_sizes()
    _initialize_booleans()
    
def main():
    #
    # load up global and user preferences
    #

    _initialize_globals()
    PythonCAD.Generic.preferences.initialize_prefs()
    PythonCAD.Generic.preferences.load_global_prefs()
    _user_flag = PythonCAD.Generic.globals.prefs['USER_PREFS']
    if _user_flag:
        PythonCAD.Generic.preferences.load_user_prefs()
    PythonCAD.Generic.globals.prefs.lock() # the globals are now set


if __name__ == '__main__':
    main()
    AppHelper.runEventLoop()

# need some version checking for OS X - 10.2?  10.3?
#    _major, _minor, _micro = gtk.pygtk_version
#    if ((_major < 2) and
#        (_minor < 100) and #
#        (_micro < 16)):
#        print     main()
