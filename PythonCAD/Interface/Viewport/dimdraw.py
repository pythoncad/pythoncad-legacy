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

#import types
#from math import pi
#_dtr = (pi/180.0)

import pygtk
pygtk.require('2.0')
import gtk
import pango

from PythonCAD.Generic import color
from PythonCAD.Generic.point import Point
from PythonCAD.Generic import dimension


#----------------------------------------------------------------------------------------------------
def _draw_dimstrings(self, viewport, col=None):
    pass
    #_ctx = gimage.getCairoContext()
    #if _ctx is not None:
        #_ctx.save()
    #_da = gimage.getDA()
    ##
    ## fixme - calculating dimensions needs rework!
    ##
    #_image = gimage.getImage()
    #_slen = _image.scaleLength(self.calculate())
    #_dims = self.getDimensions(_slen)
    #_dx, _dy = self.getLocation()
    #_ds1 = _ds2 = _l1 = _l2 = _x1 = _y1 = _x2 = _y2 = None
    #if self.getDualDimMode():
        #_off = self.getDualModeOffset()
        #_ds1 = self.getPrimaryDimstring()
        #if _ctx is not None:
            #_l1 = _ctx.create_layout()
            #_l1.set_text(_ds1.getText())
        #else:
            #_l1 = _da.create_pango_layout(_ds1.getText())
        #_ds1._formatLayout(gimage, _l1)
        #_w1, _h1 = _ds1.getBounds()
        #_ds1.setLocation((_dx - (_w1/2.0)), (_dy + _h1 + _off))
        #_x1, _y1 = _ds1.getLocation()
        #_ds2 = self.getSecondaryDimstring()
        #if _ctx is not None:
            #_l2 = _ctx.create_layout()
            #_l2.set_text(_ds2.getText())
        #else:
            #_l2 = _da.create_pango_layout(_ds2.getText())
        #_ds2._formatLayout(gimage, _l2)
        #_w2, _h2 = _ds2.getBounds()
        #_ds2.setLocation((_dx - (_w2/2.0)), (_dy - _off))
        #_x2, _y2 = _ds2.getLocation()
        #_brect = (min(_x1, _x2), # xmin
                  #_y1, # ymax
                  #max((_x1 + _w1), (_x2 + _w2)), # xmax
                  #(_y2 - _h2)) # ymin
    #else:
        #_ds1 = self.getPrimaryDimstring()
        #if _ctx is not None:
            #_l1 = _ctx.create_layout()
            #_l1.set_text(_ds1.getText())
        #else:
            #_l1 = _da.create_pango_layout(_ds1.getText())
        #_ds1._formatLayout(gimage, _l1)
        #_w, _h = _ds1.getBounds()
        #_ds1.setLocation((_dx - (_w/2.0)), (_dy + (_h/2.0)))
        #_x1, _y1 = _ds1.getLocation()
        #_brect = (_x1, _y1, (_x1 + _w), (_y1 - _h))
    #_bx1, _by1 = gimage.coordToPixTransform(_brect[0], _brect[1])
    #_bx2, _by2 = gimage.coordToPixTransform(_brect[2], _brect[3])
    #_pixmap = None
    #_bgcol = _image.getOption('BACKGROUND_COLOR') #this is a string not an object
    #print "Debug: _bhcol %s"%str(_bgcol)
    #if _ctx is not None :
        #_r, _g, _b = _bgcol.getColors()
        #_ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        #_ctx.rectangle((_bx1 - 2), (_by1 - 2),
                       #((_bx2 - _bx1) + 4), ((_by2 - _by1) + 4))
        #_ctx.fill()
    #else:
        #_gc = gimage.getGC()
        #_gc.set_function(gtk.gdk.COPY)
        #_gc.set_foreground(gimage.getColor(_bgcol))
        #_pixmap = gimage.getPixmap()
        #_pixmap.draw_rectangle(_gc, True, (_bx1 - 2), (_by1 - 2),
                               #((_bx2 - _bx1) + 4), ((_by2 - _by1) + 4))
    #_col = col
    
    #if _col is None:
        #_col = _ds1.getColor()
    #_px, _py = gimage.coordToPixTransform(_x1, _y1)        
    #if _ctx is not None:
        #_r, _g, _b = _col.getColors()
        #_ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
        #_ctx.move_to(_px, _py)
        #_ctx.show_layout(_l1)
    #else:
        #_gc.set_foreground(gimage.getColor(_col))
        #_px, _py = gimage.coordToPixTransform(_x1, _y1)
        #_pixmap.draw_layout(_gc, _px, _py, _l1)
    #if _ds2 is not None:
        #_col = col
        #if _col is None:
            #_col = _ds2.getColor()
        #if _ctx is not None:
            #_r, _g, _b = _col.getColors()
            #_ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            #_px, _py = gimage.coordToPixTransform(_x2, _y2)
            #_ctx.move_to(_px, _py)
            #_ctx.show_layout(_l2)
        #else:
            #_gc.set_foreground(gimage.getColor(_col))
            #_px, _py = gimage.coordToPixTransform(_x2, _y2)
            #_pixmap.draw_layout(_gc, _px, _py, _l2)
        #_col = col
        #if _col is None:
            #_col = self.getColor()
        #_px1, _py1 = gimage.coordToPixTransform(_brect[0], _dy)
        #_px2, _py2 = gimage.coordToPixTransform(_brect[2], _dy)
        #if _ctx is not None:
            #_r, _g, _b = _col.getColors()
            #_ctx.set_source_rgb((_r/255.0), (_g/255.0), (_b/255.0))
            #_ctx.move_to(_px1, _py1)
            #_ctx.line_to(_px2, _py2)
            #_ctx.stroke()
        #else:
            #_gc.set_foreground(gimage.getColor(_col))                    
            #_pixmap.draw_line(_gc, _px1, _py1, _px2, _py2)
        #_l2 = None
    #_l1 = None
    #if _ctx is not None:
        #_ctx.restore()


