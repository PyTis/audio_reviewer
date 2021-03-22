
import os
import configobj as COBJ

class NullDefault:
  pass

class Project(object):
  _dict=None
  _name=None
  _path=None
  path = None
  _folders = ['to-keep', 'to-review', 'to-remove', 'other']

  def set_folders(self,folders):
    self._folders=folders
  def get_folders(self):
    return self._folders
  folders=property(get_folders, set_folders)

  """
  def set_path(self,path):
    self._path=path
  def get_path(self):
    return self._path
  path=property(get_path, set_path)
  """

  def set_name(self,name):
    self._name=name
  def get_name(self):
    return self._name
  name=property(get_name, set_name)

  def set_dict(self,dict):
    self._dict=dict
  def get_dict(self):
    return self._dict
  dict=property(get_dict, set_dict)

# --------------------------------------------------------------------------- #

  def __init__(self, name=None, path=None):
    
    if name: self.name=name
    if path: self.path=path
    
    self.dict = COBJ.ConfigObj(self._config_file_path())

    if self.dict.get('name'): self.name=self.dict.get('name')
    if self.dict.get('path'): self.path=self.dict.get('path')
    if self.dict.get('folders'): self.folders=self.dict.get('folders')

  # ------------------------------------------------------------------------- #

  def _config_file_path(self):
    if not self.path:
      return None
    return os.path.abspath(os.path.join(self.path, 'data.ini'))

  def load(self):
    self.dict = COBJ.ConfigObj(self.path)
    for k, v  in self.dict.items():
      self.__setattr__(k, v)

#    if self.dict.get('name'): self.name=self.dict.get('name')
#    if self.dict.get('path'): self.path=self.dict.get('path')
#    if self.dict.get('folders'): self.folders=self.dict.get('folders')


  def create_config(self):
    cfile = COBJ.load(self._config_file_path(), True)
    print('create_config called')
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
    self.create_config()

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

