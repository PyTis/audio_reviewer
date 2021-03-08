# Built In
import os, sys
from subprocess import Popen
from distutils.dir_util import copy_tree

# Third Party
import wx.media
import wx.lib.buttons as buttons
import wx
import wx.lib.buttons  as  buttons
import wx.lib.scrolledpanel as scrolled
from wx.lib import masked

# My Stuff
from gui.images import *
#from src.OwnerDLG import OwnerDLG
#from src.GetBinsDLG import GetBinsDLG
#from src.EditDLG import EditDLG
#from src.AboutDLG import AboutDLG
from lib.log import MyLog

from images import getDarkPiSymbolIcon, getSV100Bitmap
#from util import pickle_data
#from util.zweb import GotoURL
dirName = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bitmapDir = os.path.join(dirName, 'bitmaps')
########################################################################
"""
pytis/pytis.py
lib/errors.py
lib/__init__.py [+]
lib/util.py
gui/panel.py
gui/main_frame.py    
"""

class SoundIcon(wx.StaticBitmap):
  
  def __init__(self, parent, id=-1, bitmap=wx.NullBitmap,
    pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
    name='StaticBitmapNameStr'):
    """ init__(self, Window parent, int id=-1, Bitmap bitmap=wxNullBitmap,
     |          Point pos=DefaultPosition, Size size=DefaultSize,
     |          long style=0, String name=StaticBitmapNameStr
    """
    bmp = getSV100Bitmap()
    wx.StaticBitmap.__init__(self, parent, id, bmp, (100,0), (48,48), style, name)

  def toggleVolume(self, v_as_float):
    v = int(v_as_float)
    if v <= 0:
      self.SetBitmap(getSVMuteBitmap())
    elif v <= 25:
      self.SetBitmap(getSV0Bitmap())
    elif v <= 50:
      self.SetBitmap(getSV25Bitmap())
    elif v <= 75:
      self.SetBitmap(getSV50Bitmap())
    elif v < 100:
      self.SetBitmap(getSV75Bitmap())
    else:# v >= 100:
      self.SetBitmap(getSV100Bitmap())

class MyScrolledPanel(scrolled.ScrolledPanel):

  bgcolor="#E5E5E5"
  bgimage=None


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

  def SetOtherLabel(self, label):
    wx.StaticText(self, -1, label, (4, 4))

  def showError(self, err_name, err_msg, icon=wx.ICON_ERROR):
    print('e')
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

  def SetOtherLabel(self, label):
    wx.StaticText(self, -1, label, (4, 4))

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



class MyTree(wx.TreeCtrl):
    def __init__(self, *args, **kwargs):
        pos=(0,-50)
        super(MyTree, self).__init__(*args, **kwargs)
        self.__collapsing = True
 
        il = wx.ImageList(16,16)
        self.folderidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16,16)))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)))
        self.AssignImageList(il)

        root=os.path.abspath("C:\\cygwin64\\home\\jlee\\github\\audio_reviewer\src\\store\\")
        ids = {root : self.AddRoot('Store', self.folderidx)}
        self.SetItemHasChildren(ids[root])
 
        for (dirpath, dirnames, filenames) in os.walk(root):
            for dirname in sorted(dirnames):
                fullpath = os.path.join(dirpath, dirname)
                ids[fullpath] = self.AppendItem(ids[dirpath], dirname, self.folderidx)
                 
            for filename in sorted(filenames):
                self.AppendItem(ids[dirpath], filename, self.fileidx)

class LeftPane(MyScrolledPanel):
  bgcolor='#FFFFFF'

  def __init__(self, parent, frame, log, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):

    self.frame = frame
    MyScrolledPanel.__init__(self, parent, frame, log, size,
      pos=wx.DefaultPosition, style=style)

    
    path_now = self.frame.project_path or os.curdir
    root_path=os.path.abspath(path_now)

    Bsizer = wx.BoxSizer( wx.VERTICAL)
    self.folder_tree_project = MyTree(self)
    self.folder_tree_project.dir=root_path
    self.folder_tree_project.Expand(self.folder_tree_project.GetRootItem())

