#!/usr/bin/env python
# encoding=utf-8

import os, sys
from datetime import datetime
from pprint import pprint, pformat

from ConfigParser import ConfigParser as CP

from gui.log_frame import LogFrame
from gui.project_dlg import ProjectDialog
from gui.media_panel import MediaPanel
from gui.panel import LeftPane, RightPane, CenterPane, BottomPane

from images import getMyIconIcon, getDarkPiSymbolIcon

from lib import mbool
from lib import settings
from lib.project import Project
from lib import config_file_path, config_dir
from lib.log import log
from lib.util import prettyNow
from lib.settings import _program_name

import wx
from wx.lib.splitter import MultiSplitterWindow

class MainFrame(wx.Frame):
  first_run = True
  _project = Project()

  wildcard = "Audio Files (*.midi, *.m4a, *.mp3, *.wav, *.wma)|" \
    "*.midi; *.m4a; *.mp3; *.wav; *.wma|" \
    "M4A (*.m4a)|*.m4a|" \
    "MP3 (*.mp3)|*.mp3|" \
    "WAV (*.wav)|*.wav" \
    "|WMA (*.wma)|*.wma"

  acceptable_extensions = ['.midi', '.m4a', '.mp3', '.wav', '.wma']

  default_audio_import_directory = os.getcwd()

  def set_project(self, obj):
    self._project=obj
  def get_project(self):
    return self._project
  Project = property(get_project, set_project)

  @property
  def CONFIG(self):
    return settings.CONFIG

  @property
  def project_name(self):
    return self.Project.name

  @property
  def project_path(self):
    return self.Project.path

  def __init__(self, parent, title, pos=(-1,-1), size=(1000,600),
    style=wx.DEFAULT_FRAME_STYLE):
#    style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.DOUBLE_BORDER):
    global log

    wx.Frame.__init__(self, parent, -1, title, pos, size, style)

    self.parent = parent

    self.Bind(wx.EVT_CLOSE, self.OnClose, self)

    log = self.setLogging()

    self.SetBackgroundColour('#FFFFFF')
#    self.Maximize()

    try:
      #self.SetIcon(getDarkPiSymbolIcon())
      self.SetIcon(getMyIconIcon())
    finally:
      pass

    self.hsplitter = wx.SplitterWindow(self, -1)
    sty = wx.SIMPLE_BORDER
    sty2 = wx.SIMPLE_BORDER
    
    self.top = wx.Window(self.hsplitter, size=(800, 450), style=sty2)
    self.top.Show(False)
    self.top.SetBackgroundColour("pink")

    vsplitter = MultiSplitterWindow(self.top, style=0)
    self.vsplitter  = vsplitter
  
    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(vsplitter, 99, wx.EXPAND)
    self.top.SetSizer(sizer)


    self.lp = LeftPane(self.vsplitter, self, log, size=(280, 450), style=sty)
    self.lp.Show(True)
#    self.lp.SetOtherLabel("File Browser")
    self.lp.SetMinSize((200,440))
    self.vsplitter.AppendWindow(self.lp, 280)

    self.cp = CenterPane(self.vsplitter, self, log, size=(440, 450), style=sty)
    self.cp.Show(True)
    self.vsplitter.AppendWindow(self.cp, 440)
    self.cp.SetMinSize(self.cp.GetBestSize())

    self.rp = RightPane(self.vsplitter, self, log, size=(180, 450), style=sty)
    self.rp.Show(True)
    self.rp.MaxSize = (200,2880)
    self.rp.SetOtherLabel("Bookmark View")
    self.vsplitter.AppendWindow(self.rp, 180)

    self.bp = MediaPanel(self.hsplitter, self, log, size=(800, 150), 
#      pos=(0, 450), 
      style=sty2)
    
    self.bp.Show(True)
    self.bp.SetMaxSize((1280,150))
    self.bp.SetMinSize((600,150))
