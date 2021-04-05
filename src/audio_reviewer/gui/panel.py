# Built In
import os, sys
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



from wx.lib.mixins.treemixin import DragAndDrop
class MyTree(DragAndDrop, wx.TreeCtrl):
#class MyTree(wx.TreeCtrl):
#class MyTree(wx.TreeCtrl, DragAndDrop):

  def Collapse(self, *args, **kwargs):
    return False

  def OnDrop(self, from_item, to_item):
    log=self.log
    data1 = self.GetPyData(from_item)
    log.info(data1)
    print(data1)
    data2 = self.GetPyData(to_item)
    print(data2)
    log.info(data2)

    log.warn("="*80)
    log.info(event)
    log.info(type(event))
    log.info(dir(event))
    log.info(event2)
    log.info(type(event2))
    log.info(dir(event2))
    log.warn("="*80)

    return
    if self.item:
      self.log.warn("ITEM IS: %s" % self.item)

      result = self.tree.GetPyData(self.item)
      test = os.path.abspath(result) 
      self.log.error("TEST: %s" % result)

#      if os.path.isfile(test) and os.path.exists(test): self.frame.bp.loadMusic(test)

    self.log.debug(dir(event))

    event.Skip()
    return False

  def __init__(self, *args, **kwargs):
    pos=(0,-50)
    super(MyTree, self).__init__(*args, **kwargs)
    self.__collapsing = True
    self.parent = args[0]
    self.log = self.parent.log

    il = wx.ImageList(16,16)

    self.folderidx = il.Add(images.getOther16x16Bitmap())
    self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16,16)))

    self.folderidother = il.Add(images.getTrash16x16Bitmap())
    self.folderidquestion = il.Add(images.getQuestion16x16Bitmap())
    self.folderidthumb = il.Add(images.getThumb16x16Bitmap())

    self.AssignImageList(il)


  #def addData(self, rpath="C:\\cygwin64\\home\\jlee\\github\\audio_reviewer\src\\store\\"):
  def addData(self, rpath):
    global acceptable_extensions
#    acceptable_extensions = self.parent.frame.acceptable_extensions

    root_path=os.path.abspath(rpath)
    self.root = self.AddRoot('Store', self.folderidx)
    ids = {root_path : self.root}
    self.SetPyData(self.root, root_path)

    self.SetItemHasChildren(ids[root_path])

    for (dirpath, dirnames, filenames) in os.walk(root_path):
      for dirname in sorted(dirnames):
          fullpath = os.path.join(dirpath, dirname)
          
          if dirname == 'to-keep':
            self.log.info4('dirname is: %s' % dirname)
            ids[fullpath] = self.AppendItem(ids[dirpath], dirname,
              self.folderidthumb)
          elif dirname == 'to-review':
            self.log.info4('dirname in to-review is: %s' % dirname)
            self.review_folder_item = self.AppendItem(ids[dirpath], dirname,
              self.folderidquestion)
            ids[fullpath] = self.review_folder_item

          elif dirname == 'to-remove':
            ids[fullpath] = self.AppendItem(ids[dirpath], dirname,
              self.folderidother)
          else:
            ids[fullpath] = self.AppendItem(ids[dirpath], dirname,
              self.folderidx)

          self.SetPyData(ids[fullpath], fullpath)
             
      for filename in sorted(filenames):
        sfile = SoundFile(os.path.abspath(os.path.join(dirpath, filename)))
        if sfile.ext.lower() in acceptable_extensions:
          child_fpath = os.path.abspath(os.path.join(dirpath, filename))
          child_file = self.AppendItem(ids[dirpath], filename, self.fileidx)
          self.SetPyData(child_file, child_fpath)

    self.log.debug(ids)
    self.Expand(self.review_folder_item)

class LeftPane(MyScrolledPanel):
  bgcolor='#FFFFFF'

  @property
  def Project(self):
    return self.frame.Project

  def reloadTree(self, Project=None):
    project = Project or self.Project
    self.tree.DeleteAllItems()
    self.Refresh()
    self.tree.addData(project.path)
    return
  rebuildTree=reloadTree # alias

  def __init__(self, parent, frame, log, size, pos=wx.DefaultPosition,
    style=wx.SIMPLE_BORDER):

    self.frame = frame

    MyScrolledPanel.__init__(self, parent, frame, log, size,
      pos=wx.DefaultPosition, style=style)
    self.log=log
    
    path_now = self.frame.project_path
    root_path=os.path.abspath(path_now)

    Bsizer = wx.BoxSizer( wx.VERTICAL)

    self.tree = MyTree(self)
#    self.tree.dir=root_path

#    self.tree.Expand(self.tree.GetRootItem())

    self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.tree)
    self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
#    self.tree.ShowHidden(False)
#    self.tree.SetDefaultPath(root_path)
#    self.tree.SetPath(root_path)

#    Tree = self.tree.GetTreeCtrl()

#    Tree.AppendItem(Tree.GetRootItem(), root_path)

    Bsizer.Add(self.tree,1,wx.ALL | wx.EXPAND)
    self.SetSizer(Bsizer)
 #   self.tree.SetPosition((0, -50))
    
  #----------------------------------------------------------------------
    # Timer moved from MediaPanel to here, because you can only have 1 timer
    # per Panel, otherwise, the EVT_TIMER is triggered by the other timer, even
    # though they are uniquely named..... darn.
    self.timer2 = wx.Timer(self)
    self.Bind(wx.EVT_TIMER, self.onLoadProject)
    self.timer2.Start(3)
  #----------------------------------------------------------------------
    self.Bind(wx.EVT_ERASE_BACKGROUND, self.onEraseBackground)

  def onEraseBackground(self, evt):
    dc = evt.GetDC()
    if not dc:
      dc = wx.ClientDC(self)
      rect = self.GetUpdateRegion().GetBox()
      dc.SetClippingRect(rect)

  def onLoadProject(self, evt):
    self.timer2.Stop()
