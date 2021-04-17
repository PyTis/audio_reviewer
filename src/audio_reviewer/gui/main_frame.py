#!/usr/bin/env python
# encoding=utf-8

# builtin
try:
  import sys
except KeyboardInterrupt as e:
  print("KeyboardInterrupt: %s" % str(repr(e)))
  print("Script terminated by Control-C")
  print("bye!")
  exit(1)

# builtin
from datetime import datetime
import time
import glob
import os
from pprint import pprint, pformat
import shutil
from ConfigParser import ConfigParser as CP

# Internal
from gui.log_frame import LogFrame
from gui.project_dlg import ProjectDialog
from gui.left_panel import LeftPane
from gui.media_panel import MediaPanel
from gui.panel import RightPane, CenterPane
from gui import import_dlg as MDD

from images import getMyIconIcon, getDarkPiSymbolIcon, getFolderMusicIcon
import images

from lib import mbool
from lib import settings
from lib.project import Project
from lib import config_file_path, config_dir
from lib.log import log
from lib.util import prettyNow
from lib.settings import _program_name
from lib.soundfile import SoundFile

from lib.project import acceptable_extensions

#
# Third-Party
import wx
from wx.lib.splitter import MultiSplitterWindow

class MyDirDlg(wx.DirDialog):
  
  def __init__(self,parent, message='', defaultPath=os.curdir,
    style=wx.DEFAULT, pos=wx.DefaultPosition, size=wx.DefaultSize):
    """
      parent (wx.Window) – Parent window.
      message (string) – Message to show on the dialog.
      defaultPath (string) – The default path, or the empty string.
      style (long) – The dialog style. See wx.DirDialog
      pos (wx.Point) – Dialog position. Ignored under Windows.
      size (wx.Size) – Dialog size. Ignored under Windows.
    """
    wx.DirDialog.__init__(self, parent, message, defaultPath, style, pos, size)

    self.testbutton = wx.Button(self, 20, "&SELECT", size=(20, 80),
      pos=wx.DefaultPosition) 
    w,h = self.GetSize()

    self.testbutton.SetPosition( (20, h-20) )
    self.testbutton.Show(True)
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.onUpdateBtn, self.testbutton)
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.onUpdateBtn, self)
    for child in self.GetChildren():
      child.Show(True)


  def OnInit(self):
    self.testbutton2 = wx.Button(self, 20, "&SELECT", size=(20, 80),
      pos=wx.DefaultPosition) 
    w,h = self.GetSize()

    self.testbutton2.SetPosition( (120, 0) )
    

  def onUpdateBtn(self, evt):
    self.testbutton.Update()



