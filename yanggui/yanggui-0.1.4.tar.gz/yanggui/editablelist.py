import wx
import wx.lib.mixins.listctrl  as  listmix

########################################################################
class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''

    #----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

########################################################################
class MyPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent)

        rows = [("Ford", "Taurus", "1996", "Blue"),
                ("Nissan", "370Z", "2010", "Green"),
                ("Porche", "911", "2009", "Red")
                ]
        self.list_ctrl = EditableListCtrl(self, style=wx.LC_REPORT)

        self.list_ctrl.InsertColumn(0, "Make")
        self.list_ctrl.InsertColumn(1, "Model")
        self.list_ctrl.InsertColumn(2, "Year")
        self.list_ctrl.InsertColumn(3, "Color")

        index = 0
        for row in rows:
            self.list_ctrl.InsertStringItem(index, row[0])
            self.list_ctrl.SetStringItem(index, 1, row[1])
            self.list_ctrl.SetStringItem(index, 2, row[2])
            self.list_ctrl.SetStringItem(index, 3, row[3])
            index += 1
        self.list_ctrl.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnUpdate)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)

    def OnUpdate(self, event):
        row_id = event.GetIndex() #Get the current row
        col_id = event.GetColumn () #Get the current column
        new_data = event.GetLabel() #Get the changed data
        cols = self.list_ctrl.GetColumnCount() #Get the total number of columns
        rows = self.list_ctrl.GetItemCount() #Get the total number of rows

        #Get the changed item use the row_id and iterate over the columns
        print (" ".join([self.list_ctrl.GetItem(row_id, colu_id).GetText() for colu_id in range(cols)]))
        print("Changed Item:", new_data, "Column:", col_id)

        #Get the entire listctrl iterate over the rows and the columns within each row
        print("\nEntire listctrl BEFORE the update:")
        for row in range(rows):
            row_data = (" ".join([self.list_ctrl.GetItem(row, col).GetText() for col in range(cols)]))
            print(row_data)

        #Set the new data in the listctrl
        self.list_ctrl.SetStringItem(row_id,col_id,new_data)

        print("\nEntire listctrl AFTER the update:")
        #Create a list that can be used to export data to a file
        data_for_export=[]
        for row in range(rows):
            row_data = (" ".join([self.list_ctrl.GetItem(row, col).GetText() for col in range(cols)]))
            print(row_data)
            data_for_export.append(row_data) #Add to the exportable data

        print("\nData for export")
        for row in data_for_export: #Print the data
            print(row)

########################################################################
class MyFrame(wx.Frame):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY, "Editable List Control")
        panel = MyPanel(self)
        self.Show()

#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame()
    app.MainLoop() 