
import wx

#Custom menu id 
wx.ID_IMPORT=6000


class MenuBar(wx.MenuBar):
    
    def __init__(self, parent):
        '''
        Creates the menubar
        '''
        wx.MenuBar.__init__(self)
        self._parent = parent
        # construct menus
        filemenu = self._CreateFileMenu()
        editmenu = self._CreateEditMenu()
        viewmenu = self._CreateViewMenu()
        # construct menubar
        self.Append(filemenu, "&File")
        self.Append(editmenu, "&Edit")
        self.Append(viewmenu, "&View")
        
        
        
    def _CreateFileMenu(self):
        filemenu = wx.Menu()
        file_open = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        self._parent.Bind(wx.EVT_MENU, self.OnInvoke, id=wx.ID_OPEN)
        file_import= filemenu.Append(wx.ID_IMPORT, "I&mport"," Import an external format")
        self.Bind(wx.EVT_MENU, self.OnInvoke, id=wx.ID_IMPORT)
        file_about= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.Bind(wx.EVT_MENU, self.OnInvoke, id=wx.ID_EXIT)
        file_exit = filemenu.Append(wx.ID_EXIT, "E&xit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnInvoke, id=wx.ID_ABOUT)
        filemenu.AppendSeparator()
        file_rebuild_index = filemenu.Append(-1, "Rebuild &Index"," Rebuild the spatial index")
        self.Bind(wx.EVT_MENU, self.OnInvoke, file_rebuild_index)
        return filemenu

        
    def _CreateEditMenu(self):
        editmenu= wx.Menu()
        edit_undo = editmenu.Append(wx.ID_UNDO, "&Undo", " Perform Undo")
        self.Bind(wx.EVT_MENU, self.OnInvoke, id=wx.ID_UNDO)
        edit_redu = editmenu.Append(wx.ID_REDO, "&Redo", " Perform Redo")
        self.Bind(wx.EVT_MENU, self.OnInvoke,  id=wx.ID_REDO)
        return editmenu

        
    def _CreateViewMenu(self):
        viewmenu = wx.Menu()
        view_clear = viewmenu.Append(-1, "&Clear viewport", " Erase the viewport")
        self.Bind(wx.EVT_MENU, self.OnInvoke, view_clear)
        view_zoom_all = viewmenu.Append(-1, "Zoom &All", " Show all entities in the drawing")
        self.Bind(wx.EVT_MENU, self.OnInvoke, view_zoom_all)
        viewmenu.AppendSeparator()
        view_redraw = viewmenu.Append(-1, "&Redraw", " Redraw the visible entities")
        self.Bind(wx.EVT_MENU, self.OnInvoke, view_redraw)
        view_regen = viewmenu.Append(-1, "&Regen", " Regenerate the visible entities")
        self.Bind(wx.EVT_MENU, self.OnInvoke, view_regen)
        return viewmenu
        
        
         
    def OnInvoke(self, event):
        self._parent.Document.FunctionHandler.Evaluate("OPEN")
 
        
        