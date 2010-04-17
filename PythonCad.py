#!/usr/bin/env python

#
# Copyright (c) 2002, 2003, 2004, 2005, 2006, 2007 Art Haas
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
# main routine to start GTK-based pycad
#

raise DeprecationWarning,  """"The R38 Version si under complete restructuring this entry file is no more used
use test_kernel.py or pythoncad_qt.py under PythonCAD folder"""

import getopt
import sys
import os

import pygtk
pygtk.require('2.0')
import gtk

import gettext
gettext.install('PythonCAD')

from PythonCAD.Generic import globals
from PythonCAD.Generic import imageio
from PythonCAD.Generic import fileio
from PythonCAD.Generic import selections
from PythonCAD.Generic import preferences
from PythonCAD.Generic import color
from PythonCAD.Generic import linetype
from PythonCAD.Generic import style
from PythonCAD.Generic import segment
from PythonCAD.Generic import circle
from PythonCAD.Generic import arc
from PythonCAD.Generic import leader
from PythonCAD.Generic import polyline
from PythonCAD.Generic import segjoint
from PythonCAD.Generic import conobject
from PythonCAD.Generic import baseobject
from PythonCAD.Generic import graphicobject
from PythonCAD.Generic import dimension
from PythonCAD.Generic import text
from PythonCAD.Generic import units
from PythonCAD.Interface.Gtk import gtkinit

def _initialize_booleans():
    globals.prefs['HIGHLIGHT_POINTS'] = True
    globals.prefs['AUTOSPLIT'] = False

def _initialize_sizes():
    globals.prefs['CHAMFER_LENGTH'] = 1.0
    globals.prefs['FILLET_RADIUS'] = 1.0
    globals.prefs['FILLET_TWO_TRIM_MODE'] = 'b'
    globals.prefs['UNITS'] = units.MILLIMETERS
    globals.prefs['LEADER_ARROW_SIZE'] = 1.0

def _initialize_image_colors():
    _color = color.get_color(80, 140, 210) # blueish/purpleish
    globals.prefs['INACTIVE_LAYER_COLOR'] = _color
    _color = color.get_color(0, 0, 0) # black
    globals.prefs['BACKGROUND_COLOR'] = _color
    _color = color.get_color(255, 255, 0) # yellow
    globals.prefs['SINGLE_POINT_COLOR'] = _color
    _color = color.get_color(0, 255, 255) # cyan
    globals.prefs['MULTI_POINT_COLOR'] = _color

def _initialize_styles():
    _style = graphicobject.GraphicObject.getDefaultStyle()
    globals.prefs['LINE_STYLE'] = _style
    globals.prefs['LINE_COLOR'] = _style.getColor()
    globals.prefs['LINE_TYPE'] = _style.getLinetype()
    globals.prefs['LINE_THICKNESS'] = _style.getThickness()
    #
    # set this style as the class default for the "real" drawing entities
    #
    segment.Segment.setDefaultStyle(_style)
    circle.Circle.setDefaultStyle(_style)
    arc.Arc.setDefaultStyle(_style)
    leader.Leader.setDefaultStyle(_style)
    polyline.Polyline.setDefaultStyle(_style)
    segjoint.SegJoint.setDefaultStyle(_style)
    segjoint.Chamfer.setDefaultStyle(_style)
    segjoint.Fillet.setDefaultStyle(_style)
    #
    # define and set a construction line style
    #
    _color = color.get_color(0xff, 0, 0) # red
    _lt = linetype.Linetype(u'Construction Lines', [2, 2])
    _style = style.Style(u'Construction Objects', _lt, _color, 0.0)
    conobject.ConstructionObject.setDefaultStyle(_style)
    #
    # define and add the default text style and use values in the
    # text style to define various global key/value pairs
    #
    _ts = text.TextBlock.getDefaultTextStyle()
    globals.prefs['TEXT_STYLE'] = _ts    
    globals.prefs['FONT_COLOR'] = _ts.getColor()
    globals.prefs['FONT_WEIGHT'] = _ts.getWeight()
    globals.prefs['FONT_STYLE'] = _ts.getStyle()
    globals.prefs['FONT_FAMILY'] = _ts.getFamily()
    globals.prefs['TEXT_SIZE'] = _ts.getSize()
    globals.prefs['TEXT_ANGLE'] = _ts.getAngle()
    globals.prefs['TEXT_ALIGNMENT'] = _ts.getAlignment()
    #
    # define and add the default dimension style and use the
    # values in that style to define various global preference
    # key/value pairs
    #
    _ds = dimension.Dimension.getDefaultDimStyle()
    globals.dimstyles.append(_ds)
    globals.prefs['DIM_STYLE'] = _ds
    for _key in _ds.getOptions():
        _value = _ds.getOption(_key)
        globals.prefs[_key] = _value
    
