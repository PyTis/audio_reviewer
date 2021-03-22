import os
# Third Party
import wx.media
import wx

import wx.lib.buttons  as  buttons
from wx.lib.buttons import GenBitmapButton, GenBitmapToggleButton

from lib.slider import AGWSlider
from gui.panel import MyPanel

import images

dirName = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bitmapDir = os.path.join(dirName, 'bitmaps')

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
  volume_bar = None
  rate_bar = None
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
    
    self.timer = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.onTimer)
    self.timer.Start(100)
      

  def SetOtherLabel(self, label):
    wx.StaticText(self, -1, label, (4, 4))

  def layoutControls(self):
    """
    Create and layout the widgets
    """
    
    try:
      self.mediaPlayer = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
    except NotImplementedError:
      self.Destroy()
      raise
        
    # create playback slider

    #self.playbackSlider = AGWSlider(self, size=wx.DefaultSize)
        
    # Create sizers
    outer_sizer = wx.BoxSizer(wx.HORIZONTAL)

    main_sizer = wx.BoxSizer(wx.HORIZONTAL)

    self.playbackSlider = wx.Slider(self, size=wx.DefaultSize)
    self.Bind(wx.EVT_SLIDER, self.onSeek, self.playbackSlider)

    hSizer = wx.BoxSizer(wx.VERTICAL)

    audioSizer = self.buildAudioBar()
        
    # layout widgets
#    main_sizer.Add((-1,24), 0, wx.EXPAND) # Spacer | spacer
    hSizer.Add(self.playbackSlider, 1, wx.ALL|wx.EXPAND|wx.BOTTOM|wx.NORTH|wx.SOUTH|wx.EAST | wx.WEST, 5)

    hSizer.Add(audioSizer, 40, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.NORTH|wx.SOUTH|wx.EAST | wx.WEST, 5)

#   Add(self, item, int proportion=0, int flag=0, int border=0, |PyObject userData=None)
    self.rate_label = wx.StaticText(self, -1, 'Rate: 1', (4, 4))

    rateSizer = wx.BoxSizer(wx.VERTICAL)
    rateSizer.Add(self.rateBar, proportion=0, flag=wx.ALL|wx.CENTER, border=10)
    rateSizer.Add(self.rate_label, 0, wx.ALL|wx.CENTER, 2)

    self.volume_icon = SoundIcon(parent=self, id=-1, size=(35,22))
    volume_label = wx.StaticText(self, -1, ' ', (4, 4))

    volumeSizer = wx.BoxSizer(wx.VERTICAL)
    volumeSizer.Add(self.volumeBar, proportion=0, flag=wx.ALL|wx.EXPAND|wx.ALIGN_LEFT)
    volumeSizer.Add(volume_label, 0, wx.ALL|wx.EXPAND|wx.ALIGN_LEFT, 2)
    volumeSizer.Add(self.volume_icon, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 2)

    #self.mediaPlayer.ShowPlayerControls(True)

    #hSizer.Add(volumeSizer, 35, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, 2)
    
    main_sizer.Add(hSizer, 80)

    main_sizer.Add(rateSizer, 10)

#    outer_sizer.Add(hSizer, 50)
    outer_sizer.Add(main_sizer, 80, wx.ALIGN_CENTER)
#    outer_sizer.Add(rateSizer, 50)
    outer_sizer.Add(volumeSizer, 100, wx.ALL|wx.EXPAND)

#    outer_sizer.Add(volumeSizer, 50, wx.ALL|wx.EXPAND)

    self.SetSizer(outer_sizer)
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
    audioBarSizer.Add(self.firstBtn, 0, wx.LEFT, 0)
    

    self.prevBtn = GenBitmapButton(self,
      bitmap=images.getPreviousBitmap(), name="Previous", style=border_style)
    self.prevBtn.Bind(wx.EVT_BUTTON, self.onPrev)
    audioBarSizer.Add(self.prevBtn, 0, wx.LEFT, 0)
    

    # create play/pause toggle button
    self.playPauseBtn = GenBitmapToggleButton(self, 
      bitmap=images.getPlayBitmap(), name="play", style=border_style)
    self.playPauseBtn.Enable(False)

    self.playPauseBtn.SetBitmapSelected(images.getPauseBitmap())
    
    self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
    audioBarSizer.Add(self.playPauseBtn, 0, wx.LEFT, 0)
    

    self.stopBtn = GenBitmapButton(self, bitmap=images.getStopBitmap(),
      name="Stop", style=border_style)
    self.stopBtn.Bind(wx.EVT_BUTTON, self.onStop)
    audioBarSizer.Add(self.stopBtn, 0, wx.LEFT, 0)


    self.nextBtn = GenBitmapButton(self, bitmap=images.getNextBitmap(),
      name="Next", style=border_style)
    self.nextBtn.Bind(wx.EVT_BUTTON, self.onNext)
    audioBarSizer.Add(self.nextBtn, 0, wx.LEFT, 0)

    self.lastBtn = GenBitmapButton(self,
      bitmap=images.getLastBitmap(), name="Last", style=border_style)
    self.lastBtn.SetToolTipString("Last")