#    self.bp.SetOtherLabel("Media Player")

    self.hsplitter.SetMinimumPaneSize(150)
    self.hsplitter.SplitHorizontally(self.top, self.bp, -100)

    self.statusBar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
    self.statusBar.SetStatusWidths([-2, -1])

    statusText = "Welcome to the PyTis Audio Reviewer!"
    self.statusBar.SetStatusText(statusText, 0)

    self.createMenu()
    self.loadConfig()
    self.Bind(wx.EVT_SIZE, self.OnResize, self)
    '''
    self.Bind(wx.EVT_SIZE, self.onFutureFeature, self)
#    self.Bind(wx.EVT_SIZE, self.onFutureFeature, self)
    '''
    self.disableProjectMenus()

    sp = wx.StandardPaths.Get()
    log = self.log
    log.debug("GetAppDocumentsDir: %s" % sp.GetAppDocumentsDir() )
    log.debug("GetDataDir: %s" % sp.GetDataDir() )
    log.debug("GetDocumentsDir: %s" % sp.GetDocumentsDir() )
    log.debug("GetExecutablePath: %s" % sp.GetExecutablePath() )
    log.debug("GetInstallPrefix: %s" % sp.GetInstallPrefix() )
    log.debug("GetLocalDataDir: %s" % sp.GetLocalDataDir() )
    log.debug("GetLocalizedResourcesDir: %s" % sp.GetLocalizedResourcesDir(lang='en') )
    log.debug("GetPluginsDir: %s" % sp.GetPluginsDir() )
    log.debug("GetResourcesDir: %s" % sp.GetResourcesDir() )
    log.debug("GetTempDir: %s" % sp.GetTempDir() )
    log.debug("GetUserConfigDir: %s" % sp.GetUserConfigDir() )
    log.debug("GetUserDataDir: %s" % sp.GetUserDataDir() )
    log.debug("GetUserLocalDataDir: %s" % sp.GetUserLocalDataDir() )
    log.debug("UseAppInfo: %s" % sp.UseAppInfo(info=0) )
    log.debug("UseAppInfo: %s" % sp.UseAppInfo(info=1) )
    log.debug("UseAppInfo: %s" % sp.UseAppInfo(info=2) )
    log.debug("UsesAppInfo: %s" % sp.UsesAppInfo(info=0) )
    log.debug("UsesAppInfo: %s" % sp.UsesAppInfo(info=1) )
    log.debug("UsesAppInfo: %s" % sp.UsesAppInfo(info=2) )
    log.debug("AppInfo_AppName: %s" % sp.AppInfo_AppName )
    log.debug("AppInfo_None: %s" % sp.AppInfo_None )
    log.debug("AppInfo_VendorName: %s" % sp.AppInfo_VendorName )

    self.default_audio_import_directory = str(sp.GetDocumentsDir()).replace(
      'Documents', 'Music')

    if 'Music' not in self.default_audio_import_directory:
      self.default_audio_import_directory = os.getcwd()

    self.log.debug('default_audio_import_directory: %s' % \
      self.default_audio_import_directory)

    self.currentFolder = sp.GetDocumentsDir()
  #----------------------------------------------------------------------
  def createMenu(self):
    """
    Creates a menu
    """
    menu_bar = wx.MenuBar()
    
    #----------------------------------------------------------------------
    self.file_menu = wx.Menu()
    self.open_file_menu_item = self.file_menu.Append(wx.NewId(), "&Open",
      "Open audio File -- REMOVE LATER")
    self.Bind(wx.EVT_MENU, self.onBrowse, self.open_file_menu_item)

    self.new_project_menu_item = self.file_menu.Append(wx.NewId(), "&New Project\tCTRL+N",
      "Start a Project")
    self.Bind(wx.EVT_MENU, self.onNewProject, self.new_project_menu_item)

    self.import_menu_item = self.file_menu.Append(wx.NewId(), "&Import Audio File(s)",
      "Import Audio Files")
    self.Bind(wx.EVT_MENU, self.onImportAudioFiles, self.import_menu_item)

    self.import_menu_item2 = self.file_menu.Append(wx.NewId(), "&Import Audio from Dir",
      "Import Audio from Folder")
    self.Bind(wx.EVT_MENU, self.onImportAudioFromFolder, self.import_menu_item2)

    self.settings_menu_item = self.file_menu.Append(wx.NewId(), "Project &Settings",
      "Project Settings")
    self.Bind(wx.EVT_MENU, self._on_options, self.settings_menu_item)

    self.export_menu_item = self.file_menu.Append(wx.NewId(), "&Export",
      "Export one thing")
    self.Bind(wx.EVT_MENU, self.onFutureFeature, self.export_menu_item)

    self.export_all__menu_item = self.file_menu.Append(wx.NewId(), "&Export Full Report",
      "Export Full Report Wizzard")
    self.Bind(wx.EVT_MENU, self.onFutureFeature, self.export_all__menu_item)

    self.file_menu.AppendSeparator()
   
    self.file_history = []
    for i, prj in enumerate(self.CONFIG.get('last_projects', [])):
      name,path=prj.split('::')
      if not name: name = 'N/A'
      if not path: path = ''

      menu_item = self.file_menu.Append(wx.NewId(), name, path)

      # XXX-TODO
      # this is too advanced for now, but the first item in history should
      # be disabled, the trick is re-eneabling it as it becomes the second,
      # and so on 
      if i == 0 and False:
        menu_item.Enable(False)
      # always bind, because it could get shifted down, then it needs to be
      # bound

      self.Bind(wx.EVT_MENU, self.onOpenPastItem(name, path), menu_item)
      self.file_history.append( (menu_item, name, path) )

    self.file_menu.AppendSeparator()
    exit__menu_item = self.file_menu.Append(wx.NewId(), "E&xit\tCTRL+Q",
      "Exit Program")

    self.Bind(wx.EVT_MENU, self.onClose, exit__menu_item)

    menu_bar.Append(self.file_menu, '&File')
    #----------------------------------------------------------------------

    options_menu = wx.Menu()
    
    self.debug_window_item = options_menu.Append(wx.NewId(),
      "&Debug Window\tCTRL+D",
      "Show / Hide the Debugging Window.", wx.ITEM_CHECK) #

    self.Bind(wx.EVT_MENU, self.onToggleDebugFrame,
      self.debug_window_item)

    options_menu_item = options_menu.Append(wx.NewId(), "&Convert Audio Files",
      "Convert to *mp3")
    self.Bind(wx.EVT_MENU, self.onConvertAudioFiles, options_menu_item)
    menu_bar.Append(options_menu, '&Options')

    #----------------------------------------------------------------------

    self.SetMenuBar(menu_bar)

  ##################################################################
  # Project Management

  def newProject(self):
    # first get the name
    dlg = ProjectDialog(self)
    dlg.ShowModal()
    return
    self.project_name = self.getProjectName()
    self.project_path = self.onSelectDir(None)
    return
    # now get a path

  def closeProject(self):
    self.disableProjectMenus()

  def resetLastProject(self):
    last_project = "%s::%s" % (self.CONFIG.project_name, 
      self.CONFIG.project_path)

    last_projects = self.CONFIG.get('last_projects', [])
    if last_project in last_projects:
      del last_projects[ last_projects.index(last_project) ]

    last_projects.reverse()
    last_projects.append( last_project )
    last_projects.reverse()
    self.CONFIG.last_projects=last_projects[:10]
    self.CONFIG['last_projects'] = self.CONFIG.last_projects
    self.CONFIG.save()

  def setCurrentProject(self, name, path):
    self.Project = Project(name, path)
    self.CONFIG['project_path'] = self.project_path
    self.CONFIG['project_name'] = self.project_name
    self.CONFIG.save()



  #def openProject(self, name=str_or_obj, path=str):
  def openProject(self, name_or_prj='', path=''):
    if str(type(name_or_prj)) == "<class 'lib.project.Project'>":
      name = str(name_or_prj.name)
      path = str(name_or_prj.path)
    else:
      name = name_or_prj

    if str(name).strip() and path.strip():
      self.log.info("open project running")
      self.setCurrentProject(name, path)
      self.lp.openProject(self.Project)
      self.enableProjectMenus()
      self.resetLastProject()
      self.currentFolder = os.path.abspath(path)
    else:
      self.log.debug("could not open project. type of first input " \
        "name_or_prj is: %s, and value is: %s" % ( str(type(name_or_prj)),
        str(name_or_prj)))

  ##################################################################
  # DLGs

  def getProjectName(self):
    a='Project Name:'
    b='What would you like to name your Project?'
    c=''
    name = ''

    dlg = wx.TextEntryDialog(self, a, b, c)

