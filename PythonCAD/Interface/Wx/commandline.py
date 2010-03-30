'''
Created on Mar 25, 2010

@author: gertwin
'''

import wx


class Commandline(wx.Panel):
    '''
    Panel with command line controls
    '''

    def __init__(self, parent):
        '''
        Constructor
        '''
        wx.Panel.__init__(self, parent, id=-1)
        # command label and entry
        self._label = wx.StaticText(self, -1, "Command: ") 
        self._entry = wx.TextCtrl(self, -1, "")
        # sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._label, 0, flag=wx.EXPAND)
        sizer.Add(self._entry, 1, flag=wx.EXPAND)
        # add sizer to panel
        self.SetSizer(sizer)
        #sizer.Fit(self) 
        #sizer.SetSizeHints(self)
        
        
        
        