class MainFrame(wx.Frame):
  first_run = True
  _project = Project()
  _current_file = None

  wildcard = "Audio Files (*.midi, *.m4a, *.mp3, *.wav, *.wma)|" \
    "*.midi; *.m4a; *.mp3; *.wav; *.wma|" \
    "M4A (*.m4a)|*.m4a|" \
    "MP3 (*.mp3)|*.mp3|" \
    "WAV (*.wav)|*.wav" \
    "|WMA (*.wma)|*.wma"

  default_audio_import_directory = os.getcwd()

  # current_file
  def set_current_file(self, Obj=None):
    if Obj is None:
      self.disableFileMenus()
      self.cp.SetOtherLabel('')
    else:
      self._current_file=Obj
      self.showCurrentFile()
      self.bp.loadMusic(Obj.fpath)
      self.enableFileMenus()

  def get_current_file(self):
    return self._current_file
  current_file = property(get_current_file, set_current_file)

  def showCurrentFile(self):
    self.cp.SetOtherLabel("Folder: %s       File: %s" % \
      (self.current_file.folder, self.current_file.filename))

  def set_project(self, Obj):
    self._project=Obj
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
    self.disableFileMenus()

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


  def write(self):
    if self.Project.name and self.Project.path:
      self.Project.write()

  #----------------------------------------------------------------------
  def createMenu(self):
    """
    Creates a menu
    """
    menu_bar = wx.MenuBar()
    
    #----------------------------------------------------------------------
    self.file_menu = wx.Menu()
    self.open_file_menu_item = self.file_menu.Append(wx.NewId(), "&Open\tCTRL+O",
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
    self.actions_menu = wx.Menu()
    self.keep_menu_item = self.actions_menu.Append(wx.NewId(),
      'Move "to-&keep" folder\tCTRL+1', "Move current file to Keep Folder")
    self.Bind(wx.EVT_MENU, self.bp.onMoveToKeep, self.keep_menu_item)

    self.review_menu_item = self.actions_menu.Append(wx.NewId(),
      'Move "to-&review" folder\tCTRL+2', "Move current file to review Folder")
    self.Bind(wx.EVT_MENU, self.bp.onMoveToReview, self.review_menu_item)

    self.other_menu_item = self.actions_menu.Append(wx.NewId(),
      'Move to "&other" folder\tCTRL+3', "Move current file to Other Folder")
    self.Bind(wx.EVT_MENU, self.bp.onMoveToOther, self.other_menu_item)

    self.remove_menu_item = self.actions_menu.Append(wx.NewId(),
      'Move "to-remo&ve" folder\tCTRL+4', "Move current file to remove Folder")
    self.Bind(wx.EVT_MENU, self.bp.onMoveToRemove, self.remove_menu_item)


    menu_bar.Append(self.actions_menu, '&Actions')
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
      self.cp.current_bookmark = None
      self.cp.time24.SetValue('00:00:00')

      self.cp.summ_text_ctrl.SetValue('')
      self.cp.summ_text_ctrl.Enable(False)

      self.cp.desc_text_ctrl.SetValue('')
      self.cp.desc_text_ctrl.Enable(False)

      self.cp.removeBtn.Enable(False)
      self.cp.jumpBtn.Enable(False)

      self.bp.mediaPlayer.Stop()
      self.bp.disableFileButtons()
      self.bp.playPauseBtn.SetToggle(False)
      self.bp.playPauseBtn.Enable(False)
      self.bp.Seek(0)
      self.bp.currentPos.SetLabel('0:00')
      self.bp.currentLen.SetLabel('0:00')

      self.lp.loading_project = True
      self.log.info("open project running")
      self.setCurrentProject(name, path)
      self.Project.validateCoreFolders()
      self.lp.openProject()
      self.enableProjectMenus()
      self.resetLastProject()
      self.currentFolder = os.path.abspath(path)
      self.lp.loading_project = False
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

  def disableFileMenus(self):
    self.review_menu_item.Enable(False)
    self.keep_menu_item.Enable(False)
    self.remove_menu_item.Enable(False)
    self.other_menu_item.Enable(False)

  def enableProjectMenus(self):
    self.import_menu_item.Enable(True)
    self.import_menu_item2.Enable(True)
    self.settings_menu_item.Enable(True)
    self.export_menu_item.Enable(True)
    self.export_all__menu_item.Enable(True)

  def enableFileMenus(self):
    self.review_menu_item.Enable(True)
    self.keep_menu_item.Enable(True)
    self.remove_menu_item.Enable(True)
    self.other_menu_item.Enable(True)

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
    self.write()
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
    '''
    print('-'*80)
    print("lpw:%s cpw:%s , rpw: %s" % (lpw, cpw, rpw))
    print("myw: %s || myh:%s" % (myw, myh))
    print('center panel widht should now be: %s' % new_width)
    '''
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
    # XXX-FINDME
    print("MDD.__file__: %s" % MDD.__file__)

    dlg = MDD.MultiDirDialog(None, 
                             title="Chose a direcotry",
                             defaultPath=os.getcwd(),
                             agwStyle=\
                              MDD.DD_MULTIPLE |
                              MDD.DD_NEW_DIR_BUTTON |
                              MDD.DD_DIR_MUST_EXIST
                             )

    if dlg.ShowModal() != wx.ID_OK:
        log.debug("You Cancelled The Dialog!")
        dlg.Destroy()
        return

    if dlg.checkbox.IsChecked():
      recursive=True
    else:
      recursive=False

    paths = dlg.GetPaths()

    for indx, path in enumerate(paths):
      self.importAudioFromFolder(path, self.Project.review, recursive)

    dlg.Destroy()
    return

  def importAudioFromFolder(self, scan_dir, destination, recursive=False,
    level=0 ):

    """
    First look locally for overrides

  Extentions Found: dict_keys(['*.wma', '*.WMA', '*.mp3', '*.tmk', '*.csv',
  '*.DAT', '*.m4a', '*.txt'])

  Extentions Found: dict_keys(['*.wma', '*.WMA', '*.mp3', '*.tmk', '*.DAT',
  '*.m4a', '*.txt'])



    """
    global acceptable_extensions, log

    scandir = os.path.abspath(scan_dir)
    paths = list(glob.iglob(os.path.join(scandir,'**')))

    possible_import_count = len(paths)

    dlg = wx.ProgressDialog("Audio Import Progress",
                           "Calculating Import",
                           maximum = possible_import_count,
                           parent=self,
                           style = 0
                            | wx.PD_APP_MODAL
                            | wx.PD_CAN_ABORT
                            #| wx.PD_CAN_SKIP
                            | wx.PD_ELAPSED_TIME
                            | wx.PD_ESTIMATED_TIME
                            | wx.PD_REMAINING_TIME
                            #| wx.PD_AUTO_HIDE
                            )
    print('value of recursive: %s type: %s'  % (repr(recursive),
      type(recursive)))
    self._importAudioFromFolder(scan_dir, destination, bool(recursive), 0, dlg)

    if level == 0:
      dlg.Destroy()
      self.lp.reloadTree()

  # XXX-FINDME
  def _importAudioFromFolder(self, scan_dir, destination, recursive, level, dlg):

    print('value of ccrecursive: %s type: %s'  % (repr(recursive),
      type(recursive)))

    scandir = os.path.abspath(scan_dir)
    store = os.path.abspath(destination)

    keepGoing = True
    moved_filecount = 0
    audio_files=[]
    md5_sums = {}

    paths = list(glob.iglob(os.path.join(scandir,'**')))

    possible_import_count = len(paths)

    if level == 0:
      dlg.maximum = possible_import_count
      dlg.range = possible_import_count
#      dlg.SetRange()
    else:
      dlg.maximum = dlg.maximum + possible_import_count
      dlg.range = dlg.range + possible_import_count


    for count, fpath in enumerate(paths):

      if not keepGoing:
        break;


      if os.path.isdir(fpath):
        # This is a folder
        if recursive is True:
          print("would run self._importAudioFromFolder(store, fpath, " \
          "recursive, level=level+1) where fpath is: %s and level is: " \
          "%s" % (str(fpath), str(level+1)))
          self._importAudioFromFolder(scan_dir, destination, recursive,
            (level+1), dlg)

      if os.path.isfile(fpath):

        (keepGoing, skip) = dlg.Update(count, "importing %s" %
          os.path.basename(fpath))

        log.debug("fpath found: %s" % fpath)
        # This is a file
        source = SoundFile(fpath)
        
        if source.ext.lower() in acceptable_extensions:
          # This IS a SOUND File
          audio_files.append(fpath)
          log.info("I am an exceptable file extension: %s" % source.extension)
          if source.md5 not in md5_sums.keys():
            # IT hasn't been cached yet
            md5_sums[source.md5] = source
            target = SoundFile(os.path.abspath(os.path.join(store, \
              source.filename) )) # basename with lowercase extension

            if os.path.exists(target.fpath):
              # The target exists by FILENAME
              if target.md5 == source.md5:
                # The target matches by MD5 Sum also
                log.info("Already copied/moved here, skip... (%s)" % source.fpath) 
              else:
                # The target exists by Filename, but has different contents,
                # THEREFORE we should keep this file, but with a new filename.

                shutil.copy(source.fpath, safe_fname(target.fpath))
                if not os.path.isfile(target.fpath) or \
                   not os.path.exists(target.fpath):
                  log.info("COPYING FAILED.")
                  log.info3("A1: shutil.copy(%s, safe_fname(%s))" % (source.fpath,
                    target.fpath))
                else:
                  log.info("COPIED: %s" % target.fpath)
                  moved_filecount+=1

            else:
              # This target does not exist by filename
              shutil.copy(source.fpath, target.fpath)
              if not os.path.isfile(target.fpath) or \
                 not os.path.exists(target.fpath):
                log.info("COPYING FAILED.")
                log.info3("B2: shutil.copy(%s, %s)" % (source.fpath, target.fpath))
              else:
                log.info("COPIED: %s" % target.fpath)
                moved_filecount+=1

          else:
            # This MD5 sum has already been cached (we have already came across a
            # file with the same contents).
            if source.base_name == md5_sums[source.md5].base_name:
              # The file with the same contents also has the same name, it just
              # is in a different folder, it must be a copy/paste thing.  Skip
              # it.

              pass
            else:
              # The contents already exist, but with a different filename.  Since
              # we already have a duplicate, we will skip moving.
              log.info("X"*80)
              log.info("THIS MD5 ALREADY EXITS / BUT WITH A DIFFERENT FILENAME.")
              log.info("already cached: %s" % md5_sums[source.md5].filepath)
              log.info("now looking at duplicate located at: %s" % source.filepath)
              log.info("")
        else:
          # Not a VALID file extension
          log.critical("I am NOT an exceptable file extension, " \
            "filename: %s" % source.ext)
          #pass

      
    log.info("%s files scanned" % len(audio_files))
    log.info("%s files moved" % moved_filecount)


  def importAudioFiles(self, paths):
    global acceptable_extensions, log

    # XXX-FINDME

    possible_import_count = len(paths)

    dlg = wx.ProgressDialog("Audio Import Progress",
                           "Calculating Import",
                           maximum = possible_import_count,
                           parent=self,
                           style = 0
                            | wx.PD_APP_MODAL
                            | wx.PD_CAN_ABORT
                            #| wx.PD_CAN_SKIP
                            | wx.PD_ELAPSED_TIME
                            | wx.PD_ESTIMATED_TIME
                            | wx.PD_REMAINING_TIME
                            #| wx.PD_AUTO_HIDE
                            )
    keepGoing = True
    moved_filecount = 0
    audio_files=[]
    md5_sums = {}

    
    for count, fpath in enumerate(paths):

      if not keepGoing:
        break;

      if os.path.isdir(fpath):
        # This is a folder
        pass

      (keepGoing, skip) = dlg.Update(count, "importing %s" %
        os.path.basename(fpath))

      if os.path.isfile(fpath):
        # This is a file
        source = SoundFile(fpath)
        
        if source.ext.lower() in acceptable_extensions:
          # This IS a SOUND File
          audio_files.append(fpath)

          if source.md5 not in md5_sums.keys():
            # IT hasn't been cached yet
            md5_sums[source.md5] = source

            # source.filename = basename with lowercase extension
            target = SoundFile(os.path.abspath(os.path.join(
              self.Project.review, source.filename) ))

            if os.path.exists(target.fpath):
              # The target exists by FILENAME
              if target.md5 == source.md5:
                # The target matches by MD5 Sum also
                print("Already copied/moved here, skip... (%s)" % source.fpath) 
              else:
                # The target exists by Filename, but has different contents,
                # THEREFORE we should keep this file, but with a new filename.

                shutil.copy(source.fpath, safe_fname(target.fpath))
                if not os.path.isfile(target.fpath) or not \
                  os.path.exists(target.fpath):
                  print("COPYING FAILED.")
                  print("A1: shutil.copy(%s, safe_fname(%s))" % (source.fpath,
                    target.fpath))
                else:
                  print("COPIED: %s" % target.fpath)
                  moved_filecount+=1

            else:
              # This target does not exist by filename
              shutil.copy(source.fpath, target.fpath)
              # if not result: # this only worked in python3, won't work in
              # python2.7

              if not os.path.isfile(target.fpath) or not \
                os.path.exists(target.fpath):
                print("COPYING FAILED.")
                print("B2: shutil.copy(%s, %s)" % (source.fpath, target.fpath))
              else:
                print("COPIED: %s" % target.fpath)
                moved_filecount+=1

          else:
            # This MD5 sum has already been cached (we have already came across a
            # file with the same contents).
            if source.base_name == md5_sums[source.md5].base_name:
              # The file with the same contents also has the same name, it just
              # is in a different folder, it must be a copy/paste thing.  Skip
              # it.

              #print("THIS MD5 ALREADY EXITS.")
              #print("already cached: %s" % md5_sums[source.md5].filepath)
              #print("now looking at duplicate located at: %s" % source.filepath)
              # print("")
              pass
            else:
              # The contents already exist, but with a different filename.  Since
              # we already have a duplicate, we will skip moving.
              print("X"*80)
              print("THIS MD5 ALREADY EXITS / BUT WITH A DIFFERENT FILENAME.")
              print("already cached: %s" % md5_sums[source.md5].filepath)
              print("now looking at duplicate located at: %s" % source.filepath)
              print("")
        else:
          # Not a VALID file extension
          pass

    dlg.Destroy()

    self.lp.reloadTree()


  def onImportAudioFiles(self, evt):

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
      style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR | wx.FILE_MUST_EXIST
    )
    dlg.SetIcon(images.getCatalogsIcon())

    if dlg.ShowModal() == wx.ID_OK:
      paths = dlg.GetPaths()
      for path in paths: self.log.debug('       %s\n' % path)

      self.importAudioFiles(paths)
      self.default_audio_import_directory = os.getcwd()

    dlg.Destroy()

    # XXX-TODO

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
    print('in onBrowse')
    dlg = wx.FileDialog(
      self, message="Choose a file",
      defaultDir=self.currentFolder, 
      defaultFile="",
      wildcard=self.wildcard,
      style=wx.OPEN | wx.CHANGE_DIR
      )

    if dlg.ShowModal() == wx.ID_OK:
      print('ok clicked')
      path = dlg.GetPath()
      self.currentFolder = os.path.dirname(path)
      print('path found: %s' % path)
      self.current_file = SoundFile(path)
      print('current file is: %s' % self.current_file.fpath)
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


