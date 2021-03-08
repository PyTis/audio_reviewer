
import os
import configobj as COBJ

class Project(COBJ.ConfigObj):
  _name=None
  _path=None
  _folders = ['to-keep', 'to-review', 'to-remove']

  def __init__(self, pname=None, path=None):

    if pname: self.pname=pname
    if path: self.path=path
    
    COBJ.ConfigObj.__init__(self, self._config_file_path())

    if pname: self.pname=pname
    if path: self.path=path


  def _config_file_path(self):
    if not self.path:
      return None
    return os.path.abspath(os.path.join(self.path, 'data.ini'))

  def load(self):
    COBJ.ConfigObj.__init__(self, self.path)
    self.pname = self['pname']
    self.path = self['path']
    self.folders=self['folders']


  def create_config(self):
    cfile = COBJ.load(self._config_file_path(), True)
    print('create_config called')
    cfile['pname'] = self.pname
    print('pname set to', self.pname)
    cfile['path'] = self.path
    print('path set to', self.path)
    cfile['folders'] = self.folders
    print('about to call save')

    print(cfile)

    cfile.save()


  def create(self):
    # create config file for project
    self.create_config()

    # build child folders
    self.build()

    # save config file

  def set_folders(self,n):
    self._folders=n
  def get_folders(self):
    return self._folders
  folders=property(get_folders, set_folders)

  def set_path(self,p):
    self._path=p
  def get_path(self):
    return self._path
  path=property(get_path, set_path)

  def set_name(self,n):
    self._name=n
  def get_name(self):
    return self._name
  pname=property(get_name, set_name)

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
    if not self.pname or not self.path:
      raise Exception("Cannot save, no path to save to.")
    else:
      self.save()

  def __str__(self):
    return str(self.pname)

  def build(self):
    self.addFolder('to_keep',
      os.path.abspath(os.path.join(self.path, 'to-keep')))
    
    self.addFolder('to_remove',
      os.path.abspath( os.path.join(self.path, 'to-remove')))

    self.addFolder('to_review',
      os.path.abspath( os.path.join(self.path, 'to-review')))

