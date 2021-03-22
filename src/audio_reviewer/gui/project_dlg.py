

import wx

class ProjectDialog(wx.Dialog):
  
  @property
  def CONFIG(self):
    return settings.CONFIG

  def __init__(self, parent, title='New Project Wizard', pos=(-1,-1), size=(700,400),
    style=wx.DEFAULT_FRAME_STYLE|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER):
#    style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.DOUBLE_BORDER):

    self.frame = parent
    wx.Dialog.__init__(self, parent, -1, title, pos, size, style)
    self.SetBackgroundColour('#E5E5E5')

    font = wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
    title = wx.StaticText(self, -1, "Step 1: Setup Project")
    title.SetFont(font)
    
    chars = 440
    l1 = wx.StaticText(self, -1, "Project Name:", style=wx.ALIGN_RIGHT)
    self.project_nameTC = wx.TextCtrl(self, -1, "see", size=(chars, -1))

    l2 = wx.StaticText(self, -1, "Project Path:", style=wx.ALIGN_RIGHT)
    self.project_pathTC=wx.TextCtrl(self,-1,"Empty Directory",size=(chars,-1))
    self.project_pathTC.Disable()

    select_button = wx.Button(self, 20, "&SELECT", (20, 80)) 
#   select_button.SetDefault()
    select_button.SetSize(select_button.GetBestSize())
    self.Bind(wx.EVT_BUTTON, self.onSelectDir, select_button)

    select_button.SetToolTipString("Select the Directory to store your project in.")

    space = 6

    sizer = wx.FlexGridSizer(cols=3, hgap=space, vgap=space)
    sizer.AddMany([ l1, self.project_nameTC, (0,0),
                    l2, self.project_pathTC, select_button
                    ])
    border = wx.BoxSizer(wx.VERTICAL)
    border.Add(title, 0, wx.ALL, 25)
    border.Add(sizer, 0, wx.ALL, 25)
    self.SetSizer(border)
    self.SetAutoLayout(True)

    '''
    import_box = wx.StaticBox(self, -1, "Audio Files", size=(625, 120),
      pos=(25, 160) )

    bsizer = wx.StaticBoxSizer(import_box, wx.VERTICAL)

    import_check = wx.CheckBox(self, -1, "Import")

    # item, int proportion=0, int flag=0, int border=0,
    bsizer.Add(import_check, 0, wx.TOP|wx.LEFT, 10)
    '''

    self.build_button = wx.Button(self, -1, "Build", (460, 310) )
    self.build_button.SetSize(self.build_button.GetBestSize())
    self.Bind(wx.EVT_BUTTON, self.onSave, self.build_button)

    self.cancel_button = wx.Button(self, -1, "Cancel", (560, 310) )
    self.cancel_button.SetSize(self.cancel_button.GetBestSize())
    self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancel_button)

  def onSave(self, evt):

    name = self.project_nameTC.GetValue()
    path = self.project_pathTC.GetValue()

#    print('onSave called, self.project_nameTC.GetValue() is: %s' % name)

    self.CONFIG.project_name = name
#    print('now in CONFIG, value is: %s' % self.CONFIG.project_name)
    self.CONFIG.project_path = path

#   print('passsing into Project __init__ :%s' % self.CONFIG.project_name)

    project = Project(name=self.CONFIG.project_name,
      path=self.CONFIG.project_path)

    project.create()

    self.frame.loadProject()

    last_project = "%s::%s" % (self.CONFIG.project_name, self.CONFIG.project_path)
    last_projects = self.CONFIG.get('last_projects', [])
    if last_project in last_projects:
      del last_projects[ last_projects.index(last_project) ]

    last_projects.reverse()
    last_projects.append( last_project )
    last_projects.reverse()

    self.CONFIG.last_projects=last_projects[:10]
    self.CONFIG['last_projects'] = self.CONFIG.last_projects

    self.CONFIG.save()

    self.frame.setTitle(name)

    self.Close()
    return wx.ID_OK

  def onCancel(self, evt):
    self.Close()
    return wx.ID_CANCEL

  def onSelectDir(self, evt):
    name = ''
    # In this case we include a "New directory" button. 
    dlg = wx.DirDialog(self, "Choose a directory:",
              style=wx.DD_DEFAULT_STYLE#| wx.DD_DIR_MUST_EXIST
               #| wx.DD_CHANGE_DIR
    )

    # If the user selects OK, then we process the dialog's data.
    # This is done by getting the path data from the dialog - BEFORE
    # we destroy it. 
    if dlg.ShowModal() == wx.ID_OK:
      path = os.path.abspath( dlg.GetPath() )

      if not os.path.exists(path):
        self.showError('Missing Directory', \
          "This directory does not exist: \n%s" % path)
      else:
        if self.isEmpty(path):
          self.project_pathTC.Enable()
          self.project_pathTC.SetValue(path)
          self.project_pathTC.Disable()
        else:
          self.showProjectNotEmptyError(path)
          return self.onSelectDir(evt)

    # Only destroy a dialog after you're done with it.
    dlg.Destroy()
      
  def isEmpty(self, directory):
    import glob
    retval = True
    for root, dirs, files in os.walk(os.path.abspath(directory),topdown=False):
      if len(dirs) or len(files):
        retval = False

    return retval

  def showProjectNotEmptyError(self, path):
    dlg = wx.MessageDialog(self, "%s is not EMPTY.\n" \
      'You selected a folder with files or ' \
      'folders in it.  You must SELECT or CREATE an EMPTY folder.' % path,
       'Please try again,...', wx.OK | wx.ICON_WARNING)
    dlg.ShowModal()
    dlg.Destroy()