#    self.folder_tree_project.ShowHidden(False)
#    self.folder_tree_project.SetDefaultPath(root_path)
#    self.folder_tree_project.SetPath(root_path)

#    Tree = self.folder_tree_project.GetTreeCtrl()

#    Tree.AppendItem(Tree.GetRootItem(), root_path)

    Bsizer.Add(self.folder_tree_project,1,wx.ALL | wx.EXPAND)
    self.SetSizer(Bsizer)
    self.folder_tree_project.SetPosition((0, -50))
    
  #----------------------------------------------------------------------
    # Timer moved from MediaPanel to here, because you can only have 1 timer
    # per Panel, otherwise, the EVT_TIMER is triggered by the other timer, even
    # though they are uniquely named..... darn.
    self.timer2 = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.onLoadProject)
    self.timer2.Start(3)
  #----------------------------------------------------------------------

  def onLoadProject(self, evt):
    self.timer2.Stop()
#    self.timer2.Unlink()
    self.frame.checkSetup()


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


class CenterPane(MyPanel):
  bgcolor='#E5E5E5'

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


    text1 = wx.StaticText( self, -1, "12-hour format:", pos=(20, 20) )
    self.time12 = masked.TimeCtrl( self, -1, name="12 hour control",
      pos=(100, 20) )
    h = self.time12.GetSize().height
#    log.error("H is: %s" % h)

    spin2 = wx.SpinButton( self, -1, wx.DefaultPosition, (-1,h), wx.SP_VERTICAL )
    self.time24 = masked.TimeCtrl(self, -1, name="Bookmark", fmt24hr=True,
      spinButton = spin2)



    self.summ_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1), pos=(20,80))

    self.desc_text_ctrl = wx.TextCtrl(self, -1, size=(400, 440), pos=(20,120), 
      style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
#    self.log_text_ctrl.SetSize(self.log_text_ctrl.GetBestSize())


class RightPane(MyScrolledPanel):
  bgcolor='#AAAAAA'

class BottomPane(MyPanel):
  bgcolor='#E5E5E5'


class MediaPanel(MyPanel):
  """

  """
  bgcolor="#ffFFff"
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
    
    sp = wx.StandardPaths.Get()

#    log.debug('sp.GetAppDocumentsDir: %s' % sp.GetAppDocumentsDir() )
#    log.info('sp.GetConfigDir: %s' % sp.GetConfigDir() )
#    log.warn('sp.GetDataDir: %s' % sp.GetDataDir() )
#    log.info1('sp.GetDocumentsDir: %s' % sp.GetDocumentsDir() )

#    log.debug('sp.GetUserLocalDataDir: %s' % sp.GetUserLocalDataDir())
#    log.debug('sp.GetUserConfigDir: %s' % sp.GetUserConfigDir() )
#    log.warn('sp.GetUserDir:', sp.GetUserDir() )

    self.currentFolder = sp.GetDocumentsDir()
    
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

    self.playbackSlider = wx.Slider(self, size=wx.DefaultSize)

    self.Bind(wx.EVT_SLIDER, self.onSeek, self.playbackSlider)
        
    # Create sizers
    mainSizer = wx.BoxSizer(wx.VERTICAL)
    hSizer = wx.BoxSizer(wx.HORIZONTAL)

    audioSizer = self.buildAudioBar()
        
    # layout widgets
    mainSizer.Add((-1,24), 0, wx.EXPAND) # Spacer | spacer
    mainSizer.Add(self.playbackSlider, 1, wx.ALL|wx.BOTTOM|wx.EXPAND, 5)

    hSizer.Add(audioSizer, 40, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)

#   Add(self, item, int proportion=0, int flag=0, int border=0, |PyObject userData=None)
    self.rate_label = wx.StaticText(self, -1, 'Rate: 1', (4, 4))

    rateSizer = wx.BoxSizer(wx.VERTICAL)
    rateSizer.Add(self.rateBar, proportion=0, flag=wx.ALL|wx.CENTER, border=10)
    rateSizer.Add(self.rate_label, 0, wx.ALL|wx.CENTER, 2)

    self.volume_icon = SoundIcon(parent=self, id=-1, size=(48,48))
    volume_label = wx.StaticText(self, -1, 'Volume', (4, 4))

    volumeSizer = wx.BoxSizer(wx.VERTICAL)
    volumeSizer.Add(self.volumeBar, proportion=0, flag=wx.ALL|wx.CENTER, border=10)
    volumeSizer.Add(volume_label, 0, wx.ALL|wx.CENTER, 2)

    self.mediaPlayer.ShowPlayerControls(True)

    hSizer.Add(rateSizer, 35, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 2)

    hSizer.Add(self.volume_icon, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 2)
    hSizer.Add(volumeSizer, 35, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT, 2)

    mainSizer.Add(hSizer, 50, wx.ALIGN_TOP |wx.ALIGN_CENTER, 2)
    
    self.SetSizer(mainSizer)
    self.Layout()
    
  #----------------------------------------------------------------------
  def buildAudioBar(self):
    """
    Builds the audio bar controls
    """
    audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)
    
    audioBarSizer.Add((48,48), 0, wx.EXPAND)

    self.buildBtn({'bitmap':'player_prev.png', 
             'handler':self.onPrev,
             'name':'prev'
             },
            audioBarSizer)
    
