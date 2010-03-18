import wx
import os

from Interface.Wx.document import Document
from Interface.Wx.viewport import ViewPort


class CadWindow(wx.Frame):

    def __init__(self, parent, title):
        # standard file open location
        self.__dirname = ''

        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent, title=title, size=(-1, -1))
        # create viewport
        self._viewport = ViewPort(self)
        # create document
        self._document = Document(self, self._viewport)
        # A Statusbar in the bottom of the window
        self.CreateStatusBar()
        # Set up the file menu.
        filemenu = wx.Menu()
        file_open = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        file_about= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        file_exit = filemenu.Append(wx.ID_EXIT, "E&xit"," Terminate the program")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        filemenu.AppendSeparator()
        file_rebuild_index = filemenu.Append(-1, "Rebuild &Index"," Rebuild the spatial index")
        self.Bind(wx.EVT_MENU, self.OnRebuildIndex, file_rebuild_index)
        # Set up the view menu
        viewmenu = wx.Menu()
        view_clear = viewmenu.Append(-1, "&Clear viewport", " Erase the viewport")
        self.Bind(wx.EVT_MENU, self.OnClear, view_clear)
        view_zoom_all = viewmenu.Append(-1, "Zoom &All", " Show all entities in the drawing")
        self.Bind(wx.EVT_MENU, self.OnZoomAll, view_zoom_all)
        viewmenu.AppendSeparator()
        view_redraw = viewmenu.Append(-1, "&Redraw", " Redraw the visible entities")
        self.Bind(wx.EVT_MENU, self.OnRedraw, view_redraw)
        view_regen = viewmenu.Append(-1, "&Regen", " Regenerate the visible entities")
        self.Bind(wx.EVT_MENU, self.OnRegen, view_regen)
        
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(viewmenu, "&View") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.


        # Use some sizers to see layout options
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__sizer.Add(self._viewport, 1, wx.EXPAND)
        #Layout sizers
        self.SetSizer(self.__sizer)
        self.SetAutoLayout(1)
        self.__sizer.Fit(self)
        self.Show()

    def __GetDocument(self):
        return self._document

    Document = property(__GetDocument, None, None, "Gets the document")

    def __GetViewport(self):
        return self._viewport

    Viewport = property(__GetViewport, None, None, "Gets the viewport")


    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, " A sample editor \n in wxPython",
                            "About Sample Editor", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.


    def OnExit(self,e):
        self.Close(True)  # Close the frame.


    def OnOpen(self,e):
        """ Open a file"""
        dlg = wx.FileDialog(self, "Choose a drawing file", self.__dirname, "", "*.pdr", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.__filename = dlg.GetFilename()
            self.__dirname = dlg.GetDirectory()
            self._document.Open(os.path.join(self.__dirname, self.__filename))
        dlg.Destroy()


    def OnRebuildIndex(self,e):
        """
        Rebuild the spatial index in the database
        """
        self._document.RebuildIndex()
        wx.MessageBox("Ready rebuilding spatial index")
        
        
    def OnClear(self, e):
        """
        Make the viewport empty
        """
        self._viewport.Clear()
        
        
    def OnZoomAll(self,e):
        """
        Set up view translation and redraw all entities
        """
        self._viewport.ZoomAll()
        wx.MessageBox("Ready zoom to all entities")


    def OnRedraw(self,e):
        """
        redraw all entities
        """
        self._viewport.Redraw()
        wx.MessageBox("Ready redraw to all entities")
        
        
    def OnRegen(self,e):
        """
        Rebuild the display list and redraw all entities
        """
        self._document.Regen()
        self._viewport.Redraw()
        wx.MessageBox("Ready regenerate all entities")
        
                
        
        
