
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
        # table with entries menu_id => command
        self._commands = {}
        # construct menus
        self.CreateMenuBar()
        
        
    def CreateMenuBar(self):
        for menu_data in self.MenuData():
            menu_label = menu_data[0]
            menu_items = menu_data[1]
            self.Append(self.CreateMenu(menu_items), menu_label)


    def CreateMenu(self, menu_data):
        menu = wx.Menu()
        for item in menu_data:
            if len(item) == 2:
                label = item[0]
                sub_menu = self.CreateMenu(item[1])
                menu.AppendMenu(wx.NewId(), label, sub_menu)
            else:
                self.CreateMenuItem(menu, *item)
        return menu
    

    def CreateMenuItem(self, menu, label, id, help, command, handler, kind=wx.ITEM_NORMAL):
        if not label:
            menu.AppendSeparator()
            return
        menu_item = menu.Append(id, label, help, kind)
        # bind command to menu item id
        self._commands[id] = command
        self._parent.Bind(wx.EVT_MENU, handler, menu_item)

         
    def OnInvoke(self, event):
        id = event.GetId()
        # search the command
        if self._commands.has_key(id):
            command = self._commands[id]
            # execute the command
            self._parent.SendExpression(command)
        else:
            # this should not happen
            pass

#------------------------ define menu data ----------------------#

    def MenuData(self):
        return [("&File", (
                           ("&New", wx.ID_NEW, "New Drawing file", "NEW", self.OnInvoke),
                           ("&Open", wx.ID_OPEN, "Open Drawing file", "OPEN", self.OnInvoke),
                           ("&Close", wx.ID_CLOSE, "Close Drawing file", "CLOSE", self.OnInvoke),
                           ("", -1, "", "", None),
                           ("&Rebuild Index", -1, "Rebuild search index", "REBUILD_IX", self.OnInvoke),
                           ("", -1, "", "", None),
                           ("&Quit", wx.ID_EXIT, "Quit", "QUIT", self.OnInvoke)))
        
        
        ]
        
        
        
        
        