#    audioBarSizer.Add((4,48), 0, wx.EXPAND)

    # create play/pause toggle button
    img = wx.Bitmap(os.path.join(bitmapDir, "player_play.png"))
    self.playPauseBtn = buttons.GenBitmapToggleButton(self, bitmap=img, name="play")
    self.playPauseBtn.Enable(False)

    img = wx.Bitmap(os.path.join(bitmapDir, "player_pause.png"))
    self.playPauseBtn.SetBitmapSelected(img)
    self.playPauseBtn.SetInitialSize()
    
    self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
    audioBarSizer.Add(self.playPauseBtn, 0, wx.LEFT, 3)
    
#    audioBarSizer.Add((4,48), 0, wx.EXPAND)

    btnData = [{'bitmap':'player_stop.png',
          'handler':self.onStop, 
          'name':'stop'
          }]

    for btn in btnData:
      self.buildBtn(btn, audioBarSizer)
    
#    audioBarSizer.Add((4,48), 0, wx.EXPAND)

    btnData = [{'bitmap':'player_next.png',
           'handler':self.onNext, 
           'name':'next'
          }
          ]
    for btn in btnData:
      self.buildBtn(btn, audioBarSizer)
      
    return audioBarSizer
          
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
                 style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS,
                 name="Rate Bar"
    )
    # Frequency and Position
    self.rate_bar.SetTickFreq(4, 16)
    self.rate_bar.SetMin(1)
#    self.rate_bar.SetValue(self.currentRate*4)
    self.rate_bar.Bind(wx.EVT_SLIDER, self.onSetRate)
  rateBar=property(getRateBar, setRateBar)
  #----------------------------------------------------------------------
  def onSetRate(self, event):
    """
    Sets the rate of the music player
    """
    rate = self.rateBar.GetValue()
    print('retrieved a value of : %s' % rate)
    # resetting rate
    print('type: %s' % type(rate))
    rate = float(rate)/4
    print('rate now set to : %s' % rate)
    self.currentRate = rate
    self.rate_label.SetLabel("Rate: %s " % rate)
    print("setting rate to: %s" % int(self.currentRate))
    self.mediaPlayer.SetPlaybackRate(self.currentRate)
  

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
                 pos=(30, 50),
                 size=(250, -1), 
                 style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS,
                 name="Volume Bar"
    )
    # Frequency and Position
    self.volume_bar.SetTickFreq(5, 1)
    self.volume_bar.SetValue(self.currentVolume)
    self.volume_bar.Bind(wx.EVT_SLIDER, self.onSetVolume)
  volumeBar=property(getVolumeBar, setVolumeBar)

  def buildBtn(self, btnDict, sizer):
    """"""
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

    self.currentVolume = float(self.volumeBar.GetValue())/100
    print("setting volume to: %s" % self.currentVolume)
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