#    self.lastBtn.Bind(wx.EVT_BUTTON, self.onLast)
    audioBarSizer.Add(self.lastBtn, 0, wx.LEFT, 0)

    audioBarSizer.Add((14,24), 0, wx.EXPAND)

    self.keep_btn = GenBitmapButton(self, bitmap=images.getThumbsUpBitmap(), 
      name='keep', style=border_style)
    self.keep_btn.SetToolTipString("Keep")
    audioBarSizer.Add(self.keep_btn, 0, wx.LEFT, 0)

    self.review_later_btn = GenBitmapButton(self,
      bitmap=images.getReviewLaterBitmap(), name='review_later', style=border_style)
    self.review_later_btn.SetToolTipString("Review Later")
    audioBarSizer.Add(self.review_later_btn, 0, wx.LEFT, 0)

    self.move_to_other_btn = GenBitmapButton(self,
      bitmap=images.getMoveToOtherBitmap(), name='move_to_other', style=border_style)
    self.move_to_other_btn.SetToolTipString("Move to Other")
    audioBarSizer.Add(self.move_to_other_btn, 0, wx.LEFT, 0)

    self.removeBtn = GenBitmapButton(self, bitmap=images.getTrashBitmap(),
      name='remove', style=border_style)
    self.removeBtn.SetToolTipString("Remove")
    self.removeBtn.Bind(wx.EVT_BUTTON, self.onRemoveFile)
    audioBarSizer.Add(self.removeBtn, 0, wx.LEFT, 0)

    audioBarSizer.Add((14,24), 0, wx.EXPAND)

    self.slowerBtn = GenBitmapButton(self,
      bitmap=images.getSlowerBitmap(), name="Slower", style=border_style)
    self.slowerBtn.SetToolTipString("Slower")
#    self.slowerBtn.Bind(wx.EVT_BUTTON, self.onSlower)
    audioBarSizer.Add(self.slowerBtn, 0, wx.LEFT, 0)

    self.fasterBtn = GenBitmapButton(self,
      bitmap=images.getFasterBitmap(), name="Faster", style=border_style)
    self.fasterBtn.SetToolTipString("Faster")
#    self.fasterBtn.Bind(wx.EVT_BUTTON, self.onFaster)
    audioBarSizer.Add(self.fasterBtn, 0, wx.LEFT, 0)


    audioBarSizer.Add((14,24), 0, wx.EXPAND)

    return audioBarSizer
          
  def onRemoveFile(self, evt):
    pass

  def onKeepFile(self, evt):
    pass

  def onMoveFileToReview(self, evt):
    pass

  #----------------------------------------------------------------------
  def buildPrevButton(self):
    pass

  def buildPlayButton(self):
    pass

  def buildPauseButton(self):
    pass

  def buildStopButton(self):
    pass

  def buildNextButton(self):
    pass
    pass

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
                 size=(160, -1), 
                 style=wx.SL_VERTICAL | wx.SL_AUTOTICKS,
                 #style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS,
                 name="Rate Bar"
    )
    # Frequency and Position
    self.rate_bar.SetTickFreq(4, 16)
    self.rate_bar.SetMin(1)
#    self.rate_bar.SetValue(self.currentRate*4)
    self.rate_bar.Bind(wx.EVT_SLIDER, self.onSetRate)
    self.rate_bar.SetThumbLength(200)
  rateBar=property(getRateBar, setRateBar)
  #----------------------------------------------------------------------
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
    self.rate_label.SetLabel("Rate: %s " % rate)
    self.log.debug("setting rate to: %s" % int(self.currentRate))
    self.mediaPlayer.SetPlaybackRate(self.currentRate)
  
  #----------------------------------------------------------------------
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

  def buildBtn(self, btnDict, sizer):
    """
    # XXX-FINDME
    """
    bmp = btnDict['bitmap']
    handler = btnDict['handler']
        
    img = wx.Bitmap(os.path.join(bitmapDir, bmp))
    btn = buttons.GenBitmapButton(self, bitmap=img, name=btnDict['name'])
    btn.SetInitialSize()
    btn.Bind(wx.EVT_BUTTON, handler)
    sizer.Add(btn, 0, wx.LEFT, 3)
    sizer.Add((4,48), 0, wx.EXPAND)
    

  def _on_options(self, evt):
    self.frame._options_frame.Show()

    
  #----------------------------------------------------------------------
  def loadMusic(self, musicFile):
    """"""
    if not self.mediaPlayer.Load(musicFile):
      wx.MessageBox("Unable to load %s: Unsupported format?" % path,
              "ERROR",
              wx.ICON_ERROR | wx.OK)
    else:
      self.mediaPlayer.SetInitialSize()
      self.GetSizer().Layout()
      self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
      self.playPauseBtn.Enable(True)
      
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
      self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
      
    event.Skip()
  
  #----------------------------------------------------------------------
  def onPrev(self, event):
    """
    Not implemented!
    """
    pass
  
  #----------------------------------------------------------------------
  def onSeek(self, event):
    """
    Seeks the media file according to the amount the slider has
    been adjusted.
    """
    offset = self.playbackSlider.GetValue()
    self.mediaPlayer.Seek(offset)
    
  #----------------------------------------------------------------------
  def onSetVolume(self, event):
    """
    Sets the volume of the music player
    """
    global log
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
    
  #----------------------------------------------------------------------
  def onTimer(self, event):
    """
    Keeps the player slider updated
    """
    offset = self.mediaPlayer.Tell()
    self.playbackSlider.SetValue(offset)

########################################################################

