#!/usr/bin/env python
# encoding=utf-8

import os, sys
from datetime import datetime

from ConfigParser import ConfigParser as CP

from lib import mbool
from lib import settings
from lib.project import Project
from images import getDarkPiSymbolIcon, getBevelGearIcon
from panel import MediaPanel, LogPanel
from panel import LeftPane, RightPane, CenterPane, BottomPane
from lib import config_file_path, config_dir
from lib.log import set_logging
from lib.util import prettyNow
from lib.settings import _program_name

import wx
from wx.lib.splitter import MultiSplitterWindow
import wx.aui

class LogFrame(wx.Frame):

  def __init__(self, parent, title, pos=(-1,-1), size=(1000,600),
    style=wx.DEFAULT_FRAME_STYLE):
#    style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.DOUBLE_BORDER):
    global log
    self.log = log
    wx.Frame.__init__(self, parent, -1, title, pos, size, style)
    self.parent = parent

    self.SetBackgroundColour('#FFFFFF')

    self.LogPanel=LogPanel(parent=self, frame=self, size=(1000, 600),
      style=style)
    self.log.info("Starting %s at %s" % (_program_name, prettyNow()) ) 

    self.createMenu()

  def createMenu(self):
    menu_bar = wx.MenuBar()
    
    #----------------------------------------------------------------------
    options_menu = wx.Menu()
    
    self.debugid = wx.NewId()
    self.infoid0 = wx.NewId()
    self.infoid1 = wx.NewId()
    self.infoid2 = wx.NewId()
    self.infoid3 = wx.NewId()
    self.infoid4 = wx.NewId()
    self.warn_id = wx.NewId()
    self.erro_id = wx.NewId()
    self.crit_id = wx.NewId()

    self.debug_item   =options_menu.Append(self.debugid,"&Debug\tCTRL+0",
      "Show more verbosity (include debug messages).", wx.ITEM_RADIO) #
    self.info4_item   =options_menu.Append(self.infoid4,"&Noisy (+++)\tCTRL+1",
      "Info 4 >=", wx.ITEM_RADIO) #
    self.info3_item   =options_menu.Append(self.infoid3,"Verbose (&++)\tCTRL+2",
      "Info 3 >=", wx.ITEM_RADIO) #
    self.info2_item   =options_menu.Append(self.infoid2,"&More Verbose (+)\tCTRL+3",
      "Info 2 >=", wx.ITEM_RADIO) #
    self.info1_item   =options_menu.Append(self.infoid1,"&Verbose\tCTRL+4", 
      "Info 1 >=", wx.ITEM_RADIO) #
    self.info_item    =options_menu.Append(self.infoid0,"&Quiet\tCTRL+5", 
      "Info >=", wx.ITEM_RADIO) #
    self.warn_item    =options_menu.Append(self.warn_id,"&Warning\tCTRL+6",
      "Warning >=", wx.ITEM_RADIO) #
    self.error_item   =options_menu.Append(self.erro_id,"&Error\tCTRL+7", 
      "Error >=", wx.ITEM_RADIO) #
    self.critical_item=options_menu.Append(self.crit_id,"&Critical && Failure\tCTRL+8",
      "Critical \& Failure >=", wx.ITEM_RADIO) #

    options_menu.AppendSeparator()

    """
    self.show_timestamp_item = options_menu.Append(wx.NewId(),
      "&Timestamps",
      "Show / Hide Timestamps", wx.ITEM_CHECK) #

    options_menu.AppendSeparator()
    """

    self.close_item=options_menu.Append(wx.NewId(),
      "&Close/Hide Window\tCTRL+D", "Hide Debugging Window") #

    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.debug_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.info4_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.info3_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.info2_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.info1_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.info_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.warn_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.error_item)
    self.Bind(wx.EVT_MENU, self.onToggleDebug, self.critical_item)

    #self.Bind(wx.EVT_MENU, self.onToggleTimestamp, self.show_timestamp_item)

    self.Bind(wx.EVT_MENU, self.OnHideNow, self.close_item)

    self.Bind(wx.EVT_CLOSE, self.OnClose, self)

