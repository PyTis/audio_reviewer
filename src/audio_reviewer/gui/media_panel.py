import os
import datetime
import time
# Third Party
import wx.media as WM
import wx

import wx.lib.buttons  as  buttons
from wx.lib.buttons import GenBitmapButton, GenBitmapToggleButton

from lib.slider import AGWSlider
from gui.panel import MyPanel

import images

def convert(i):
  if i >= 86400000:
    raise Exception("File is too large to load, it's playtime is longer " \
      "than an entire day.")
    return
  elif i >= 3600000:
    return datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(i/1000), "%H:%M:%S")
  else:
    return datetime.datetime.strftime(datetime.datetime.utcfromtimestamp(i/1000), "%M:%S")


class SoundIcon(wx.StaticBitmap):
  
  def __init__(self, parent, id=-1, bitmap=wx.NullBitmap,
    pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
    name='StaticBitmapNameStr'):
    """ init__(self, Window parent, int id=-1, Bitmap bitmap=wxNullBitmap,
     |          Point pos=DefaultPosition, Size size=DefaultSize,
     |          long style=0, String name=StaticBitmapNameStr
    """
    bmp = images.getSV100Bitmap()
    wx.StaticBitmap.__init__(self, parent, id, bmp, (100,0), (35,22), style, name)

  def toggleVolume(self, v_as_float):
    v = int(v_as_float)
    if v <= 0:
      self.SetBitmap(images.getSVMuteBitmap())
    elif v <= 25:
      self.SetBitmap(images.getSV0Bitmap())
    elif v <= 50:
      self.SetBitmap(images.getSV25Bitmap())
    elif v <= 75:
      self.SetBitmap(images.getSV50Bitmap())
    elif v < 100:
      self.SetBitmap(images.getSV75Bitmap())
    else:# v >= 100:
      self.SetBitmap(images.getSV100Bitmap())

class MediaPanel(MyPanel):
  """

  """
  bgcolor="#ffFFff"
  bgcolor="#e5e5e5"
