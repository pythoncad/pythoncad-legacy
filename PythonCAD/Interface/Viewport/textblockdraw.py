#
# Copyright (c) 2005, 2006 Art Haas
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
# code for adding graphical methods to drawing entities
#


import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic import text


#----------------------------------------------------------------------------------------------------
def _format_layout(self, viewport, layout):
    font_descr = pango.FontDescription()
    font_descr.set_family(self.getFamily())
    # font style
    font_style = self.getStyle()
    if font_style == text.TextStyle.FONT_NORMAL:
        pango_style = pango.STYLE_NORMAL
    elif font_style == text.TextStyle.FONT_OBLIQUE:
        pango_style = pango.STYLE_OBLIQUE
    elif font_style == text.TextStyle.FONT_ITALIC:
        pango_style = pango.STYLE_ITALIC
    else:
        raise ValueError, "Unexpected TextBlock font style: %d" % font_style
    # set font style
    font_descr.set_style(pango_style)
    # font weight
    font_weight = self.getWeight()
    if font_weight == text.TextStyle.WEIGHT_NORMAL:
        pango_weight = pango.WEIGHT_NORMAL
    elif font_weight == text.TextStyle.WEIGHT_LIGHT:
        pango_weight = pango.WEIGHT_LIGHT
    elif font_weight == text.TextStyle.WEIGHT_BOLD:
        pango_weight = pango.WEIGHT_BOLD
    elif font_weight == text.TextStyle.WEIGHT_HEAVY:
        pango_weight = pango.WEIGHT_HEAVY
    else:
        raise ValueError, "Unexpected TextBlock font weight: %d" % font_weight
    # set font weight
    font_descr.set_weight(pango_weight)
    
    font_size = viewport.WorldToViewportSize(self.getSize())
    pango_size = int(pango.SCALE * font_size)
    if pango_size < pango.SCALE:
        pango_size = pango.SCALE
    # set font size      
    font_descr.set_size(pango_size)
    #
    # todo: handle drawing rotated text
    #
    font_alignment = self.getAlignment()
    if font_alignment == text.TextStyle.ALIGN_LEFT:
        layout.set_alignment(pango.ALIGN_LEFT)
    elif font_alignment == text.TextStyle.ALIGN_CENTER:
        layout.set_alignment(pango.ALIGN_CENTER)
    elif font_alignment == text.TextStyle.ALIGN_RIGHT:
        layout.set_alignment(pango.ALIGN_RIGHT)
    else:
        raise ValueError, "Unexpected TextBlock alignment value: %d" % font_alignment
    # set font alignment
    layout.set_font_description(font_descr)
    if self.getLineCount() > 0:
        width, height = layout.get_pixel_size()
        self.setBounds(viewport.ViewportToWorldSize(width), viewport.ViewportToWorldSize(height))
        
#----------------------------------------------------------------------------------------------------
def _draw_textblock(self, viewport, col=None):
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # create layout
    layout = viewport.cairo_context.create_layout()
    layout.set_text(self.getText())            
    # do the formatting
    self._formatLayout(viewport, layout)
    # get the text location
    location = self.getLocation()
    # do the actual draw of the text
    viewport.draw_text(color, location, layout)
    
#----------------------------------------------------------------------------------------------------
def _erase_textblock(self, viewport):
    self.draw(viewport, viewport.Image.getOption('BACKGROUND_COLOR'))