#    dlg.SetValue(c)

    if dlg.ShowModal() == wx.ID_OK:
      name = dlg.GetValue()

    dlg.Destroy()
    return name

  def showError(self, err_name, err_msg, icon=wx.ICON_ERROR):
    
    dlg = wx.MessageDialog(self, err_msg,
       err_name, wx.OK | icon
       )
    dlg.ShowModal()
    dlg.Destroy()

  ##################################################################
  # 


  ##################################################################
  # Actions

  def disableProjectMenus(self):
    self.import_menu_item.Enable(False)
    self.import_menu_item2.Enable(False)
    self.settings_menu_item.Enable(False)
    self.export_menu_item.Enable(False)
    self.export_all__menu_item.Enable(False)

  def enableProjectMenus(self):
    self.import_menu_item.Enable(True)
    self.import_menu_item2.Enable(True)
    self.settings_menu_item.Enable(True)
    self.export_menu_item.Enable(True)
    self.export_all__menu_item.Enable(True)

  def futureFeature(self, text='This feature is not yet implemented.'):
    global log
    log.info1('test tst2')
    log.warn('test WARN test')
    return self.showError('Comming Soon,..', text, wx.ICON_INFORMATION)

  ##################################################################
  # BEGIN EVENTS 

  def onFutureFeature(self, evt):
    evt.Skip()
    wx.LogMessage("event dir:%s" % dir(evt))
    wx.LogMessage("event type:%s" % type(evt))
    wx.LogMessage("event repr:%s" % repr(evt))
    wx.LogMessage("event str:%s" % str(evt))
    return self.futureFeature()

  def onOpenPastItem(self, name, path):

    def onOpenPastItem_event(evt):
      
      new_pos = 0
      for item in self.file_menu.GetMenuItems():
        if item.GetId() == self.file_history[0][0].GetId():
          break
        new_pos += 1
          
      for i, item in enumerate(self.file_history):
        item, iname, ipath = item
        if item.GetId() == evt.GetId():
          del self.file_history[i]
          self.file_history.insert(0, (item, iname, ipath))
          self.file_menu.DeleteItem(item)
          
          new_item = wx.MenuItem(self.file_menu, wx.NewId(), iname)
          # XXX-TODO
          # this is too advanced for now, but the first item in history should
          # be disabled, the trick is re-eneabling it as it becomes the second,
          # and so on 

          # new_item.Enable(False)
          self.file_menu.InsertItem(new_pos, new_item)
          self.Bind(wx.EVT_MENU, self.onOpenPastItem(iname, ipath), new_item)

      if str(path).strip():
        tpath=os.path.abspath(path)
      else:
        self.showError("INVALID PATH",
          "Invalid/Missing path for %s" % str(name))
        return

      if not str(name).strip():
        self.showError("INVALID NAME",
          "Invalid name for project: %s" % str(name))
        return
      if not os.path.exists(tpath):
        self.showError("INVALID PATH",
          "Missing or invalid path, it does not exist: %s" % str(tpath))
        return
      else:
        self.log.info("open project being called from menu")
        self.openProject(name, path)

    return onOpenPastItem_event

  def OnClose(self, evt):
    old_mode = self.log.mode 
    self.log.mode='file_only'
    self.log.info("Stopping %s at %s" % (_program_name,prettyNow())) 
    self.log.mode=old_mode