# init__(self, Menu parentMenu=None, int id=ID_SEPARATOR, String text=EmptyString, |          String help=EmptyString, int kind=ITEM_NORMAL, |          Menu subMenu=None) -> MenuItem

    dump_menu = wx.Menu()

    self.dump_item = dump_menu.Append(wx.NewId(), '&Print "%s" to screen.' \
      % os.path.basename(config_file_path()), "Dump Config")

    self.Bind(wx.EVT_MENU, self.OnPrintConfig, self.dump_item)

#    self.debug_item.Toggle()

    menu_bar.Append(options_menu, '&Log Level') #, "Debbugin / Verbosity Level (-d -vvvv)")

    menu_bar.Append(dump_menu, '&Options') #, "Debbugin / Verbosity Level (-d -vvvv)")

#    self.Bind(wx.EVT_MENU, self.onFutureFeature, show_stuff)

    #----------------------------------------------------------------------
    self.SetMenuBar(menu_bar)

  ##################################################################
  def OnPrintConfig(self, evt):
    global log
    evt.Skip()

    # wx.LogMessage('PRINTING CONFIG FILE "%s" to LOG' % config_file_path())
    wx.LogMessage("")
    log.addSeperator('PRINTING CONFIG FILE "%s" to LOG' % config_file_path())

    log.addSeperator()
    h = open(config_file_path(), 'r')
    for line in h.readlines(-1):
      log.addSeperator(str(line).strip())
    h.close()
    log.addSeperator()

  def futureFeature(self, text='This feature is not yet implemented.'):
    global log
    log.info1('test', 'tst2')
    log.warn('test WARN test', 'tsWARNINGt2')
    return self.showError('Comming Soon,..', text, wx.ICON_INFORMATION)

  def onToggleDebug(self, evt):
    """
      3 points
      logging
      CONFIG
      checkbox save in config ?
      tell logging

      0 : 'ALL',
      10 : 'debug',
      20 : 'info',
      30 : 'warn',
      40 : 'error',
      50 : 'critcial'
    """
    global log

    id = evt.GetId()
    if id == self.debugid:
      self.CONFIG['debug_level'] = 'debug'
      self.CONFIG.save()
      self.log.verbosity = 5
      self.log.setLevel(10)

    elif id == self.infoid4:
      self.CONFIG['debug_level'] = 'info4'
      self.CONFIG.save()
      self.log.verbosity = 4
      self.log.setLevel(20)

    elif id == self.infoid3:
      self.CONFIG['debug_level'] = 'info3'
      self.CONFIG.save()
      self.log.verbosity = 3
      self.log.setLevel(22)

    elif id == self.infoid2:
      self.CONFIG['debug_level'] = 'info2'
      self.CONFIG.save()
      self.log.verbosity = 2
      self.log.setLevel(24)

    elif id == self.infoid1:
      self.CONFIG['debug_level'] = 'info1'
      self.CONFIG.save()
      self.log.verbosity = 1 
      self.log.setLevel(26)

    elif id == self.infoid0:
      self.CONFIG['debug_level'] = 'info'
      self.CONFIG.save()
      self.log.verbosity = 1 
      self.log.setLevel(28)

    elif id == self.warn_id:
      self.CONFIG['debug_level'] = 'warn'
      self.CONFIG.save()
      self.log.verbosity = 0
      self.log.setLevel(30)

    elif id == self.erro_id:
      self.CONFIG['debug_level'] = 'error'
      self.CONFIG.save()
      self.log.verbosity = 0
      self.log.setLevel(40)

    elif id == self.crit_id:
      self.CONFIG['debug_level'] = 'critical'
      self.CONFIG.save()
      self.log.verbosity = 0
      self.log.setLevel(50)

    log.info("self.CONFIG['debug_level'] %s" % self.CONFIG['debug_level'])
  
  """
  def onToggleTimestamp(self, evt):
    global log

    if self.show_timestamp_item.IsChecked():
      log.use_timestamps = self.CONFIG['logging__show_timestamps'] = True
      self.CONFIG.save()
    else:
      log.use_timestamps = self.CONFIG['logging__show_timestamps'] = False
      self.CONFIG.save()
  """

  def OnHideNow(self, evt):
