'''
Created on Mar 25, 2010

@author: gertwin
'''

import wx

wx.ID_COMMAND_ENTRY=6000


class Commandline(wx.Panel):
    '''
    Panel with command line controls
    '''

    def __init__(self, parent):
        '''
        Constructor
        '''
        wx.Panel.__init__(self, parent, id=-1)
        # function handler parses commandline expressions
        self._function_handler = None
        # command label and entry
        self._label = wx.StaticText(self, -1, "Command: ") 
        self._entry = wx.TextCtrl(parent=self, id=-1, value="", style=wx.TE_PROCESS_ENTER, name="COMMAND_ENTRY")
        self.Bind(wx.EVT_TEXT_ENTER, self.OnCommand, self._entry)
        # sizer
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self._label, 0, flag=wx.EXPAND)
        sizer.Add(self._entry, 1, flag=wx.EXPAND)
        # add sizer to panel
        self.SetSizer(sizer)
        #sizer.Fit(self) 
        #sizer.SetSizeHints(self)
        
        
    def SetFunctionHandler(self, function_handler):
        '''
        All expressions entered in the commandline are
        handled by the function handler
        '''
        self._function_handler = function_handler

        
    def OnCommand(self, event):
        '''
        Call the function handler with the expression from the commandline
        '''
        expression = self._entry.Value
        result = self._function_handler.Evaluate(expression)
        self._entry.Value = str(result)
        
        
    
        
        
        