#    self.LogFrame.Close()
    self.CONFIG.save()

    evt.Skip()

  def OnResize(self, evt):
    evt.Skip() 
    lpw,lph = self.lp.GetSize()
    cpw,cph = self.cp.GetSize()
    rpw,rph = self.rp.GetSize()

    myw, myh = self.GetSize()
    new_width = myw-lpw-rpw
    print('-'*80)
    print("lpw:%s cpw:%s , rpw: %s" % (lpw, cpw, rpw))
    print("myw: %s || myh:%s" % (myw, myh))
    print('center panel widht should now be: %s' % new_width)
    self.cp.SetSize((new_width,cph))

    return evt

  def talkAboutEvent(self, evt, print_out=False):
    global log
    """
    wx.LogMessage("event dir: %s" % dir(evt))
    wx.LogMessage("event type: %s" % type(evt))
    wx.LogMessage("event repr: %s" % repr(evt))
    wx.LogMessage("event str: %s" % str(evt))
    wx.LogMessage("event IDa :%s" % str(evt.GetId()))
    """
    log.debug("event dir: %s" % str(dir(evt)) )
    log.debug("event dir: %s" % str(dir(evt)) )
    log.info("event type: %s" % type(evt))
    log.info1("event repr: %s" % repr(evt))
    log.info3("event str: %s" % str(evt))
    log.warn("event IDa :%s" % str(evt.GetId()))

    if print_out:
      print("="*80)
      print("event dir: %s" % dir(evt))
      print("event type: %s" % type(evt))
      print("event repr: %s" % repr(evt))
      print("event str: %s" % str(evt))
      print("event IDa :%s" % str(evt.GetId()))
      print("-"*80)
    return evt
    
  def onConvertAudioFiles(self, evt):
    evt.Skip()
    log.info1("now the verbosity is: %s" % self.log.verbosity)
    log.info2 (" and now the Effective level is : %s" % self.log.getEffectiveLevel())
    log.info1 (" and now the level is : %s" % self.log.level)
    return self.futureFeature()

  def onImportAudioFromFolder(self, evt):
    evt.Skip()
    return self.futureFeature()

  def importAudioFiles(self, paths):
    global log
    log.info('test')
    print("I will imnport paths", paths)

  def onImportAudioFiles(self, evt):
    paths = None

    # self.log.WriteText("CWD: %s\n" % os.getcwd())
    # Create the dialog. In this case the current directory is forced as the starting
    # directory for the dialog, and no default file name is forced. This can easilly
    # be changed in your program. This is an 'open' dialog, and allows multitple
    # file selections as well.
    #
    # Finally, if the directory is changed in the process of getting files, this
    # dialog is set up to change the current working directory to the path chosen.

    dlg = wx.FileDialog(
      self, message="Choose a file or files",
      defaultDir=self.default_audio_import_directory, 
      defaultFile="",
      wildcard=self.wildcard,
      style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR
    )

    # Show the dialog and retrieve the user response. If it is the OK response, 
    # process the data.
    if dlg.ShowModal() == wx.ID_OK:
      # This returns a Python list of files that were selected.
      paths = dlg.GetPaths()

      self.log.WriteText('You selected %d files:' % len(paths))

      for path in paths: self.log.debug('       %s\n' % path)

      self.importAudioFiles(paths)

      self.default_audio_import_directory = os.getcwd()

    # Compare this with the debug above; did we change working dirs?
