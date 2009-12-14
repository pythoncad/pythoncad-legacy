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
    return

    #
    # fixme - calculating dimensions needs rework!
    #
    length = self.calculate()

#    _slen = _image.scaleLength(self.calculate())
#    _dims = self.getDimensions(_slen)

    location_x, location_y = self.getLocation()

    primary_dimstring = secondary_dimstring = None
    layout1 = layout2 = None
    x1 = y1 = x2 = y2 = None

    if self.getDualDimMode():
        offset = self.getDualModeOffset()

        primary_dimstring = self.getPrimaryDimstring()

        layout1 = viewport.cairo_context.create_layout()
        layout1.set_text(primary_dimstring.getText())

        primary_dimstring._formatLayout(viewport, layout1)

        width1, height1 = primary_dimstring.getBounds()
        primary_dimstring.setLocation((location_x - (width1 / 2.0)), (location_y + height1 + offset))
        x1, y1 = primary_dimstring.getLocation()

        secondary_dimstring = self.getSecondaryDimstring()

        layout2 = viewport.cairo_context.create_layout()
        layout2.set_text(secondary_dimstring.getText())

        secondary_dimstring._formatLayout(viewport, layout2)

        width2, height2 = secondary_dimstring.getBounds()
        secondary_dimstring.setLocation((location_x - (width2 / 2.0)), (location_y - offset))
        x2, y2 = secondary_dimstring.getLocation()
        boundary_rect = (min(x1, x2), # xmin
                  y1, # ymax
                  max((x1 + width1), (x2 + width2)), # xmax
                  (y2 - height2)) # ymin



    else:
        primary_dimstring = self.getPrimaryDimstring()

        layout1 = viewport.cairo_context.create_layout()
        layout1.set_text(primary_dimstring.getText())

        primary_dimstring._formatLayout(viewport, layout1)
        width1, height1 = primary_dimstring.getBounds()
        primary_dimstring.setLocation((location_x - (width1 / 2.0)), (location_y + (height1 / 2.0)))
        x1, y1 = primary_dimstring.getLocation()
        boundary_rect = (x1, y1, (x1 + width1), (y1 - height1))

#    _bx1, _by1 = gimage.coordToPixTransform(boundary_rect[0], boundary_rect[1])
#    _bx2, _by2 = gimage.coordToPixTransform(boundary_rect[2], boundary_rect[3])

    background_color = _image.getOption('BACKGROUND_COLOR') #this is a string not an object
    print "Debug: background_color %s" % str(background_color)

    points = []
    points.add(Point(boundary_rect[0], boundary_rect[1]))
    points.add(Point(boundary_rect[2], boundary_rect[1]))
    points.add(Point(boundary_rect[2], boundary_rect[3]))
    points.add(Point(boundary_rect[0], boundary_rect[3]))
    # draw rectangle in background color
    self.draw_polygon(self, background_color, None, None, points, True)

    color = col
    # get the color from the object
    if color is None:
        color = primary_dimstring.getColor()
    # get the text location
    location = primary_dimstring.getLocation()
    # do the actual draw of the text
    viewport.draw_text(color, location, layout1)

    if secondary_dimstring is not None:
        color = col
        if color is None:
            color = secondary_dimstring.getColor()
        # get the text location
        location = secondary_dimstring.getLocation()
        # do the actual draw of the text
        viewport.draw_text(color, location, layout2)

        color = col

        if color is None:
            color = self.getColor()

        points = []
        points.add(Point(boundary_rect[0], location_y))
        points.add(Point(boundary_rect[2], location_y))
        # draw rectangle in background color
        self.draw_linestring(self, color, None, None, points)
    # cleanup
    layout2 = None
    layout1 = None


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
        points.append(p3)
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
        points.append(p3)
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
    # self.draw(viewport, viewport.Image.getOption('BACKGROUND_COLOR'))