#----------------------------------------------------------------------------------------------------
def _draw_arrow_endpt(viewport, crossbar_pts, marker_pts, fill):
    # first marker
    p1 = crossbar_pts[0]
    p2 = marker_pts[0]
    if p2 is not None:
        p3 = marker_pts[1]
        # add points to list
        points = []
        points.append(p1)
        points.append(p2)
        # do the actual draw of the arrow
        viewport.draw_polygon(None, None, None, points, fill)         
    # second marker
    p1 = crossbar_pts[1]
    p2 = marker_pts[2]
    if p2 is not None:
        p3 = marker_pts[3]
        # add points to list
        points = []
        points.append(p1)
        points.append(p2)
        # do the actual draw of the arrow
        viewport.draw_polygon(None, None, None, points, fill)         

#----------------------------------------------------------------------------------------------------
def _draw_slash_endpt(viewport, marker_pts):
    # first
    p1 = marker_pts[0]
    if p1 is not None:
        p2 = marker_pts[1]
        # add points to list
        points = []
        points.append(p1)
        points.append(p2)
        # do the actual draw of the linestring
        viewport.draw_linestring(color, lineweight, linestyle, points)  
    # second
    p1 = marker_pts[2]
    if p1 is not None:
        p2 = marker_pts[3]
        # add points to list
        points = []
        points.append(p1)
        points.append(p2)
        # do the actual draw of the linestring
        viewport.draw_linestring(color, lineweight, linestyle, points)  

#----------------------------------------------------------------------------------------------------
def _draw_circle_endpt(viewport, crossbar_pts, size):
    # radius
    radius = size / 2.0
    # center circle 1
    center = crossbar_pts[0]
    if center is not None:
        # do the actual draw of the circle
        viewport.draw_circle(None, None, None, center, radius, True)    
    # center circle 2
    center = crossbar_pts[1]
    if center is not None:
        # do the actual draw of the circle
        viewport.draw_circle(None, None, None, center, radius, True) 
        
#----------------------------------------------------------------------------------------------------
def _draw_crossbar(viewport, cross_bar, color):
    p1, p2 = cross_bar.getEndpoints()
    # add points to list
    points = []
    points.append(Point(p1[0], p1[1]))
    points.append(Point(p2[0], p2[1]))
    # do the actual draw of the linestring
    viewport.draw_linestring(color, None, None, points)    

   
#----------------------------------------------------------------------------------------------------
def _draw_crossarc(viewport, cross_arc, center, color):
    start = cross_arc.getStartAngle()
    end = cross_arc.getEndAngle()    
    radius = cross_arc.getRadius()
    # do the actual draw of the arc
    viewport.draw_arc(color, None, None, center, radius, start, end) 