#    self.log.WriteText("CWD: %s\n" % os.getcwd())

    # Destroy the dialog. Don't do this until you are done with it!
    # BAD things can happen otherwise!

    dlg.Destroy()

  def onToggleDebugFrame(self, event):
    global log
    if self.LogFrame.IsShown():
      self.LogFrame.Hide()
      if self.debug_window_item.IsChecked():
        self.CONFIG['show_debug_frame'] = False
        self.CONFIG.save()
        self.debug_window_item.Toggle()
    else:
      self.CONFIG['show_debug_frame'] = True
      self.CONFIG.save()
      self.LogFrame.Show()
      self.debug_window_item.Check()
  
  #----------------------------------------------------------------------
  def onNewProject(self, evt):
    return self.newProject()

  def onBrowse(self, event):
    """
    Opens file dialog to browse for music
    """

    dlg = wx.FileDialog(
      self, message="Choose a file",
      defaultDir=self.currentFolder, 
      defaultFile="",
      wildcard=self.wildcard,
      style=wx.OPEN | wx.CHANGE_DIR
      )
    if dlg.ShowModal() == wx.ID_OK:
      path = dlg.GetPath()
      self.currentFolder = os.path.dirname(path)
      self.loadMusic(path)
    dlg.Destroy()

  def onClose(self, evt):
    # what do we need to close down, write, save first?
    # :XXX-TODO
    self.LogFrame.Close()
    self.Close()

  # END EVENTS 
  ##################################################################

  def loadPane(self, obj, *args, **kwargs):
    x = obj(self, *args, **kwargs)
    x.Show(False)
    return x
      
  def hidePane(self, obj):
    obj.Show(False)
      
  def showPane(self, obj):
    obj.Show(true)
      
  def swapPanes(self, hideObj, showObj):
    class _(object):
      def __init__(self, hideObj, showObj):
        self.hideObj = hideObj
        self.showObj = showObj
      def __call__(self, o):
        hideObj.Show(False)
        showObj.Show(True)
            
    return _(hideObj,showObj)

  def loadProject(self):
    self.Project = Project(name=self.CONFIG.project_name,
      path=self.CONFIG.project_path)
    self.Project.load()

  def setTitle(self, project_name=''):
    self.SetTitle("Audio Reviewer - %s :: 2020-%s (c) " \
      "PyTis, LLC." % (project_name, str(datetime.now().year)) )


  def testLog(self):
    global log
    log.debug('debug CONFIG.verbosity: %s' % self.CONFIG.verbosity)
    log.info4('verbose +++')
    log.info3('verbose ++')
    log.info2('verbose +')
    log.info1('verbose')
    log.info('quiet')
    log.warn('CONFIG.verbosity: %s' % self.CONFIG.verbosity)
    log.error('This is an ERROR')