#    self.timer2.Unlink()
    self.frame.checkSetup()

  def setSoundFile(self, fpath):
    pass

  def OnSelChanged(self, event):
    self.item = event.GetItem()
    self.log.debug("ITEM IS: %s" % self.item)


    if self.item:
      result = self.tree.GetPyData(self.item)
      test = os.path.abspath(result) 
      if os.path.isfile(test) and os.path.exists(test):
        self.frame.bp.mediaPlayer.Stop()
        self.frame.current_file = SoundFile(test)
        #self.frame.bp.loadMusic(test)

      if wx.Platform == '__WXMSW__':
        self.log.debug("BoundingRect: %s\n" %
                   self.tree.GetBoundingRect(self.item, True))

      #items = self.tree.GetSelections()
      #print map(self.tree.GetItemText, items)
    event.Skip()

  def OnActivate(self, event):
    if self.item:
      self.log.debug("OnActivate: %s\n" % self.tree.GetItemText(self.item))

  
  def openProject(self, Project):
    return self.reloadTree(Project)
#    self.tree.root_dir=Project.path
    #path_now = self.frame.project_path or os.curdir
    path_now = str(Project.path)
    root_path=os.path.abspath(path_now)
    self.tree.dir = root_path
    self.tree.addData(root_path)
#    self.tree.Expand(self.tree.GetRootItem())

#    self.tree.ShowHidden(False)
#    self.tree.SetDefaultPath(root_path)
#    self.tree.SetPath(root_path)

#    Tree = self.tree.GetTreeCtrl()

#    Tree.AppendItem(Tree.GetRootItem(), root_path)


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

    border_style = wx.BORDER_STATIC

    border_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer = wx.BoxSizer(wx.VERTICAL)

    first_row_sizer = wx.BoxSizer(wx.HORIZONTAL)

    bookmark = wx.StaticText(self, -1, 'Bookmark Time:')
    spin2 = wx.SpinButton( self, -1, pos=(20, 40), size=(-1,23), style=wx.SP_VERTICAL )
    self.time24 = masked.TimeCtrl(self, -1, name="Bookmark", fmt24hr=True,
      spinButton = spin2)
    self.time24.SetSize( (66,-1) )
    first_row_sizer.Add(bookmark, 20, wx.ALL|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL,2)

    first_row_sizer.Add(self.time24, 15, wx.FIXED_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 2)

    first_row_sizer.Add(spin2, 5, wx.EXPAND|wx.ALL, 2)

    self.captureBtn = GenBitmapButton(self,
      bitmap=images.getClockBitmap(), name="Capture", style=border_style)
    self.captureBtn.SetToolTipString("Grab Timestamp")
    self.captureBtn.Bind(wx.EVT_BUTTON, self.onGrabTime)
    first_row_sizer.Add(self.captureBtn, 0, wx.EXPAND|wx.ALL) # Spacer, 

    self.insertBtn = GenBitmapButton(self,
      bitmap=images.getPlusBitmap(), name="Insert", style=border_style)
    self.insertBtn.SetToolTipString("Create Bookmark")
    self.insertBtn.Bind(wx.EVT_BUTTON, self.onInsertBookmark)
    first_row_sizer.Add(self.insertBtn, 0, wx.EXPAND|wx.ALL) # Spacer, 

    self.removeBtn = GenBitmapButton(self,
      bitmap=images.getMinusBitmap(), name="Remove", style=border_style)
    self.removeBtn.SetToolTipString("Remove Bookmark")
    self.removeBtn.Bind(wx.EVT_BUTTON, self.onRemoveBookmark)
    self.removeBtn.Enable(False)
    first_row_sizer.Add(self.removeBtn, 0, wx.EXPAND|wx.ALL) # Spacer, 


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
    self.summ_text_ctrl = wx.TextCtrl(self, -1, size=(400, -1))#, pos=(20,80))
    summary_sizerr.Add(self.summ_text_ctrl, 80, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 2)

    desc_txt = wx.StaticText(self, -1, 'Description:')
    self.desc_text_ctrl = wx.TextCtrl(self, -1, size=(400, 440),# pos=(20,120), 
      style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

    main_sizer.Add(first_row_sizer, 2, wx.EXPAND|wx.ALL|wx.ALIGN_BOTTOM |wx.ALIGN_LEFT)
    main_sizer.Add(summary_sizerr, 2, wx.ALIGN_TOP |wx.ALIGN_LEFT)
    main_sizer.Add(desc_txt, 2, wx.ALIGN_TOP |wx.ALIGN_LEFT)
    main_sizer.Add(self.desc_text_ctrl, 96, wx.ALIGN_TOP |wx.ALIGN_LEFT)
    border_sizer.Add(main_sizer, 100, wx.EXPAND|wx.ALL, 20) 
    self.SetSizer(border_sizer)
    self.Layout()
#    self.log_text_ctrl.SetSize(self.log_text_ctrl.GetBestSize())

  def onGrabTime(self, evt):
    pass

  def onInsertBookmark(self, evt):
    pass

  def onRemoveBookmark(self, evt):
    pass

class RightPane(MyScrolledPanel):
  bgcolor='#AAAAAA'

class BottomPane(MyPanel):
  bgcolor='#E5E5E5'


