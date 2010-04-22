'''
Created on Mar 18, 2010

@author: gertwin
'''



class DisplayPoint(object):
    '''
    Point for use in a display object
    '''
    def __init__(self, point):
        self._x = point.x
        self._y = point.y
        
        
    def _GetX(self):
        return self._x
    
    def _SetX(self, x):
        self._x = x
        
    X = property(_GetX, _SetX, None, "get/set x ordinate")    
    
    
    def _GetY(self):
        return self._y
    
    def _SetY(self, y):
        self._y = y
        
    Y = property(_GetY, _SetY, None, "get/set y ordinate")
    
