#
# Copyright (c) 2010 Matteo Boscolo, Carlo Pavan
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
# This Module provide a polar guides management for the drawing scene and icommand
# 
#

import math

from PyQt4 import QtCore, QtGui

def getPolarMenu():
    '''
    returns a menu to operate with guide objects STILL TO BE IMPLEMENTED
    '''
    menu=QtGui.QMenu()
    return menu
        
class guideHandler(QtGui.QGraphicsItem):
    '''
    This class provide management of a guide Handler to be instanced by the scene
    on startup, and to be placed by iCommand when a point is succesfully added to a command
    '''
    def __init__(self, parent, x, y, a):
        super(guideHandler, self).__init__()
        self.scene=parent
        
        self.x=x
        self.y=y
        self.a=a
        
        self.guides=[]
        
        self.addGuidesByIncrement(math.pi/4)

        
    def setForceDirection(self, a):
        '''
        set scene.forceDirection to a angle
        '''
        self.scene.forceDirection=a
        
    def setIsGuided(self, bool):
        '''
        set scene.isGuided to bool value
        '''
        self.scene.isGuided=bool
        
    def setIsGuidLocked(self, bool):
        '''
        set scene.isGuideLocked to bool value
        '''
        self.scene.isGuideLocked=bool
    
    def addGuideByAngle(self, a):
        '''
        add guide by a angle
        '''
        guide(self, a)
        self.guides.append(a)
        
    def addGuidesByIncrement(self, a=math.pi/2):
        '''
        add guides by a increment angle
        '''
        self.clearGuides()
        guide(self, 0.0)
        i=0.0
        while i<math.pi*2:
            g=guide(self, i)
            self.guides.append(g)
            i=i+a
        return
    
    def clearGuides(self):
        '''
        delete all guides   STILL DOESN'T WORK HELPPPPPPPPPPPPPPPPPPPPP
        '''
        for i in self.childItems():
            i.kill()
            
    def place(self, x, y):
        '''
        set position of the handler (called by icommand)
        '''
        self.setPos(x, y*-1)
    
    def reset(self):
        '''
        reset position of the handler and hides it
        '''
        try:
            self.scene.forceDirection=None
            self.setPos(0.0, 0.0)
            self.hide()
        except:
            return
    
    def hideGuides(self):
        '''
        hides every guide children
        '''
        for i in self.childItems():
            i.hide()
        
    def boundingRect(self):
        return self.childrenBoundingRect()
    
    def paint(self, painte, option, widget):
        return
        
class guide(QtGui.QGraphicsLineItem):
    '''
    This class provide a guide object and it's management
    it's added to the guideHandler object
    '''
    def __init__(self, parent=None, a=0.0):
        super(guide, self).__init__(parent)
        self.handler=parent
        #Flags
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations, True)
        self.setAcceptsHoverEvents(True)
        #Events
        
        self.a=parent.a+a
        line=QtCore.QLineF(0.0, 0.0, 20000*math.cos(a), (20000*math.sin(a))*-1)
        self.setLine(line)
        self.setToolTip("Guide [Press Shift to lock direction] "+ str(self.a)+"rad")
        
        self.highlightPen=QtGui.QPen(QtGui.QColor(150, 150, 150, 255), 1, QtCore.Qt.DotLine)
        self.hidePen=QtGui.QPen(QtGui.QColor(255, 50, 50, 0),1, QtCore.Qt.DotLine)
        
        self.setPen(self.hidePen)
        self.hide()
    
    def hide(self):
        self.setPen(self.hidePen)
        self.handler.setForceDirection(None)
        self.handler.setIsGuided(None)
        
    def kill(self):
        
        del self
        
    def shape(self):
        x=self.pos().x()
        y=self.pos().y()
        P1=QtCore.QPointF(x+10*math.cos(self.a-0.4), y-10*math.sin(self.a-0.4))
        P2=QtCore.QPointF(x+20000*math.cos(self.a-0.03), y-20000*math.sin(self.a-0.03))
        P3=QtCore.QPointF(x+20000*math.cos(self.a+0.03), y-20000*math.sin(self.a+0.03))
        P4=QtCore.QPointF(x+10*math.cos(self.a+0.4), y-10*math.sin(self.a+0.4))
        poly=QtGui.QPolygonF([P1, P2, P3, P4])
        #self.handler.scene.addPolygon(poly) #this is for checking the design of snapping guides
        shp=QtGui.QPainterPath()
        shp.addPolygon(poly)
        return shp
        
        return shp
        
    def hoverEnterEvent(self, event):
        if self.handler.scene.isGuideLocked==None:
            self.handler.hideGuides()
            self.setPen(self.highlightPen)
            self.handler.setForceDirection(self.a)
            self.handler.setIsGuided(True)
        super(guide, self).hoverEnterEvent(event)
        return
        
    def hoverLeaveEvent(self, event):
        if self.handler.scene.isGuideLocked==None:
            self.hide()
            #self.update(self.boundingRect())
        super(guide, self).hoverLeaveEvent(event)