def _initialize_linetypes():
    _lt = linetype.Linetype(u'Solid') # solid
    globals.linetypes[_lt] = _lt
    _lt = linetype.Linetype(u'Dash1', [4, 1]) # dashed line
    globals.linetypes[_lt] = _lt
    _lt = linetype.Linetype(u'Dash2', [8, 2]) # dashed line
    globals.linetypes[_lt] = _lt
    _lt = linetype.Linetype(u'Dash3', [12, 2]) # dashed line
    globals.linetypes[_lt] = _lt
    _lt = linetype.Linetype(u'Dash4', [10, 2, 2, 2]) # dashed line
    globals.linetypes[_lt] = _lt
    _lt = linetype.Linetype(u'Dash5', [15, 5, 5, 5]) # dashed line
    globals.linetypes[_lt] = _lt

def _initialize_colors():
    _color = color.Color(255, 0, 0) # red
    globals.colors[_color] = _color
    _color = color.Color(0, 255, 0) # green
    globals.colors[_color] = _color
    _color = color.Color(0, 0, 255) # blue
    globals.colors[_color] = _color
    _color = color.Color(255, 0, 255) # violet
    globals.colors[_color] = _color
    _color = color.Color(255, 255, 0) # yellow
    globals.colors[_color] = _color
    _color = color.Color(0, 255, 255) # cyan
    globals.colors[_color] = _color
    _color = color.Color(255, 255, 255) # white
    globals.colors[_color] = _color
    _color = color.Color(0, 0, 0) # black
    globals.colors[_color] = _color

def _inizialize_snap():
    """
        Inizialize Global Snap Erray
    """
    globals.snapOption={'mid':True,'point':True,'end':True,'intersection':True,
        'origin':False,'perpendicular':False,'tangent':False,'center':True}

def _initialize_globals():
    #
    # define globals
    #
    globals.imagelist = []
    globals.prefs = {}
    globals.colors = baseobject.TypedDict(color.Color, color.Color)
    globals.linetypes = baseobject.TypedDict(linetype.Linetype, linetype.Linetype)
    globals.dimstyles = []
    globals.selectobj = selections.Selection()
    
    _initialize_colors()
    _initialize_linetypes()
    _initialize_styles()
    _initialize_image_colors()
    _initialize_sizes()
    _initialize_booleans()
    _inizialize_snap()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help", "version"])
    except getopt.GetoptError, e:
        sys.stderr.write("Error: %s\n" % e)
        sys.exit(1)
    for o, a in opts:
        if o in ("-h", "--help"):
            sys.stdout.write("No help yet! Sorry ...\n")
            sys.exit()
        if o in ("-v", "--version"):
            sys.stdout.write("PythonCAD - DS1 - Release 37 Alfa \n")
            sys.exit()

    #
    # load up global and user preferences
    #

    _initialize_globals()
    preferences.initialize_prefs()
    preferences.load_global_prefs()
    _user_flag = globals.prefs['USER_PREFS']
    if _user_flag:
        preferences.load_user_prefs()

    #
    # open any drawings passed as arguments. This code needs
    # to be much more robust ...
    #

    assert 'BACKGROUND_COLOR' in globals.prefs, "BACKGROUND_COLOR missing"
    _background = globals.prefs['BACKGROUND_COLOR']
    from PythonCAD.Interface.Gtk.gtkimage import GTKImage
    from PythonCAD.Generic.image import Image, ImageLog
    for _arg in args:
        if os.path.exists(_arg):
            sys.stdout.write("Opening '%s'\n" % _arg)
            try:
                _imfile = fileio.CompFile(_arg, "r")
            except IOError, _e:
                sys.stderr.write("Can't open '%s'! %s" % (_arg, _e))
                continue
            _image = Image()
            try:
                try:
                    imageio.load_image(_image, _imfile)
                finally:
                    _imfile.close()
                _log = ImageLog(_image)
                _image.setLog(_log)
                _fname = os.path.realpath(_arg)
                _image.setFilename(_fname)
                _gtkimage = GTKImage(_image)
                _window = _gtkimage.getWindow()
                _window.set_title(os.path.basename(_fname))
                globals.imagelist.append(_image)
                if _image.getOption('BACKGROUND_COLOR') == _background:
                    _image.setOption('BACKGROUND_COLOR', _background)
                _window.show_all()                    
                _gtkimage.fitImage()
            except StandardError, _e:
                sys.stderr.write("Failed loading '%s'! %s" % (_arg, _e))
        else:
            sys.stderr.write("Can't find file '%s' - Skipping ...\n" % _arg)
    if not len(globals.imagelist):
        _image = Image()
        _gtkimage = GTKImage(_image)
        _log = ImageLog(_image)
        _image.setLog(_log)
        globals.imagelist.append(_image)
        _image.setOption('BACKGROUND_COLOR', _background)        
        _gtkimage.window.show_all()
    gtk.main()

if __name__ == '__main__':
    _major, _minor, _micro = gtk.pygtk_version
    if ((_major < 2) and
        (_minor < 100) and #
        (_micro < 16)):
        print """
The PyGTK version you are using needs to be upgraded to
a newer version. Changes in the PyGTK code have required
the addition of some compatibility code in PythonCAD,
but these changes are temporary and will be removed in
a future PythonCAD release. Please upgrade your PyGTK
module to version 1.99.16 (at least), or retrieve and
build the PyGTK module from the CVS archive.
"""
    main()
