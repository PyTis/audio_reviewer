# Built In
import os, sys
import datetime
from subprocess import Popen
from distutils.dir_util import copy_tree

# Third Party
import wx
import wx.lib.scrolledpanel as scrolled
from wx.lib.buttons import GenBitmapButton
from wx.lib import masked

# My Stuff
from gui import images
from lib.project import acceptable_extensions
from lib.settings import CONFIG
from lib.soundfile import SoundFile
#from src.OwnerDLG import OwnerDLG
#from src.GetBinsDLG import GetBinsDLG
#from src.EditDLG import EditDLG
#from src.AboutDLG import AboutDLG

#from util import pickle_data
#from util.zweb import GotoURL
########################################################################
"""
pytis/pytis.py
lib/errors.py
lib/__init__.py [+]
lib/util.py
gui/panel.py
gui/main_frame.py    
"""
import  wx.lib.newevent
(OnChangeEvent, EVT_VALUE_CHANGED) = wx.lib.newevent.NewEvent()
class TextBox(wx.TextCtrl):
  old_value = u''

  def __init__(self,*args,**kwargs):
    wx.TextCtrl.__init__(self,*args,**kwargs)
    self.Bind(wx.EVT_SET_FOCUS, self.gotFocus)
    self.Bind(wx.EVT_KILL_FOCUS, self.lostFocus)

  def gotFocus(self, evt):
    evt.Skip()
    self.old_value = self.GetValue() 

  def lostFocus(self, evt):
    evt.Skip()
    if self.GetValue() != self.old_value:
      evt = OnChangeEvent(old_value=self.old_value, new_value=self.GetValue())
      wx.PostEvent(self, evt)

def HMStoMS(string):
  """
  string as HOUR:MINUTE:SECONDS to milliseconds
  """
  hours, minutes, seconds = (["0", "0"] + string.split(":"))[-3:]
  hours = int(hours)
  minutes = int(minutes)
  seconds = float(seconds)
  milliseconds = int(3600000 * hours + 60000 * minutes + 1000 * seconds)
  return milliseconds

def MStoHMS(ms):
  """
  return milliseconds to string as HOUR:MINUTE:SECONDS
  """
  if ms >= 86400000:
    raise Exception("File is too large to load, it's playtime is longer " \
      "than an entire day.")
    return
  else:
    return datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(
      ms/1000), "%H:%M:%S")


class Time24(object):
  _milliseconds = 0

  def set_milliseconds(self, ms):
    self._milliseconds = ms
  def get_milliseconds(self):
    return self._milliseconds
  milliseconds=property(get_milliseconds, set_milliseconds)

  def __init__(self, value=None):
    if ':' in value:
      self.milliseconds = self.HMS_to_miliseconds(value)
    else:
      self.milliseconds = value

  def HMS_to_miliseconds(self, string):
    return HMStoMS(string)

  def toHMS(self):
    return MStoHMS(self.milliseconds)

  def __str__(self):
    if self.milliseconds < 3600000:
      return datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(
        self.milliseconds/1000), "%M:%S")
    else:
      return MStoHMS(self.milliseconds)

class MyScrolledPanel(scrolled.ScrolledPanel):

  bgcolor="#E5E5E5"
  bgimage=None
  my_label=None

  def __init__(self, parent, frame, log, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):
    """Constructor"""
    self.log = log 
    self.frame = frame
    scrolled.ScrolledPanel.__init__(self, parent, 0, pos, size, style)


    self.setBackground()

  def setBackground(self):
    if self.bgimage:
      #png = getzpinBitmap()
      png = self.bgimage
      self.bg_bmp = png
      self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
    else:
      self.SetBackgroundColour(self.bgcolor)

  def onEraseBackground(self, evt):
    dc = evt.GetDC()
    if not dc:
      dc = wx.ClientDC(self)
      rect = self.GetUpdateRegion().GetBox()
      dc.SetClippingRect(rect)

  def SetOtherLabel(self, label=None):
    if not label:
      label = ''
    if not self.my_label:
      self.my_label = wx.StaticText(self, -1, label, (4, 4))
    else:
      # first clear it if there had been data before that was longer
      self.my_label.SetLabelText('')
      # now we will call refresh to ensure we wiped the screen
      self.my_label.Refresh()
      # now add new label
      self.my_label.SetLabelText(label)
      # and now call refresh to make sure it draws
      self.my_label.Refresh()

  def showError(self, err_name, err_msg, icon=wx.ICON_ERROR):
    dlg = wx.MessageDialog(self, err_msg,
       err_name, wx.OK | icon
       )
    dlg.ShowModal()
    dlg.Destroy()

  def onFutureFeature(self, evt):
    return self.futureFeature()

  def futureFeature(self, text='This feature is not yet implemented.'):
    return self.showError('Comming Soon,..', text, wx.ICON_INFORMATION)

