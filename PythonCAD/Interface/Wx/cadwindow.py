import wx
import os

from Interface.Wx.menubar import MenuBar
from Interface.Wx.document import Document
from Interface.Wx.viewport import ViewPort
from Interface.Wx.commandline import Commandline


#Custom menu id 
wx.ID_IMPORT=6000

class CadWindow(wx.Frame):

    def __init__(self):
        # standard file open location
        self.__dirname = ''
        
        # A "-1" in the size parameter instructs wxWidgets to use the default size.
        # In this case, we select 200px width and the default height.
        wx.Frame.__init__(self, parent=None, title="PythonCAD Wx", size=(800,600))

        # create controls
        self._CreateControls()
        
        # create document
        self._document = Document(self, self._viewport)
        
        # Creating the menubar.
        menu_bar = MenuBar(self)
        self.SetMenuBar(menu_bar)  # Adding the MenuBar to the Frame content.
        
        self._RegisterCommands()

        # create viewport
        #self._viewport = ViewPort(self)
        # A Statusbar in the bottom of the window
        #self.CreateStatusBar()
        
        self.Bind(wx.EVT_SIZE, self.OnResize)
        
        self.Show()
        
        
    def OnResize(self, event):
        if self.GetAutoLayout():
            self.Layout()
        
    def _GetCommandline(self):
        return self._commandline
    
    Commandline = property(_GetCommandline, None, None, "Reference to the commandline")
    
    
    def _CreateControls(self):
        # viewport
        self._viewport = ViewPort(self)
        # commandline
        self._commandline = Commandline(self)
        # sizer
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self._viewport, 1, flag=wx.EXPAND)
        self._sizer.Add(self._commandline, 0, flag=wx.EXPAND)
        # add sizer to frame
        self.SetAutoLayout(True)
        self.SetSizer(self._sizer)
        self.Layout()
        #self._sizer.Fit(self) 
        #self._sizer.SetSizeHints(self)
        self.Fit()
        # A Statusbar in the bottom of the window
        self.CreateStatusBar()
              
        

    def _GetDocument(self):
        return self._document

    Document = property(_GetDocument, None, None, "Gets the document")

    def __GetViewport(self):
        return self._viewport

    Viewport = property(__GetViewport, None, None, "Gets the viewport")
    
    
    
    def _RegisterCommands(self):
        '''
        Register commands available for this object
        '''
        self.Document.FunctionHandler.RegisterCommand("OPEN", self.OnOpen)
        self.Document.FunctionHandler.RegisterCommand("QUIT", self.OnExit)
        self.Document.FunctionHandler.RegisterCommand("IMPORT", self.OnImport)
        self.Document.FunctionHandler.RegisterCommand("ABOUT", self.OnAbout)
    


    def OnAbout(self,e):
        # Create a message dialog box
        dlg = wx.MessageDialog(self, "PythonCAD a 2D CAD program.", "About PythonCAD", wx.OK)
        dlg.ShowModal() # Shows it
        dlg.Destroy() # finally destroy it when finished.


    def OnExit(self,e):
        self.Close(True)  # Close the frame.


    def OnOpen(self):
        """ 
        Open a file
        """
        dlg = wx.FileDialog(self, "Choose a drawing file", self.__dirname, "", "*.pdr", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.__filename = dlg.GetFilename()
            self.__dirname = dlg.GetDirectory()
            self._document.Open(os.path.join(self.__dirname, self.__filename))
        dlg.Destroy()
        
    
    def OnImport(self, e):
        """
            on import call back
        """
        dlg = wx.FileDialog(self, "Choose a drawing file", self.__dirname, "", "*.dxf", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            
            _filename = dlg.GetFilename()
            _dirname = dlg.GetDirectory()
            self._document.Import(os.path.join(_dirname, _filename))
        dlg.Destroy()
        
        
    def OnUndo(self, e):
        """
            perform undo operation
        """
        self._document.undo()
        self._viewport.Redraw()

        
    def OnRedo(self, e):
        """
            perform redo operation
        """     
        self._document.redo()
        self._viewport.Redraw()
  
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
        
                
        
        
