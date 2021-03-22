
# Built In
from lib.log import MyLog

# Third Party
import wx
import wx.lib.scrolledpanel as scrolled

# My Stuff
from gui.panel import MyScrolledPanel

class LogPanel(MyScrolledPanel):
  bgcolor='#AcAcAc'

  def __init__(self, parent, frame, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):
    """Constructor"""
    
    self.frame = frame
    scrolled.ScrolledPanel.__init__(self, parent, 0, pos, size, style)

    self.setBackground()

#    mainSizer = wx.BoxSizer(wx.VERTICAL)
    self.log_text_ctrl = wx.TextCtrl(self, -1, size=(960, 540), pos=(10,10), 
      style = wx.TE_MULTILINE|wx.HSCROLL|wx.TE_PROCESS_ENTER)
#      style = wx.TE_READONLY|wx.TE_MULTILINE|wx.HSCROLL|wx.TE_PROCESS_ENTER)
#    self.log_text_ctrl.SetSize(self.log_text_ctrl.GetBestSize())

#    mainSizer.Add(self.log_text_ctrl, 0, wx.EXPAND)

    if wx.Platform == "__WXMAC__":
      self.log_text_ctrl.MacCheckSpelling(False)

    # But instead of the above we want to show how to use our own wx.Log class
    wx.Log_SetActiveTarget(MyLog(self.log_text_ctrl))

#    self.SetSizer(mainSizer)

    self.Bind(wx.EVT_SIZE, self.OnResize)
    self.log_text_ctrl.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
    self.Layout()

  def OnKeyDown(self, event):
    """
    This permitts the user to press "ENTER" to create log file seperators
    """
    if event.GetKeyCode() == wx.WXK_RETURN:
      if self.frame.CONFIG.get('debug_level','') == 'debug':
        self.frame.log.addSeperator()
      else:
        wx.LogMessage("")
        return event
    elif event.controlDown is True or \
         event.cmdDown is True or \
         event.altDown is True:
      event.Skip()
      return event
    else:
      if event.altDown is True:
        event.Skip()# this allow hotkeys to still work (CTRL+D) to hide window
        # OR Alt+L to open the "&Log Menu"
        return
    return False

  def OnResize(self, evt):
    w,h = self.GetSize()
    self.log_text_ctrl.SetSize( (w-20,h-20) )