class MyPanel(wx.Panel):

  bgcolor="#E5E5E5"
  bgimage=None
  my_label=None

  def __init__(self, parent, frame, log, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):
    """Constructor"""
    
    self.log = log 
    self.frame = frame
    wx.Panel.__init__(self, parent, 0, pos, size, style)


    self.setBackground()

  def setBackground(self):
    if self.bgimage:
      #png = getzpinBitmap()
      png = self.bgimage
      self.bg_bmp = png
      self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)
    else:
      self.SetBackgroundColour(self.bgcolor)

  def onEraseBackground(self, evt):
    dc = evt.GetDC()
    if not dc:
      dc = wx.ClientDC(self)
      rect = self.GetUpdateRegion().GetBox()
      dc.SetClippingRect(rect)

  def SetOtherLabel(self, label=None):
    if not label:
      label = ''
    if not self.my_label:
      self.my_label = wx.StaticText(self, -1, label, (4, 4))
    else:
      # first clear it if there had been data before that was longer
      self.my_label.SetLabelText('')
      # now we will call refresh to ensure we wiped the screen
      self.my_label.Refresh()
      # now add new label
      self.my_label.SetLabelText(label)
      # and now call refresh to make sure it draws
      self.my_label.Refresh()

  def showError(self, err_name, err_msg, icon=wx.ICON_ERROR):
    dlg = wx.MessageDialog(self, err_msg,
       err_name, wx.OK | icon
       )
    dlg.ShowModal()
    dlg.Destroy()

  def onFutureFeature(self, evt):
    wx.LogMessage("event dir:%s" % dir(evt))
    wx.LogMessage("event type:%s" % type(evt))
    wx.LogMessage("event repr:%s" % repr(evt))
    wx.LogMessage("event str:%s" % str(evt))
    return self.futureFeature()

  def futureFeature(self, text='This feature is not yet implemented.'):
    return self.showError('Comming Soon,..', text, wx.ICON_INFORMATION)



class CenterPane(MyPanel):
  bgcolor='#E5E5E5'
  _current_bookmark=None # str time H:M:S

  def set_current_bookmar(self, bm=None):
    if bm:
      self.removeBtn.Enable(True)
    else:
      self.removeBtn.Enable(False)

    self._current_bookmark = bm
  def get_current_bookmark(self):
    return self._current_bookmark
  current_bookmark=property(get_current_bookmark, set_current_bookmar)

  def __init__(self, parent, frame, log, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):
    """Constructor"""

    self.frame = frame
    MyPanel.__init__(self, parent, frame, log, size, pos, style)
    
    """ init__(self, Window parent, int id=-1, Bitmap bitmap=wxNullBitmap,
     |          Point pos=DefaultPosition, Size size=DefaultSize,
     |          long style=0, String name=StaticBitmapNameStr
    """
