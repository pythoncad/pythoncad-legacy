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
        # create document
        self.__document = Document(self)
        # create viewport
        self.__viewport = ViewPort(self)
        # A Statusbar in the bottom of the window
        self.CreateStatusBar()
        # Setting up the menu.
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
        menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Events.
        self.Bind(wx.EVT_MENU, self.OnOpen, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)

        # Use some sizers to see layout options
        self.__sizer = wx.BoxSizer(wx.VERTICAL)
        self.__sizer.Add(self.__viewport, 1, wx.EXPAND)
        #Layout sizers
        self.SetSizer(self.__sizer)
        self.SetAutoLayout(1)
        self.__sizer.Fit(self)
        self.Show()

    def __GetDocument(self):
        return self.__document

    Document = property(__GetDocument, None, None, "Gets the document")

    def __GetViewport(self):
        return self.__viewport

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
            self.__document.Open(os.path.join(self.__dirname, self.__filename))
        dlg.Destroy()