#    print("CALLED")
#    wx.LogMessage("\n")
#    self.parent.onToggleDebugFrame(evt)
    return self.OnClose(evt)

  def OnClose(self, evt):
    wx.LogMessage("\n")
    self.parent.onToggleDebugFrame(evt)

class MainFrame(wx.Frame):
  first_run = True
  _project = Project()

  def OnClose(self, evt):
    self.log.info("Stopping %s at %s" % (_program_name,prettyNow())) 
#    self.LogFrame.Close()
    self.CONFIG.save()

    evt.Skip()
  
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
    return self.Project.get('pname', None)

  @property
  def project_path(self):
    return self.Project.get('path', None)

  def __init__(self, parent, title, pos=(-1,-1), size=(1000,600),
    style=wx.DEFAULT_FRAME_STYLE):
#    style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.DOUBLE_BORDER):
    global log

    wx.Frame.__init__(self, parent, -1, title, pos, size, style)
    self.parent = parent

    self.Bind(wx.EVT_CLOSE, self.OnClose, self)

    log = self.setLogging()

#    self.LogFrame.Show(True)
#    self._options_frame = OptionsFrame(self)

    self.SetBackgroundColour('#FFFFFF')
#    self.Maximize()

    try:
      self.SetIcon(getDarkPiSymbolIcon())
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
    self.cp.SetOtherLabel("Text Editor")
    self.cp.SetMinSize(self.cp.GetBestSize())

    self.rp = RightPane(self.vsplitter, self, log, size=(180, 450), style=sty)
    self.rp.Show(True)
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
    '''
    self.Bind(wx.EVT_SIZE, self.onFutureFeature, self)
#    self.Bind(wx.EVT_SIZE, self.onFutureFeature, self)
    '''
  
  #----------------------------------------------------------------------
  def createMenu(self):
    """
    Creates a menu
    """
    menu_bar = wx.MenuBar()
    
    #----------------------------------------------------------------------
    file_menu = wx.Menu()
    open_file_menu_item = file_menu.Append(wx.NewId(), "&Open", "Open audio File")
    self.Bind(wx.EVT_MENU, self.onBrowse, open_file_menu_item)

    new_project_menu_item = file_menu.Append(wx.NewId(), "&New Project\tCTRL+N",
      "Start a Project")
    self.Bind(wx.EVT_MENU, self.onNewProject, new_project_menu_item)

    import_menu_item = file_menu.Append(wx.NewId(), "&Import Audio Files",
      "Import Audio Files")
    self.Bind(wx.EVT_MENU, self.onFutureFeature, import_menu_item)

    settings_menu_item = file_menu.Append(wx.NewId(), "Project &Settings",
      "Project Settings")
    self.Bind(wx.EVT_MENU, self._on_options, settings_menu_item)

    export_menu_item = file_menu.Append(wx.NewId(), "&Export",
      "Export one thing")
    self.Bind(wx.EVT_MENU, self.onFutureFeature, export_menu_item)

    export_all__menu_item = file_menu.Append(wx.NewId(), "&Export Full Report",
      "Export Full Report Wizzard")
    self.Bind(wx.EVT_MENU, self.onFutureFeature, export_all__menu_item)

    file_menu.AppendSeparator()
    
    for prj in self.CONFIG.get('last_projects', []):
      name,path=prj.split('::')
      menu_item = file_menu.Append(wx.NewId(), name, path)
      self.Bind(wx.EVT_MENU, self.onOpenPastItem(name, path), menu_item)

    file_menu.AppendSeparator()
    exit__menu_item = file_menu.Append(wx.NewId(), "E&xit\tCTRL+Q",
      "Exit Program")

    self.Bind(wx.EVT_MENU, self.onClose, exit__menu_item)

    menu_bar.Append(file_menu, '&File')
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

    #print(dir(self.debug_window_item))
    #----------------------------------------------------------------------

    self.SetMenuBar(menu_bar)

    #debug_window_item.Toggle()
  ##################################################################
  # New Project

  def newProject(self):
    # first get the name
    dlg = ProjectDialog(self)
    dlg.ShowModal()
    return
    self.project_name = self.getProjectName()
    self.project_path = self.onSelectDir(None)
    return
    # now get a path

  ##################################################################
  # Actions

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

  def openProject(self, name, path):
    print('open past item')
    print('name, ', name)
    print('path, ', path)
    test = '%s::%s' % (name, path)
    p = Project(*test.split('::') )
    print(p)
    print(p.name)

  ##################################################################
  # Events 

  def onOpenPastItem(self, name, path):
    def _onOpenPastItem(evt):
      self.openProject(name, path)
    return _onOpenPastItem

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

  def onFutureFeature(self, evt):
    evt.Skip()
    wx.LogMessage("event dir:%s" % dir(evt))
    wx.LogMessage("event type:%s" % type(evt))
    wx.LogMessage("event repr:%s" % repr(evt))
    wx.LogMessage("event str:%s" % str(evt))
    return self.futureFeature()

  def futureFeature(self, text='This feature is not yet implemented.'):
    global log
    log.info1('test', 'tst2')
    log.warn('test WARN test')
    return self.showError('Comming Soon,..', text, wx.ICON_INFORMATION)

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
    wildcard = "Audio Files (*.midi, *.mp3, *.wav, *.wma)|*.midi; *.mp3; *.wav; *.wma|" \
      "MP3 (*.mp3)|*.mp3|WAV (*.wav)|*.wav|WMA (*.wma)|*.wma"

    dlg = wx.FileDialog(
      self, message="Choose a file",
      defaultDir=self.currentFolder, 
      defaultFile="",
      wildcard=wildcard,
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

  def loadProject(self):
    self.Project = Project(pname=self.CONFIG.project_name,
      path=self.CONFIG.project_path)

    self.Project.load()

  def setTitle(self, project_name=''):
    self.SetTitle("Audio Reviewer - %s :: 2020-%s (c) " \
      "PyTis, LLC." % (project_name, str(datetime.now().year)) )

  def onImportAudio(self, evt):
    pass

  def setLogging(self):
    global log
    self.debug  = self.CONFIG.get('debug', False)
    log = set_logging(_program_name, self.debug)
    self.log = log
    self.LogFrame = LogFrame(self, "Debug Log")
    self.LogFrame.CONFIG=self.CONFIG
    return log


  def checkSetup(self):
    self.Project.name = self.CONFIG.project_name
    self.Project.path = os.path.abspath(self.CONFIG.project_path)


    if not os.path.isdir(self.Project.path) or not \
      os.path.exists(self.Project.path):
      self.showError("Missing Project", "The project to be loaded appears " \
        'to be missing, or something,... "%s" cannot be found.' %
        self.Project.path)
      self.newProject()

    elif self.Project.get('name', None) is None:
      self.newProject()
    
    self.setTitle(self.project_name)
    show_debug_frame = mbool(self.CONFIG.get('show_debug_frame',''))
    print("TYPE OF show_debug_frame: %s" % str( type(show_debug_frame)))
    print("VALUE OF show_debug_frame: %s" % str( show_debug_frame))

    if show_debug_frame:
      self.LogFrame.Show()
      self.debug_window_item.Check()

    if mbool(self.CONFIG.get('debug','')):
      self.LogFrame.debug_item.Toggle()
      self.log.verbosity = 5
      self.log.setLevel(10)
    else:
      self.log.verbosity = 1
      self.log.setLevel(30)
    
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


class ProjectDialog(wx.Dialog):
  
  def __init__(self, parent, title='New Project Wizard', pos=(-1,-1), size=(700,400),
    style=wx.DEFAULT_FRAME_STYLE|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER):
#    style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.DOUBLE_BORDER):

    self.frame = parent
    wx.Dialog.__init__(self, parent, -1, title, pos, size, style)
    self.SetBackgroundColour('#E5E5E5')

    self.CONFIG = self.frame.CONFIG

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

    print('onSave called, self.project_nameTC.GetValue() is: %s' % \
      name)

    self.CONFIG.project_name = name
    print('now in CONFIG, value is: %s' % self.CONFIG.project_name)
    self.CONFIG.project_path = path

    print('passsing into Project __init__ :%s' % self.CONFIG.project_name)

    project = Project(pname=self.CONFIG.project_name,
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