#    bpm = wx.StaticBitmap(self, -1, getSV100Bitmap(), (50,50), (44,44) )
#    bpm = wx.StaticBitmap(self, -1, getSVMuteBitmap(), (50,150), (48,48) )
#    bpm.Show(True)

    border_style = wx.BORDER_STATIC

    border_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    first_row_sizer = wx.BoxSizer(wx.HORIZONTAL)

    bookmark = wx.StaticText(self, -1, 'Bookmark Time:')
    spin2 = wx.SpinButton( self, -1, pos=(20, 40), size=(-1,23), style=wx.SP_VERTICAL )

    self.time24 = masked.TimeCtrl(self, -1, name="Bookmark", fmt24hr=True,
      spinButton = spin2)

    self.time24.SetSize( (66,-1) )
    self.time24.SetToolTipString('HOURS : MINUTES : SECONDS')
    self.time24.old_valu = '0:00:00'
    self.time24.Bind(wx.EVT_SET_FOCUS, self.gotTimeFocus)
    self.time24.Bind(wx.EVT_KILL_FOCUS, self.lostTimeFocus)
    self.time24.Bind(EVT_VALUE_CHANGED, self.onTime24Changed)

    spin2.Bind(wx.EVT_SPIN, self.onTime24ChangedViaSpin)

    first_row_sizer.Add(bookmark, 20, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,2)

    # XXX-FINDME

    first_row_sizer.Add(self.time24, 15, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 2)

    first_row_sizer.Add(spin2, 5, wx.EXPAND|wx.ALL, 2)

    first_row_sizer.Add((10,22), 0, wx.EXPAND|wx.ALL) # Spacer, 

    self.captureBtn = GenBitmapButton(self,
      bitmap=images.getClockBitmap(), name="Capture", style=border_style)
    self.captureBtn.SetToolTipString("Grab Timestamp")
    self.captureBtn.Bind(wx.EVT_BUTTON, self.onGrabTime)
    first_row_sizer.Add(self.captureBtn, 0, wx.EXPAND|wx.ALL) 

    self.insertBtn = GenBitmapButton(self,
      bitmap=images.getPlusBitmap(), name="Insert", style=border_style)
    self.insertBtn.SetToolTipString("Create Bookmark")
    self.insertBtn.Bind(wx.EVT_BUTTON, self.onInsertBookmark)
    first_row_sizer.Add(self.insertBtn, 0, wx.EXPAND|wx.ALL) 

    self.removeBtn = GenBitmapButton(self,
      bitmap=images.getMinusBitmap(), name="Remove", style=border_style)
    self.removeBtn.SetToolTipString("Remove Bookmark")
    self.removeBtn.Bind(wx.EVT_BUTTON, self.onRemoveBookmark)
    self.removeBtn.Enable(False)
    first_row_sizer.Add(self.removeBtn, 0, wx.EXPAND|wx.ALL) 

    self.jumpBtn = GenBitmapButton(self,
      bitmap=images.getJumpBitmap(), name="Jump", style=border_style)
    self.jumpBtn.SetToolTipString("Jump to Timestamp")
    self.jumpBtn.Bind(wx.EVT_BUTTON, self.onJumpToTimestamp)
    self.jumpBtn.Enable(False)
    first_row_sizer.Add(self.jumpBtn, 0, wx.EXPAND|wx.ALL) 

    '''
    self.moreButton = GenBitmapButton(self,
      bitmap=images.getMoreBitmap(), name="More", style=border_style)
    self.moreButton.SetToolTipString("Ask Question")
    self.moreButton.Bind(wx.EVT_BUTTON, self.onAskQuestion)
    first_row_sizer.Add(self.moreButton, 0, wx.EXPAND|wx.ALL) 
    '''

    '''
    rateButtonsGroup.Add(self.insertBtn, 0, wx.ALIGN_BOTTOM, 0)
    '''

    #insert_button = wx.Button(self, -1, "&INSERT", (20, 80)) 

    #first_row_sizer.Add(insert_button, 15, wx.EXPAND|wx.ALL) # Spacer, 

    first_row_sizer.Add((24,24), 15, wx.EXPAND|wx.ALL) # Spacer, 
    first_row_sizer.Add((24,24), 15, wx.EXPAND|wx.ALL) # Spacer, but later buttons
    first_row_sizer.Add((24,24), 15, wx.EXPAND|wx.ALL) # Spacer, but later buttons
    first_row_sizer.Add((24,24), 15, wx.EXPAND|wx.ALL) # Spacer, but later buttons

    sum_txt = wx.StaticText(self, -1, 'Summary:')
    summary_sizerr = wx.BoxSizer(wx.HORIZONTAL)
    summary_sizerr.Add(sum_txt, 20, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 2)
    self.summ_text_ctrl = TextBox(self, -1, size=(400, -1))#, pos=(20,80))
    self.summ_text_ctrl.Bind(EVT_VALUE_CHANGED, self.onSummChanged)
    self.summ_text_ctrl.Enable(False)
    summary_sizerr.Add(self.summ_text_ctrl, 80, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

    desc_txt = wx.StaticText(self, -1, 'Description:')
    self.desc_text_ctrl = TextBox(self, -1, size=(400, 440),# pos=(20,120), 
      style = wx.TE_MULTILINE|wx.HSCROLL)
    self.desc_text_ctrl.Enable(False)
    self.desc_text_ctrl.Bind(EVT_VALUE_CHANGED, self.onDescChanged)


#textCtrl->Connect(ID_TEXTCTRL1,wxEVT_KILL_FOCUS,(wxObjectEventFunction)&MyFrame::OnKillFocus);

    main_sizer.Add(first_row_sizer, 2, wx.EXPAND|wx.ALL|wx.ALIGN_BOTTOM |wx.ALIGN_LEFT)
    main_sizer.Add(summary_sizerr, 2, wx.ALIGN_TOP |wx.ALIGN_LEFT)
    main_sizer.Add(desc_txt, 2, wx.ALIGN_TOP |wx.ALIGN_LEFT)
    main_sizer.Add(self.desc_text_ctrl, 96, wx.ALIGN_TOP |wx.ALIGN_LEFT)
    border_sizer.Add(main_sizer, 100, wx.EXPAND|wx.ALL, 20) 
    self.SetSizer(border_sizer)
    self.Layout()
#    self.log_text_ctrl.SetSize(self.log_text_ctrl.GetBestSize())
    
  def saveBookmark(self):
    bookmark_time = self.time24.GetValue()
    bookmark = {'time' : bookmark_time,
                'summ' : self.summ_text_ctrl.GetValue(),
                'desc' : self.desc_text_ctrl.GetValue()
    }
    self.frame.Project.addBookmark(self.frame.current_file, bookmark)
    self.current_bookmark = bookmark_time

    self.frame.lp.loading_project = True
    self.frame.lp.rebuildTree()
    self.frame.lp.loading_project = False

  def gotTimeFocus(self, evt):
    evt.Skip()
    self.time24.old_value = self.time24.GetValue() 

  def lostTimeFocus(self, evt):
    evt.Skip()
    if self.time24.GetValue() != self.time24.old_value:
      evt = OnChangeEvent(old_value=self.time24.old_value,
        new_value=self.time24.GetValue())
      wx.PostEvent(self.time24, evt)


  def onAskQuestion(self, evt):
    ms = HMStoMS(self.time24.GetValue())
    if ms:
      self.saveBookmark()

  def onTime24ChangedViaSpin(self, evt):
    evt.Skip()

    if self.frame.current_file:
      bookmark_times = self.frame.Project.bookmarksFor(self.frame.current_file).keys()
    else:
      bookmark_times = []
    
    new_value = self.time24.GetValue()

    if new_value in bookmark_times:
      self.loadBookmark(new_value)
    else:
      if HMStoMS(new_value):
        self.summ_text_ctrl.Enable(True)

  
  def onTime24Changed(self, evt):
    if self.frame.current_file:
      bookmark_times = self.frame.Project.bookmarksFor(self.frame.current_file).keys()
    else:
      bookmark_times = []
    
    if evt.new_value in bookmark_times:
      self.loadBookmark(evt.new_value)
    else:

      if self.current_bookmark:
        # okay, this one is tricky, we changed the time on an existing
        # bookmark, we need to remove the old, and save the new.

        self.frame.Project.removeBookmark(self.frame.current_file,
          self.current_bookmark)
        
        self.saveBookmark()

      else:
        if HMStoMS(evt.new_value):
          self.summ_text_ctrl.Enable(True)

  def onSummChanged(self, evt):
    evt.Skip()
    if self.current_bookmark:
      self.saveBookmark()
    else:
      self.desc_text_ctrl.Enable(True)
  
  def onDescChanged(self, evt):
    evt.Skip()
    summary = self.summ_text_ctrl.GetValue().strip()
    description = self.desc_text_ctrl.GetValue()
    self.saveBookmark()

  def setTime(self, player_time_hms):
    self.time24.SetLabelText(player_time_hms)
    self.jumpBtn.Enable(True)

  def areYouSure(self, player_time_hms):
    dlg = wx.MessageDialog(self, 'Are you sure?  This bookmark already has ' \
      'a time set.  Pulling the current time will overwrite "%s" with "%s".' \
      % (self.time24.GetValue(), player_time_hms),
         'Overwrite?',
         wx.YES_NO | wx.NO_DEFAULT | wx.ICON_INFORMATION
    )

    result = dlg.ShowModal()
    dlg.Destroy()
    if result == wx.ID_YES:
      return True
    else:
      return False

  def grabTime(self):
    return Time24(self.frame.bp.currentPos.GetLabelText()).toHMS()

# self.removeBtn.Enable(True)

  def onJumpToTimestamp(self, evt):
    ms = Time24(self.time24.GetValue()).milliseconds
    self.frame.bp.Seek(ms)

  def loadBookmark(self, bookmark_time):
    self.current_bookmark = bookmark_time
    bookmarks = self.frame.Project.bookmarksFor(self.frame.current_file)
    bookmark = bookmarks[bookmark_time]
    self.time24.SetValue(bookmark_time)
    self.summ_text_ctrl.SetValue(bookmark['summ'])
    self.desc_text_ctrl.SetValue(bookmark['desc'])
    self.summ_text_ctrl.Enable(True)
    self.desc_text_ctrl.Enable(True)
    self.removeBtn.Enable(True)
    self.jumpBtn.Enable(True)

    self.frame.bp.Seek(Time24(bookmark_time).milliseconds)

  def onRemoveBookmark(self, evt):
    if self.current_bookmark:
      self.time24.SetValue('00:00:00')
      self.summ_text_ctrl.SetValue('')
      self.desc_text_ctrl.SetValue('')
      self.removeBtn.Enable(False)
      self.jumpBtn.Enable(False)
      self.frame.Project.removeBookmark(self.frame.current_file,
        self.current_bookmark)
      self.current_bookmark = None
      self.frame.lp.loading_project = True
      self.frame.lp.rebuildTree()
      self.frame.lp.loading_project = False

  def onGrabTime(self, evt):
    if not self.frame.current_file:
      return

    label_time = Time24(self.time24.GetValue())
    player_time_hms = self.grabTime()
    
    if self.frame.current_file:
      bookmark_times = self.frame.Project.bookmarksFor(self.frame.current_file).keys()
    else:
      bookmark_times = []

    if player_time_hms in bookmark_times:
      self.loadBookmark(player_time_hms)
      return

    if label_time.toHMS() == player_time_hms:
      self.summ_text_ctrl.Enable(True)
      evt.Skip()
      return

    if not label_time.milliseconds or self.areYouSure(player_time_hms):
      self.summ_text_ctrl.Enable(True)
      self.setTime(player_time_hms)

      if self.current_bookmark:

        self.frame.Project.removeBookmark(self.frame.current_file,
          self.current_bookmark)
        
        self.saveBookmark()

        self.frame.bp.Seek(Time24(self.current_bookmark).milliseconds)


  def onInsertBookmark(self, evt):
    self.current_bookmark = None
    self.time24.SetValue( '00:00:00' )
    self.onGrabTime(evt)
    self.summ_text_ctrl.SetValue('')
    self.desc_text_ctrl.SetValue('')
    self.summ_text_ctrl.Enable(True)
    self.desc_text_ctrl.Enable(False)

class RightPane(MyScrolledPanel):
  bgcolor='#AAAAAA'

