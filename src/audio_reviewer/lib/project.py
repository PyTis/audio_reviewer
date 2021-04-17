
import os, sys
import configobj as COBJ

acceptable_extensions = ['.midi', '.m4a', '.mp3', '.wav', '.wma']

class NullDefault:
  pass

class Project(object):
  """

  """
  _cfile=None
  name = None
  path = None
  _folders = ['to-keep', 'to-review', 'to-remove', 'other']
  _data = {
    'to-keep' : {},
    'to-review' : {},
    'to-remove' : {},
    'other' : {}
  }

  def set_data(self, data):
    self._data = data
  def get_data(self):
    return self._data
  data=property(get_data, set_data)

  def set_folders(self,folders):
    self._folders=folders
  def get_folders(self):
    return self._folders
  folders=property(get_folders, set_folders)

  @property
  def keep(self):
    return os.path.abspath(os.path.join(self.path, 'to-keep'))

  @property
  def review(self):
    return os.path.abspath(os.path.join(self.path, 'to-review'))

  @property
  def remove(self):
    return os.path.abspath(os.path.join(self.path, 'to-remove'))

  @property
  def other(self):
    return os.path.abspath(os.path.join(self.path, 'to-other'))

  def set_cfile(self,cfile):
    self._cfile=cfile
  def get_cfile(self):
    return self._cfile
  cfile=property(get_cfile, set_cfile)

  def validate(self):
    for folder in folders:
      path = os.path.abspath(os.path.join(self.path, folder))
      self.addFolder(folder, path)


# --------------------------------------------------------------------------- #

  def __init__(self, name=None, path=None):
    
    if name: self.name=name
    if path: self.path=path

    if self._config_file_path and os.path.exists(self._config_file_path):
      self.load()

  def validateCoreFolders(self):
    call_save = False
    if self.path:

      for folder in self._folders:
        fpath = os.path.abspath(os.path.join(self.path, folder))
        if not os.path.exists(fpath):
          try:
            os.mkdir(fpath, 0777)
          except (OSError, IOError) as e:
            print("an error occured when attempting to create folder: %s"%fpath)
            print(e)
          else:
            call_save = True

      if call_save:
        self.saveData()


  # ------------------------------------------------------------------------- #
  def addBookmark(self, SoundFile, bookmark={}):
    btime = bookmark['time']

    # is this soundfile already in the dict?
    if not self.data.get(SoundFile.folder, {}):
      self.data[SoundFile.folder] = {}

    if not self.data[SoundFile.folder].get(SoundFile.fpath):
      self.data[SoundFile.folder][SoundFile.fpath] = {}
  
    
    self.data[SoundFile.folder][SoundFile.fpath].update( {
      'name' : SoundFile.name,
      'filename' : SoundFile.filename,
      'filepath' : SoundFile.filepath,
    })
  
    bookmarks=self.data[SoundFile.folder][SoundFile.fpath].get('bookmarks', {})

    bookmarks[btime] = bookmark

    self.data[SoundFile.folder][SoundFile.fpath]['bookmarks'] = bookmarks
    self.save()

  def bookmarksFor(self, SoundFile):
    return self.data.get(SoundFile.folder, {}).get(SoundFile.fpath,
      {}).get('bookmarks', {})

  def removeBookmark(self, SoundFile, bookmark_time):
    bookmarks = self.bookmarksFor(SoundFile)
    del bookmarks[bookmark_time]
    self.data[SoundFile.folder][SoundFile.fpath]['bookmarks'] = bookmarks
    self.save()

  def moveFile(self, SoundFile, old_path, old_folder, new_path, new_folder):
  #self.Project.moveFile(old_path, old_folder, new_path, new_folder=target)
    data = self.data.get(old_folder, {}).get(old_path, {})
    bookmarks = data.get('bookmarks', {})

    if data:
      del self.data[old_folder][old_path]
      data['filepath'] = new_path

    data = {
      'name' : SoundFile.name,
      'filename' : SoundFile.filename,
      'filepath' : new_path,
      'bookmarks' : bookmarks
    }

    if not self.data.get(new_folder, {}):
      self.data[new_folder] = {}

    self.data[new_folder][new_path] = data
    self.save()

  @property
  def _config_file_path(self):
    if not self.path:
      return None
    return os.path.abspath(os.path.join(self.path, 'data.ini'))

              
  def load(self):
    self.cfile = COBJ.ConfigObj(self._config_file_path)
    data = {}

    for k, v  in self.cfile.items():
      if k == 'data':
        for kk, vv in v.items():
          data[kk] = vv

      self.__setattr__(k, v)
    """ 
    for folder_name, folders in data.items():
      for file_name, file_data in folders.items():
        fixed_bookmarks = {}

        if data[folder_name][file_name].get('bookmarks'):

          bookmarks = data[folder_name][file_name].get('bookmarks')
          if bookmarks and type(bookmarks) is type([]):
            for bookmark in bookmarks:
              bookmark = eval(bookmark)
              fixed_bookmarks[bookmark['time']] = {
                  'time':bookmark['time'],
                  'summ':bookmark['summ'],
                  'desc':bookmark['desc']
              }
          elif bookmarks and type(bookmarks) is type({}):
            fixed_bookmarks.update(bookmarks)

        data[folder_name][file_name]['bookmarks'] = fixed_bookmarks
    """
          
    self.data = data
    
  @property
  def record(self):
    return {
  #    'project-settings' : '',
      'name'    : self.name,
      'path'    : self.path,
      'folders' : self.folders,
      'data' : self.data
    }

  def write(self):
    cfile = COBJ.load(self._config_file_path, True)
    cfile.update(self.record)
    cfile.save()

  def save(self):
    cfile = COBJ.load(self._config_file_path, True)
    cfile['name'] = self.name
    cfile['path'] = self.path
    cfile['folders'] = self.folders
    cfile['data'] = self.data
    cfile.save()

  def create(self):
    # create config file for project
    self.save()

    # build child folders
    self.build()

    # save config file



  def removeFolder(self, name):
    if name.lower() in self._folders:
      raise Exception("This is a special folder required by this program, " \
        "and thus can not be removed.")
    else:
      pass
      # TODO - allow user to remove folders

  def addFolder(self, name, path):
    if name in self.folders:
      print("This folder name already exists: %s" % name)
    else:
      success = False
      if os.path.exists(path):
        print("this folder path already exists: %s" % path)
        success = True
      else:
        try:
          os.mkdir(path, 0777)
        except (OSError, IOError) as e:
          print("an error occured when attempting to create folder: %s" % path)
          print(e)
        else:
          success = True

      if success:
        self._folders.append(name)

  def saveData(self):
    if not self.name or not self.path:
      raise Exception("Cannot save, no path to save to.")
    else:
      self.save()

  def __str__(self):
    return str(self.name)

  def build(self):
    self.addFolder('to_keep',
      os.path.abspath(os.path.join(self.path, 'to-keep')))
    
    self.addFolder('to_remove',
      os.path.abspath( os.path.join(self.path, 'to-remove')))

    self.addFolder('to_review',
      os.path.abspath( os.path.join(self.path, 'to-review')))

    self.addFolder('other',
      os.path.abspath( os.path.join(self.path, 'other')))

