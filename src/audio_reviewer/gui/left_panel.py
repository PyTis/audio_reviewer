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
from gui.panel import MyScrolledPanel
from lib.project import acceptable_extensions
from lib.settings import CONFIG
from lib.soundfile import SoundFile

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
    data2 = self.GetPyData(to_item)
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
    self.idbookmark = il.Add(images.getLittleBubbleBitmap())
    self.idbookmark = il.Add(images.getBwBookmark16x16Bitmap())

    self.AssignImageList(il)


  #def addData(self, rpath="C:\\cygwin64\\home\\jlee\\github\\audio_reviewer\src\\store\\"):
  def addData(self, rpath):
    global acceptable_extensions
#    acceptable_extensions = self.parent.frame.acceptable_extensions

    root_path=os.path.abspath(rpath)
    self.root = self.AddRoot('Store', self.folderidx)
    ids = {root_path : self.root}
    self.SetPyData(self.root, (root_path, 'root'))

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

          self.SetPyData(ids[fullpath], (fullpath, 'folder'))
             
      for filename in sorted(filenames):
        sfile = SoundFile(os.path.abspath(os.path.join(dirpath, filename)))
        if sfile.ext.lower() in acceptable_extensions:
          child_fpath = os.path.abspath(os.path.join(dirpath, filename))

          bookmark_times = self.parent.frame.Project.bookmarksFor(sfile).keys()
          bookmarks = self.parent.frame.Project.bookmarksFor(sfile)

          child_file = self.AppendItem(ids[dirpath], filename, self.fileidx)


          self.SetPyData(child_file, (child_fpath, 'file'))
          if self.parent.frame.current_file and \
            child_fpath == self.parent.frame.current_file.fpath:
            self.SelectItem(child_file)
    
          bookmark_times.sort()
          
          for bmtime in bookmark_times:
            bm = bookmarks[bmtime]

            text = '%s %s...' % (bm['time'], bm['summ'][:22])
            child_bm = self.AppendItem(child_file, text, self.idbookmark)

            self.SetPyData(child_bm, (bm['time'], 'bookmark'))

          self.Expand(child_file)


    self.log.debug(ids)
    self.Expand(self.review_folder_item)
class LeftPane(MyScrolledPanel):
  bgcolor='#FFFFFF'

  loading_project = False

  @property
  def Project(self):
    return self.frame.Project

  def reloadTree(self):
    self.tree.DeleteAllItems()
    self.Refresh()
    self.tree.addData(self.frame.Project.path)
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

    #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate, self.tree)
    self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, self.tree)
    #self.Bind(wx.EVT_LEFT_UP, self.OnSelectFile, self.tree.parent)

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

  def OnSelectFile(self, evt):
    self.item = event.GetItem()
    self.log.warn("ITEM IS: %s" % self.item)

    if self.item:
      result = self.tree.GetPyData(self.item)
      test = os.path.abspath(result[0]) 
      if os.path.isfile(test) and os.path.exists(test):
        self.frame.bp.mediaPlayer.Stop()
        self.frame.current_file = SoundFile(test)
        self.frame.bp.loadMusic(test)
      if wx.Platform == '__WXMSW__':
        self.log.debug("BoundingRect: %s\n" %
                   self.tree.GetBoundingRect(self.item, True))
    event.Skip()
    

  def OnSelChanged(self, event):
    if self.loading_project: return

    self.item = event.GetItem()
    self.log.debug("ITEM IS: %s" % self.item)


    if self.item:
      result = self.tree.GetPyData(self.item)
      item_type = result[1]

      if item_type == 'file':
        fpath = result[0]
        test = os.path.abspath(fpath) 
        if os.path.isfile(test) and os.path.exists(test):
          self.frame.bp.mediaPlayer.Stop()
          self.frame.current_file = SoundFile(test)
          self.frame.bp.loadMusic(test)

      elif item_type == 'bookmark':
        bookmark_time = result[0]
        parent_item = self.tree.GetItemParent(self.item)
        parent_result = self.tree.GetPyData(parent_item)

        test = os.path.abspath(parent_result[0]) 
        if os.path.isfile(test) and os.path.exists(test) and \
          (not self.frame.current_file or \
          not (self.frame.current_file.fpath == test)):
          self.frame.bp.mediaPlayer.Stop()
          self.frame.current_file = SoundFile(test)
          self.frame.bp.loadMusic(test)

        self.frame.cp.loadBookmark(bookmark_time)

      if wx.Platform == '__WXMSW__':
        self.log.debug("BoundingRect: %s\n" %
                   self.tree.GetBoundingRect(self.item, True))

      #items = self.tree.GetSelections()
    event.Skip()

  def OnActivate(self, event):
    if self.item:
      self.log.debug("OnActivate: %s\n" % self.tree.GetItemText(self.item))

  
  def openProject(self):
    return self.reloadTree()


