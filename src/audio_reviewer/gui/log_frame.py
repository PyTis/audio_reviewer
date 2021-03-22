
import os, sys

from gui.log_panel import LogPanel
from lib import config_file_path, config_dir
from lib.util import prettyNow
from lib.settings import CONFIG

import wx

class LogFrame(wx.Frame):

  def __init__(self, parent, log, title, pos=(-1,-1), size=(1000,600),
    style=wx.DEFAULT_FRAME_STYLE):
#    style=wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.DOUBLE_BORDER):
    self.log = log
    wx.Frame.__init__(self, parent, -1, title, pos, size, style)
    self.parent = parent

    self.SetBackgroundColour('#FFFFFF')

    self.LogPanel=LogPanel(parent=self, frame=self, size=(1000, 600),
      style=style)

    self.createMenu()

  def createMenu(self):
    global log
    log = self.log
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

    self.mode_toscreen_id = wx.NewId()
    self.mode_tolog_id = wx.NewId()
    self.mode_both_id = wx.NewId()


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

    self.mode_toscreen_item   =options_menu.Append(self.mode_toscreen_id, 
      "&Screen Only", "Log to Screen Only", wx.ITEM_RADIO) #

    self.mode_tolog_item   =options_menu.Append(self.mode_tolog_id, 
      "&Print Only", "Print Log Only", wx.ITEM_RADIO) #
    self.mode_both_item    =options_menu.Append(self.mode_both_id,"&Both", 
      "Display on Both", wx.ITEM_RADIO) #

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

    log.debug('debug CONFIG.verbosity: %s' % CONFIG.verbosity)

    log.info4('verbose +++')
    log.info3('verbose ++')
    log.info2('verbose +')
    log.info1('verbose')

    log.info('quiet')
    log.warn('a warning')
    log.error('an error ')
    log.critical('boom')

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
      CONFIG['debug_level'] = 'debug'
      CONFIG['verbosity'] = log.verbosity = 5

      CONFIG.save()
      log.setLevel(10)

    elif id == self.infoid4:
      CONFIG['debug_level'] = 'info4'
      CONFIG['verbosity'] = log.verbosity = 4
      CONFIG.save()
      log.setLevel(12)

    elif id == self.infoid3:
      CONFIG['debug_level'] = 'info3'
      CONFIG['verbosity'] = log.verbosity = 3
      CONFIG.save()
      log.setLevel(14)

    elif id == self.infoid2:
      CONFIG['debug_level'] = 'info2'
      CONFIG['verbosity'] = log.verbosity = 2
      CONFIG.save()
      log.setLevel(16)

    elif id == self.infoid1:
      CONFIG['debug_level'] = 'info1'
      CONFIG['verbosity'] = log.verbosity = 1 
      CONFIG.save()
      log.setLevel(18)

    elif id == self.infoid0: # QUIET
      CONFIG['debug_level'] = 'info'
      CONFIG['verbosity'] = log.verbosity = 1 
      CONFIG.save()
      log.setLevel(20)

    elif id == self.warn_id:
      CONFIG['debug_level'] = 'warn'
      CONFIG['verbosity'] = log.verbosity = 0
      CONFIG.save()
      log.setLevel(30)

    elif id == self.erro_id:
      CONFIG['debug_level'] = 'error'
      CONFIG['verbosity'] = log.verbosity = 0
      CONFIG.save()
      log.setLevel(40)

    elif id == self.crit_id:
      CONFIG['debug_level'] = 'critical'
      CONFIG['verbosity'] = log.verbosity = 0
      CONFIG.save()
      log.setLevel(50)

    log.info("CONFIG['debug_level'] %s" % CONFIG['debug_level'])
    log.info("CONFIG['verbosity'] %s" % CONFIG['verbosity'])
  
  """
  def onToggleTimestamp(self, evt):
    global log

    if self.show_timestamp_item.IsChecked():
      log.use_timestamps = CONFIG['logging__show_timestamps'] = True
      CONFIG.save()
    else:
      log.use_timestamps = CONFIG['logging__show_timestamps'] = False
      CONFIG.save()
  """

  def OnHideNow(self, evt):
#    self.parent.onToggleDebugFrame(evt)
    return self.OnClose(evt)

  def OnClose(self, evt):
    wx.LogMessage("\n")
    self.parent.onToggleDebugFrame(evt)