#----------------------------------------------------------------------------------------------------
def _draw_dimbar(viewport, dim_bar, color):
    # first dimbar
    p1, p2 = dim_bar.getEndpoints()
    # add points to list
    points = []
    points.append(Point(p1[0], p1[1]))
    points.append(Point(p2[0], p2[1]))
    # do the actual draw of the linestring
    viewport.draw_linestring(color, None, None, points)  

    
#----------------------------------------------------------------------------------------------------
def _draw_markers(self, viewport, dim_object):
    # points
    crossbar_pts = dim_object.getCrossbarPoints()
    marker_pts = dim_object.getMarkerPoints()
    # visual depend on type
    endpoint_type = self.getEndpointType()
    if endpoint_type != dimension.Dimension.DIM_ENDPT_NONE:
        dia_mode = self.getDiaMode()
        # 
        if (endpoint_type == dimension.Dimension.DIM_ENDPT_ARROW or
            endpoint_type == dimension.Dimension.DIM_ENDPT_FILLED_ARROW or
            endpoint_type == dimension.Dimension.DIM_ENDPT_SLASH):
            # open arrow
            if endpoint_type == dimension.Dimension.DIM_ENDPT_ARROW:
                _draw_arrow_endpt(viewport, crossbar_pts, marker_pts, False)
            # filled arrow
            elif endpoint_type == dimension.Dimension.DIM_ENDPT_FILLED_ARROW:
                _draw_arrow_endpt(viewport, crossbar_pts, marker_pts, True)
            # slash
            elif endpoint_type == dimension.Dimension.DIM_ENDPT_SLASH:
                _draw_slash_endpt(viewport, marker_pts)
            else:
                raise ValueError, "Unexpected end point type: %d" % endpoint_type
        # circle
        elif endpoint_type == dimension.Dimension.DIM_ENDPT_CIRCLE:
            size = self.getEndpointSize()
            _draw_circle_endpt(viewport, crossbar_pts, size)
        # error
        else:
            raise ValueError, "Unexpected endpoint value: %d" % endpoint_type
        
#----------------------------------------------------------------------------------------------------
def _draw_ldim(self, viewport, col=None):
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # display properties
    lineweight = self.getThickness()
    # cross bar
    cross_bar = self.getDimCrossbar()
    _draw_crossbar(viewport, cross_bar, color)
    # draw the dimension bars
    dim_bar1, dim_bar2 = self.getDimBars()
    # first dimbar
    _draw_dimbar(viewport, dim_bar1, color)
    # second dimbar
    _draw_dimbar(viewport, dim_bar2, color)
    # draw endpoint markers
    self.draw_markers(viewport, cross_bar)
    # dim text
    self._drawDimStrings(viewport, color)

#----------------------------------------------------------------------------------------------------
def _draw_rdim(self, viewport, col=None):
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # display properties
    lineweight = self.getThickness()
    # cross bar
    cross_bar = self.getDimCrossbar()
    _draw_crossbar(viewport, cross_bar, color)    
    # draw endpoint markers
    self.draw_markers(viewport, cross_bar)
    # dim text
    self._drawDimStrings(viewport, color)

#----------------------------------------------------------------------------------------------------
def _draw_adim(self, viewport, col=None):
    color = col
    # is color defined
    if color is not None and not isinstance(color, color.Color):
        raise TypeError, "Invalid Color: " + `type(color)`
    # if color is not defined, take color of entity
    if color is None:
        color = self.getColor()
    # display properties
    lineweight = self.getThickness()
    # draw cross arc
    center = self.getVertexPoint()
    cross_arc = self.getDimCrossarc()
    _draw_crossarc(viewport, cross_arc, center, color)
    # draw the dimension bars
    dim_bar1, dim_bar2 = self.getDimBars()
    # first dimbar
    _draw_dimbar(viewport, dim_bar1, color)
    # second dimbar
    _draw_dimbar(viewport, dim_bar2, color)    
    # draw endpoint markers
    self.draw_markers(viewport, cross_arc)
    # dim text
    self._drawDimStrings(viewport, color)

#----------------------------------------------------------------------------------------------------
def _erase_dim(self, viewport):
    pass 
    # originally the erase_dim set the color of the dimansion equal to the background color
    # for deleting the dimension.
    # But when we close the application we get an error 
    # Adding pass to the erese_dim functions we not have any problems
    # self.draw(gimage, gimage.image.getOption('BACKGROUND_COLOR'))