#  bgcolor="#4C4C4C"
  volume_bar = None
  rate_bar = None
  mute_volume = 50
  is_muted = False
  _muted = False

  def set_muted(self, b):
    self._muted = b
  def get_muted(self):
    return self._muted
  muted=Muted=property(get_muted, set_muted)

  def Mute(self): self.set_muted(True)
  def toggleMute(self): self.muted = bool(not self.muted)

  #----------------------------------------------------------------------
  def __init__(self, parent, frame, log, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):
    """Constructor"""
    self.log = log

    self.frame = frame

    MyPanel.__init__(self, parent=parent, frame=frame, log=log,
      size=(100, 150), style=style)

    self.parent=parent # the splitter
    self.currentRate = 1
    self.currentVolume = 50
    self.layoutControls()
    self.disableFileButtons()
    
    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.onTimer)
    self.timer.Start(100)

  def layoutControls(self):
    """
    Create and layout the widgets
    """
    
    try:
      self.mediaPlayer = WM.MediaCtrl(self, style=wx.SIMPLE_BORDER)
    except NotImplementedError:
      self.Destroy()
      raise
        
    # create playback slider

    #self.playbackSlider = AGWSlider(self, size=wx.DefaultSize)
        
    #audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)
    # Create sizers
    a_sizer = wx.BoxSizer(wx.HORIZONTAL)
    b_sizer = wx.BoxSizer(wx.VERTICAL)
    c_sizer = wx.BoxSizer(wx.HORIZONTAL)
    control_button_sizer = self.buildAudioBar()


    self.currentPos = wx.StaticText(self, -1, '0:00', pos=wx.DefaultPosition,
      size=(48, 24), style=wx.ALIGN_RIGHT)

    self.currentLen = wx.StaticText(self, -1, ' 0:00 ', pos=wx.DefaultPosition,
      size=(48,24), style=wx.ALIGN_LEFT)

    playback_sizer  = wx.BoxSizer(wx.HORIZONTAL)

    self.playbackSlider = wx.Slider(self, size=wx.DefaultSize,
      style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
    self.playbackSlider.SetThumbLength(10)
    self.Bind(wx.EVT_SLIDER, self.onSeek, self.playbackSlider)
    
    playback_sizer.Add(self.currentPos, 0,
      wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE)
    playback_sizer.Add(self.playbackSlider, 1,
      wx.ALIGN_CENTER|wx.ALIGN_TOP|wx.EXPAND|wx.ALL)
    playback_sizer.Add(self.currentLen, 0,
      wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE)

    # layout widgets
#    b_sizer.Add((-1,24), 0, wx.EXPAND) # Spacer | spacer
    b_sizer.Add(playback_sizer, 1, wx.ALL|wx.EXPAND|wx.ALIGN_TOP)
#    b_sizer.AddStretchSpacer()

    c_sizer.Add(control_button_sizer, 1, wx.ALIGN_BOTTOM|wx.ALIGN_LEFT|wx.SOUTH|wx.EAST, 5)
#    c_sizer.AddStretchSpacer(1)
#    c_sizer.Add(self.rateBar, 0, wx.ALL|wx.EXPAND|wx.ALIGN_BOTTOM|wx.ALIGN_RIGHT)

    b_sizer.Add(c_sizer, 1, wx.ALL|wx.EXPAND|wx.ALIGN_BOTTOM)

    # parent id pos size

    self.volume_icon = SoundIcon(parent=self, id=-1, size=(35,22)) # XXX
    volumeSizerUD = wx.BoxSizer(wx.VERTICAL)
    volumeSizerLR = wx.BoxSizer(wx.HORIZONTAL)
    volumeSizerLR.Add(self.volume_icon, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 2)
    volumeSizerLR.Add(self.volumeBar, proportion=0, flag=wx.ALL|wx.EXPAND|wx.ALIGN_LEFT)
    volumeSizerUD.Add(volumeSizerLR, 1, wx.ALL|wx.EXPAND|wx.ALIGN_RIGHT)

    self.volume_icon.Bind(wx.EVT_LEFT_UP, self.onToggleMute)
    #volumeSizer_x, volumeSizer_y= volumeSizer.GetMinSize()

    #volumeSizer.SetSize(volumeSizer.GetMinSize())

    a_sizer.Add(b_sizer, 1, wx.ALL|wx.EXPAND|wx.ALIGN_TOP) # |wx.NORTH|wx.SOUTH|wx.EAST | wx.WEST)
    a_sizer.Add(volumeSizerUD, 0, wx.FIXED_MINSIZE, 2)

    self.mediaPlayer.ShowPlayerControls(True)
#    self.mediaPlayer.ShowPlayerControls(wx.media.MEDIACTRLPLAYERCONTROLS_DEFAULT)

    self.SetSizer(a_sizer)
    self.Layout()
    
  #----------------------------------------------------------------------
  def buildAudioBar(self):
    """
    Builds the audio bar controls
    """

    border_style = wx.BORDER_SUNKEN
    border_style = wx.BORDER_STATIC

    audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    audioBarSizer.Add((24,24), 0, wx.EXPAND)

    self.firstBtn = GenBitmapButton(self,
      bitmap=images.getFirstBitmap(), name="First", style=border_style)
    self.firstBtn.SetToolTipString("First")
#    self.firstBtn.Bind(wx.EVT_BUTTON, self.onFirst)
    audioBarSizer.Add(self.firstBtn, 0, wx.ALIGN_BOTTOM, 0)
    

    self.prevBtn = GenBitmapButton(self,
      bitmap=images.getPreviousBitmap(), name="Previous", style=border_style)
    self.prevBtn.Bind(wx.EVT_BUTTON, self.onPrev)
    audioBarSizer.Add(self.prevBtn, 0, wx.ALIGN_BOTTOM, 0)
    

    # create play/pause toggle button
    self.playPauseBtn = GenBitmapToggleButton(self, 
      bitmap=images.getPlayBitmap(), name="play", style=border_style)
    self.playPauseBtn.Enable(False)

    self.playPauseBtn.SetBitmapSelected(images.getPauseBitmap())
    
    self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
#    self.playPauseBtn.SetBackgroundColour(self.bgcolor)
    audioBarSizer.Add(self.playPauseBtn, 0, wx.ALIGN_BOTTOM, 0)
    

    self.stopBtn = GenBitmapButton(self, bitmap=images.getStopBitmap(),
      name="Stop", style=border_style)
    self.stopBtn.Bind(wx.EVT_BUTTON, self.onStop)
#    self.stopBtn.SetBackgroundColour(self.bgcolor)
    audioBarSizer.Add(self.stopBtn, 0, wx.ALIGN_BOTTOM, 0)


    self.nextBtn = GenBitmapButton(self, bitmap=images.getNextBitmap(),
      name="Next", style=border_style)
    self.nextBtn.Bind(wx.EVT_BUTTON, self.onNext)
#    self.nextBtn.SetBackgroundColour(self.bgcolor)
    audioBarSizer.Add(self.nextBtn, 0, wx.ALIGN_BOTTOM, 0)

    self.lastBtn = GenBitmapButton(self,
      bitmap=images.getLastBitmap(), name="Last", style=border_style)
    self.lastBtn.SetToolTipString("Last")
#    self.lastBtn.Bind(wx.EVT_BUTTON, self.onLast)
    audioBarSizer.Add(self.lastBtn, 0, wx.ALIGN_BOTTOM, 0)

    audioBarSizer.Add((14,24), 0, wx.EXPAND)

    self.keep_btn = GenBitmapButton(self, bitmap=images.getThumbsUpBitmap(), 
      name='keep', style=border_style)
    self.keep_btn.SetToolTipString("move to KEEP (CTRL+1)")
    audioBarSizer.Add(self.keep_btn, 0, wx.ALIGN_BOTTOM, 0)
    self.keep_btn.Bind(wx.EVT_BUTTON, self.onMoveToKeep)

    self.review_later_btn = GenBitmapButton(self,
      bitmap=images.getReviewLaterBitmap(), name='review_later', style=border_style)
    self.review_later_btn.SetToolTipString("Review Later (CTRL+2)")
    audioBarSizer.Add(self.review_later_btn, 0, wx.ALIGN_BOTTOM, 0)
    self.review_later_btn.Bind(wx.EVT_BUTTON, self.onMoveToReview)

    self.move_to_other_btn = GenBitmapButton(self,
      bitmap=images.getMoveToOtherBitmap(), name='move_to_other', style=border_style)
    self.move_to_other_btn.SetToolTipString("Move to Other (CTRL+3)")
    audioBarSizer.Add(self.move_to_other_btn, 0, wx.ALIGN_BOTTOM, 0)
    self.move_to_other_btn.Bind(wx.EVT_BUTTON, self.onMoveToOther)

    self.removeBtn = GenBitmapButton(self, bitmap=images.getTrashBitmap(),
      name='remove', style=border_style)
    self.removeBtn.SetToolTipString("Remove (CTRL+4)")
    audioBarSizer.Add(self.removeBtn, 0, wx.ALIGN_BOTTOM, 0)
    self.removeBtn.Bind(wx.EVT_BUTTON, self.onMoveToRemove)

    audioBarSizer.Add((64,24), 1, wx.EXPAND)


    #audioBarSizer.AddStretchSpacer(1)

    rateGroup = wx.BoxSizer(wx.VERTICAL)

    self.rate_label_e = wx.StaticText(self, -1, ' RATE ', pos=wx.DefaultPosition,
      size=(48,24), style=wx.ALIGN_CENTER)

    rateGroup.Add(self.rate_label_e, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)

    rateGroup.Add(self.rateBar, 0, wx.FIXED_MINSIZE|wx.ALIGN_CENTER)

    rateButtonsGroup = wx.BoxSizer(wx.HORIZONTAL)

    self.slowerBtn = GenBitmapButton(self,
      bitmap=images.getSlowerBitmap(), name="Slower", style=border_style)
    self.slowerBtn.SetToolTipString("Slower")
    self.slowerBtn.Bind(wx.EVT_BUTTON, self.onSlower)
    rateButtonsGroup.Add(self.slowerBtn, 0, wx.FIXED_MINSIZE|wx.ALIGN_BOTTOM, 0)

    self.rate_label = wx.StaticText(self, -1, str(self.currentRate),
      pos=wx.DefaultPosition, size=(48,24), style=wx.ALIGN_CENTER)

    rateButtonsGroup.Add(self.rate_label, 0,
      wx.ALIGN_CENTER|wx.SOUTH|wx.NORTH, 4)
      #wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL)

    self.fasterBtn = GenBitmapButton(self,
      bitmap=images.getFasterBitmap(), name="Faster", style=border_style)

    self.fasterBtn.SetToolTipString("Faster")
    self.fasterBtn.Bind(wx.EVT_BUTTON, self.onFaster)
    rateButtonsGroup.Add(self.fasterBtn, 0, wx.ALIGN_BOTTOM, 0)

    rateGroup.Add(rateButtonsGroup, 0,
      wx.FIXED_MINSIZE|wx.ALIGN_BOTTOM|wx.ALIGN_CENTER)

    audioBarSizer.Add(rateGroup, 0, wx.FIXED_MINSIZE|wx.ALIGN_TOP|wx.ALIGN_RIGHT, 0)

    audioBarSizer.Add((64,24), 1, wx.EXPAND)

    self.rate_label.Bind(wx.EVT_LEFT_DCLICK, self.onResetRate)
    self.rate_label_e.Bind(wx.EVT_LEFT_DCLICK, self.onResetRate)

    # XXX-TODO add notes to help or somewhere letting people know that double
    # clicking resets the rate to 1.0

    return audioBarSizer
          
  #----------------------------------------------------------------------

  def getRateBar(self):
    if not self.rate_bar:
      self.setRateBar()
    return self.rate_bar
  def setRateBar(self):
    """ 
    wx.Slider.__init__(self, 
import wx.lib.buttons  as  buttons
               Window parent,
               int id=-1,
               int value=0,
               int minValue=0,
               int maxValue=100,
               Point pos=DefaultPosition,
               Size size=DefaultSize,
               long style=SL_HORIZONTAL,
               Validator validator=DefaultValidator,
               String name=SliderNameStr
    """
    self.rate_bar = wx.Slider(parent=self,
                 id=-1,
                 value=4,
                 minValue=1,
                 maxValue=16,
                 pos=wx.DefaultPosition,
                 #size=(-1, 160), 
                 size=(144, -1), 
                 #style=wx.SL_VERTICAL | wx.SL_AUTOTICKS,
                 style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS,
                 name="Rate Bar"
    )
    # Frequency and Position
    self.rate_bar.SetTickFreq(4, 12)
    self.rate_bar.SetMin(1)
#    self.rate_bar.SetValue(self.currentRate*4)
    self.rate_bar.Bind(wx.EVT_SLIDER, self.onSetRate)
#    self.rate_bar.SetThumbLength(2)
  rateBar=property(getRateBar, setRateBar)

  def getVolumeBar(self):
    if not self.volume_bar:
      self.setVolumeBar()
    return self.volume_bar
  def setVolumeBar(self):
    """ 
    wx.Slider.__init__(self, 
               Window parent,
               int id=-1,
               int value=0,
               int minValue=0,
               int maxValue=100,
               Point pos=DefaultPosition,
               Size size=DefaultSize,
               long style=SL_HORIZONTAL,
               Validator validator=DefaultValidator,
               String name=SliderNameStr
    """
    self.volume_bar = wx.Slider(parent=self,
                 id=100,
                 value=25,
                 minValue=0,
                 maxValue=100,
#                 pos=(30, 50),
#                 size=(200, -1), 
                 size=(-1, 150), 
#                 style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS,
                 style=wx.SL_RIGHT | wx.SL_INVERSE | wx.SL_AUTOTICKS | wx.SL_LABELS,
                 name="Volume Bar"
    )
    # Frequency and Position
    self.volume_bar.SetTickFreq(5, 1)
    self.volume_bar.SetValue(self.currentVolume)
    self.volume_bar.Bind(wx.EVT_SLIDER, self.onSetVolume)
    self.volume_bar.SetThumbLength(2)
  volumeBar=property(getVolumeBar, setVolumeBar)
  #----------------------------------------------------------------------

  def moveFileToTarget(self, target): # (event helper)
    
    
    current_state = self.mediaPlayer.State
    
    if self.frame.current_file.folder == target:
      return
    else:
      self.frame.lp.tree.UnselectAll()

      offset = self.playbackSlider.GetValue()
      self.mediaPlayer.Stop()

      self.playPauseBtn.SetToggle(False)

      self.playPauseBtn.Enable(False)
      target_path = os.path.abspath( os.path.join( self.frame.project_path,
        target))

      old_path = self.frame.current_file.fpath
      old_folder = self.frame.current_file.folder

      new_path = self.frame.current_file.moveFile(target_path)
      
      # call rebuild on SoundFile first, so paths will update
      self.frame.current_file.rebuild(new_path) 
      # then move on project, so that paths will be correct.
      self.frame.Project.moveFile(self.frame.current_file, old_path, 
        old_folder, new_path, new_folder=target)

      self.frame.lp.rebuildTree()
      self.frame.showCurrentFile()
      
      self.playPauseBtn.Enable(True)
      if current_state == WM.MEDIASTATE_PLAYING:
        self.playPauseBtn.SetToggle(True)
#        self.mediaPlayer.Play()
        self.mediaPlayer.Seek(offset)
      elif current_state == WM.MEDIASTATE_PAUSED:
        self.mediaPlayer.Seek(offset)
#        self.mediaPlayer.Pause()

    
    return

  def onSlower(self, evt):
    rate = self.rateBar.GetValue()
    self.log.debug('retrieved a value of : %s' % rate)
    rate = float(rate)/4
    self.log.debug('rate now set to : %s' % rate)
    rate = rate - 0.25
    self.log.debug('rate recalculated to : %s' % rate)
    if rate <= 0.25: rate = 0.25
    self.currentRate = rate
    self.rate_label.SetLabel("%s" % rate)
    self.log.debug("setting rate to: %s" % float(self.currentRate))
    self.rateBar.SetValue(rate*4)
    self.mediaPlayer.SetPlaybackRate(self.currentRate)

  def onResetRate(self, evt):
    rate = 1
    self.currentRate = rate
    self.rate_label.SetLabel("%s" % rate)
    self.log.debug("setting rate to: %s" % float(self.currentRate))
    self.rateBar.SetValue(rate*4)
    self.mediaPlayer.SetPlaybackRate(self.currentRate)

  def onFaster(self, evt):
    rate = self.rateBar.GetValue()
    self.log.debug('retrieved a value of : %s' % rate)
    rate = float(rate)/4
    self.log.debug('rate now set to : %s' % rate)
    rate = rate + 0.25
    if rate >= 4.0: rate = 4.0
    self.currentRate = rate
    self.rate_label.SetLabel("%s" % rate)
    self.log.debug("setting rate to: %s" % float(self.currentRate))
    self.rateBar.SetValue(rate*4)
    self.mediaPlayer.SetPlaybackRate(self.currentRate)

  def onMoveToKeep(self, evt):
    self.moveFileToTarget('to-keep')

  def onMoveToOther(self, evt):
    self.moveFileToTarget('other')

  def onMoveToRemove(self, evt):
    self.moveFileToTarget('to-remove')

  def onMoveToReview(self, evt):
    self.moveFileToTarget('to-review')

  def onSetRate(self, event):
    """
    Sets the rate of the music player
    """
    rate = self.rateBar.GetValue()
    self.log.debug('retrieved a value of : %s' % rate)
    # resetting rate
    self.log.debug('type: %s' % type(rate))
    rate = float(rate)/4
    self.log.debug('rate now set to : %s' % rate)
    self.currentRate = rate
    self.rate_label.SetLabel("%s" % rate)
    self.log.debug("setting rate to: %s" % int(self.currentRate))
    self.mediaPlayer.SetPlaybackRate(self.currentRate)
  
  #----------------------------------------------------------------------

  def disableFileButtons(self):
    self.move_to_other_btn.Enable(False)
    self.keep_btn.Enable(False)
    self.review_later_btn.Enable(False)
    self.removeBtn.Enable(False)

  def enableFileButtons(self):
    self.move_to_other_btn.Enable(True)
    self.keep_btn.Enable(True)
    self.review_later_btn.Enable(True)
    self.removeBtn.Enable(True)

  def _on_options(self, evt):
    self.frame._options_frame.Show()
    
  #----------------------------------------------------------------------
  def loadMusic(self, musicFile):
    """"""
    if not self.mediaPlayer.Load(musicFile):
      self.playPauseBtn.Enable(False)
      self.disableFileButtons()
      wx.MessageBox("Unable to load %s: Unsupported format?" % path,
              "ERROR",
              wx.ICON_ERROR | wx.OK)
    else:
      # ALL 4 REQURES are required to get the file length in time
      self.mediaPlayer.Stop() # REQUIRED HERE 
      self.enableFileButtons()
      self.playPauseBtn.Enable(True)
      self.mediaPlayer.SetInitialSize()
      self.mediaPlayer.Play() # REQUIRED HERE
      self.GetSizer().Layout()
      time.sleep(1) # REQUIRED HERE
      self.mediaPlayer.Play() # REQUIRED HERE
      # ALL 4 REQURES are required to get the file length in time

      self.currentLen.SetLabel(convert( self.mediaPlayer.Length()) )
      length = self.mediaPlayer.Length()
      int_round_len = int(round(length))
      secs =  int_round_len/ 10000
      ticks = int(round(secs))/10
      self.playbackSlider.SetTickFreq(ticks*1000,1)
      self.playbackSlider.SetRange(0, self.mediaPlayer.Length())

      self.mediaPlayer.Play() # THIS IS THE ONE THAT PLAYS THE FILE
      self.mediaPlayer.SetPlaybackRate(self.currentRate)
      self.playPauseBtn.SetToggle(True)


#      self.mediaPlayer.Refresh()

  #----------------------------------------------------------------------
  def onNext(self, event):
    """
    Not implemented!
    """
    pass
  
  #----------------------------------------------------------------------
  def onPause(self):
    """
    Pauses the music
    """
    self.mediaPlayer.Pause()
  
  #----------------------------------------------------------------------
  def onPlay(self, event):
    """
    Plays the music
    """
    if not event.GetIsDown():
      self.onPause()
      return
    
    if not self.mediaPlayer.Play():
      wx.MessageBox("Unable to Play media : Unsupported format?",
              "ERROR",
              wx.ICON_ERROR | wx.OK)
    else:
      self.mediaPlayer.SetInitialSize()
      self.GetSizer().Layout()
      #self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
      self.playbackSlider.SetMin(0)
      self.playbackSlider.SetMax(self.mediaPlayer.Length())
      
      ticks = (int(round(int(round(self.mediaPlayer.Length())) / 10000)) / 10)*1000
      self.playbackSlider.SetTickFreq(ticks,1)
      
      self.currentPos.SetLabel(convert( self.playbackSlider.GetValue()) )
      self.currentLen.SetLabel(convert( self.mediaPlayer.Length()) )
    
    event.Skip()
  
  #----------------------------------------------------------------------
  def onPrev(self, event):
    """
    Not implemented!
    """
    return self.onFutureFeature(event)
  
  def Seek(self, ms):
    self.mediaPlayer.Seek(ms)
    self.playbackSlider.SetValue(ms)

  #----------------------------------------------------------------------
  def onSeek(self, event):
    """
    Seeks the media file according to the amount the slider has
    been adjusted.
    """
    self.Seek(self.playbackSlider.GetValue())

  #----------------------------------------------------------------------
  def onToggleMute(self, event):
    """
    Sets the volume of the music player
    """
    global log
    log = self.log

    if self.Muted:
      # put back
      self.currentVolume = self.mute_volume

      self.volumeBar.SetValue( self.currentVolume*100 )
      
      self.volume_icon.toggleVolume(self.currentVolume*100)
      self.mediaPlayer.SetVolume(self.currentVolume)
      self.toggleMute()

    else:
      self.currentVolume = float(self.volumeBar.GetValue())/100
      self.mute_volume = self.currentVolume # to set back later
      self.mediaPlayer.SetVolume(0)
      self.volume_icon.toggleVolume(0)
      self.volumeBar.SetValue(0)
      self.toggleMute()
    
  #----------------------------------------------------------------------
  def onSetVolume(self, event):
    """
    Sets the volume of the music player
    """
    global log
    if self.Muted:
      self.set_muted(False)

    log = self.log
    self.currentVolume = float(self.volumeBar.GetValue())/100
    log.debug("setting volume to: %s" % self.currentVolume)
    self.mediaPlayer.SetVolume(self.currentVolume)
    self.volume_icon.toggleVolume(self.currentVolume*100)
  
  #----------------------------------------------------------------------
  def onStop(self, event):
    """
    Stops the music and resets the play button
    """
    self.mediaPlayer.Stop()
    self.playPauseBtn.SetToggle(False)
    self.currentPos.SetLabelText("0:00")

    
  #----------------------------------------------------------------------
  def onTimer(self, event):
    """
    Keeps the player slider updated
    """
    offset = self.mediaPlayer.Tell()
    self.playbackSlider.SetValue(offset)

    if offset and offset > 0:
      self.currentPos.SetLabel(convert( offset ) )

########################################################################

