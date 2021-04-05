
import os
import configobj as COBJ

acceptable_extensions = ['.midi', '.m4a', '.mp3', '.wav', '.wma']

class NullDefault:
  pass

class Project(object):
  """

  """
  _cfile=None
  _name=None
  _path=None
  path = None
  _folders = ['to-keep', 'to-review', 'to-remove', 'other']

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

  def set_name(self,name):
    self._name=name
  def get_name(self):
    return self._name
  name=property(get_name, set_name)

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
    
    self.cfile = COBJ.ConfigObj(self._config_file_path())

    if self.cfile.get('name'): self.name=self.cfile.get('name')
    if self.cfile.get('path'): self.path=self.cfile.get('path')
    if self.cfile.get('folders'): self.folders=self.cfile.get('folders')

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

  def _config_file_path(self):
    if not self.path:
      return None
    return os.path.abspath(os.path.join(self.path, 'data.ini'))

  def load(self):
    self.cfile = COBJ.ConfigObj(self.path)
    for k, v  in self.cfile.items():
      self.__setattr__(k, v)

#    if self.cfile.get('name'): self.name=self.cfile.get('name')
#    if self.cfile.get('path'): self.path=self.cfile.get('path')
#    if self.cfile.get('folders'): self.folders=self.cfile.get('folders')


  def save(self):
    cfile = COBJ.load(self._config_file_path(), True)
    print('save called')
    cfile['name'] = self.name
    print('name set to', self.name)
    cfile['path'] = self.path
    print('path set to', self.path)
    cfile['folders'] = self.folders
    print('about to call save')

    print(cfile)

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