#    log.critical('CRITICAL ERROR')
  
  def setLogging(self):
    global log
    # XXX-TODO, add a feature to my logger to do this for me, print to log, or
    # our logging window only, but not actually printing to STDOUT

    self.log = log
    #self.log.mode='file_only'
    old_mode = self.log.mode 
    self.log.mode='screen_only'
    self.log.info("Starting %s at %s" % (_program_name, prettyNow()) ) 
    self.log.mode=old_mode
#    self.testLog()


    self.LogFrame = LogFrame(self, log, "Debug Log")
    return log


  def checkSetup(self):
    global log
    self.Project.name = self.CONFIG.project_name
    self.Project.path = os.path.abspath(self.CONFIG.project_path)

    if not os.path.isdir(self.Project.path) or not \
      os.path.exists(self.Project.path):
      self.showError("Missing Project", "The project to be loaded appears " \
        'to be missing, or something,... "%s" cannot be found.' %
        self.Project.path)
      self.newProject()

    elif self.Project.name is None:
      self.newProject()
    else:
      self.log.info("open project called from checkSetup")
      self.openProject(self.Project)
      self.setTitle(self.project_name)

  def loadConfig(self):
    show_debug_frame = mbool(self.CONFIG.get('show_debug_frame',''))
    log.debug("TYPE OF show_debug_frame: %s" % str( type(show_debug_frame)))
    log.debug("VALUE OF show_debug_frame: %s" % str( show_debug_frame))

    if show_debug_frame:
      self.LogFrame.Show()
      self.debug_window_item.Check()

    dblvl = self.CONFIG.get('debug_level', '')
    if dblvl == 'debug':
      self.LogFrame.debug_item.Check()
      self.log.verbosity = 5
      self.log.setLevel(10)

    elif dblvl == 'info4':
      self.LogFrame.info4_item.Check()
      self.log.verbosity = 4
      self.log.setLevel(20)

    elif dblvl == 'info3':
      self.LogFrame.info3_item.Check()
      self.log.verbosity = 3
      self.log.setLevel(22)

    elif dblvl == 'info2':
      self.LogFrame.info2_item.Check()
      self.log.verbosity = 2
      self.log.setLevel(24)

    elif dblvl == 'info1':
      self.LogFrame.info1_item.Check()
      self.log.verbosity = 1 
      self.log.setLevel(26)

    elif dblvl == 'warn':
      self.LogFrame.warn_item.Check()
      self.log.verbosity = 0
      self.log.setLevel(30)

    elif dblvl == 'error':
      self.LogFrame.error_item.Check()
      self.log.verbosity = 0
      self.log.setLevel(40)

    elif dblvl == 'critical':
      self.LogFrame.critical_item.Check()
      self.log.verbosity = 0
      self.log.setLevel(50)

      '''
    elif dblvl == 'info':
      self.LogFrame.info_item.Check()
      self.log.verbosity = 1 
      self.log.setLevel(28)
      '''

    else:
      self.LogFrame.info_item.Check()
      self.log.verbosity = 1 
      self.log.setLevel(28)


  def _on_options(self, event):
    """Event handler of the self._options_btn widget.

    This method is used when the options button is pressed to show
    the options window.

    """
    self._options_frame.load_all_options()
    self._options_frame.Show()


