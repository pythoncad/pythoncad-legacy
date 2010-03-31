'''
Created on Mar 25, 2010

@author: gertwin
'''

import wx
from Interface.FunctionParser.functionhandler import FunctionHandler





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
        self._function_handler = FunctionHandler(self)
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
        
        
    def _GetFunctionHandler(self):
        return self._function_handler
    
    FunctionHandler = property(_GetFunctionHandler, None, None, "Get the function handler")
    
        
    def OnCommand(self, event):
        '''
        Call the function handler with the expression from the commandline
        '''
        expression = self._entry.Value
        self.Evaluate(expression)


    def RegisterCommand(self, name, callback):
        '''
        Convenient function to register a command
        '''
        self._function_handler.RegisterCommand(name, callback)
        
        
    def Evaluate(self, expression):
        '''
        Evaluate a expression / send a command
        '''
        # show it in the command line
        self._entry.Value = expression
        # check if it is a string
        if type(expression) is str or type(expression) is unicode:
            result = self._function_handler.Evaluate(expression)
            # show the result in the command line
            self._entry.Value = str(result)
        
        