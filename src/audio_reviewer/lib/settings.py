
import os, sys

#sys.path.append(os.path.dirname(__file__))
import configobj as COBJ

__all__ = ['DEFAULT_OPTIONS',
  '_program_foundation', '_program_base', '_program_name',
  'homedir', 'is_root', 'config_dir', 'config_file_path', 'log_file_path']

DEFAULT_OPTIONS = dict(
  project_name=None,
  project_path=None,
  last_projects=[],
  show_debug_frame = False,
  debug_level = 'debug',
  verbosity=0
)

_program_foundation = 'PyTis'
_program_base = 'AudioReviewer'
_program_name = 'audio_reviewer'

# _program_name = os.path.basename(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# /home/jlee/github/audio_reviewer/src/audio_reviewer/lib/settings.ini
# __file__ = settings.ini
# abspath(__file__) = /home/jlee/github/audio_reviewer/src/audio_reviewer/lib/settings.ini
# dirname(__file__) = ../src/audio_reviewer/lib/
# dirname(lib) = /home/jlee/github/audio_reviewer/src/audio_reviewer/
# basename = audio_reviewer
# thus, audio_reviewer, why not just hard code this?  why all of the
# basename(dirname(dirname(abspath( bullshit? I guess sometimes when you code
# until 6am, it can show.

def add_os_touch():
  if not getattr(os,'touch',None):
    if sys.version_info >= (3, 3) and sys.version_info < (3,6):
      def touch(fname, *largs,**kwargs):
#        if os.path.isfile(fname) and os.path.exists(fname): return False
        open(fname, 'w+').close()
        return True

    elif sys.version_info >=(3, 3):
      def touch(fname, mode=0o666, dir_fd=None, **kwargs):
        if os.path.isfile(fname) and os.path.exists(fname):
          return False
        flags = os.O_CREAT | os.O_APPEND
        with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
          os.utime(f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd, **kwargs)
        return True

    else:
      def touch(fname, times=None):
#        if os.path.isfile(fname) and os.path.exists(fname): return False
        with file(fname, 'a'):
          os.utime(fname, times)
        return True
    os.touch = touch
add_os_touch()

def homedir():
  """ Get Home directory path in Python for Windows and Linux
  """
  #homedir = os.path.expanduser('~')
  # ...works on at least windows and linux. 
  # In windows it points to the user's folder 
  #  (the one directly under Documents and Settings, not My Documents)
  # In windows, you can choose to care about local versus roaming profiles.
  # You can fetch the current user's through PyWin32.
  #
  # For example, to ask for the roaming 'Application Data' directory:
  #  (CSIDL_APPDATA asks for the roaming, CSIDL_LOCAL_APPDATA for the local one)
  #  (See microsoft references for further CSIDL constants)
  try:
    from win32com.shell import shellcon, shell
    homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
  except ImportError: # quick semi-nasty fallback for non-windows/win32com case
    homedir = os.path.expanduser("~")
  return homedir

def is_root():
  import getpass
  if sys.platform in ('win32', 'win64'):
    return bool(getpass.getuser()=='Administrator')
  else:
    return bool(getpass.getuser()=='root')

def config_dir():
  global _program_foundation, _program_base
  import getpass
  if sys.platform in ('win32', 'win64'):
    if is_root():
      cdir = os.path.abspath(os.path.dirname(sys.argv[0]))
    else:
      cdir = os.path.join(homedir(), _program_foundation, _program_base)

  else: # LINUX
    if is_root():
      cdir = os.path.join('/etc', _program_foundation, _program_base)
    else:
      cdir = os.path.join(homedir(), '.config/', _program_foundation,
        _program_base)

  return os.path.abspath(cdir)

def log_file_path():
  global _program_name
  import errors
#  cfn = "%s.dat" % os.path.splitext(os.path.basename(sys.argv[0]) )[0]
  cfn = "%s.log" % _program_name

  if not os.path.exists(config_dir()):
    os.makedirs(config_dir())

  config_file = os.path.abspath(os.path.join(config_dir(), cfn))

  if not os.touch(config_file):
    config_file = os.path.abspath(os.path.join(homedir(), cfn))
    if not os.touch(config_file):
      raise errors.PermissionError('Cannot touch "%s"' % config_file)

  other_possible = \
  os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
    cfn))
#  print('other possible is: %s' % other_possible)
  if os.path.exists(other_possible):
#    print("log_file_path() returning: %s" % other_possible)
    return other_possible
  else:
#    print("log_file_path() returning: %s" % config_file)
    return config_file

def config_file_path():
  global _program_name
  import errors
#  cfn = "%s.dat" % os.path.splitext(os.path.basename(sys.argv[0]) )[0]
  cfn = "%s.dat" % _program_name

  if not os.path.exists(config_dir()):
    os.makedirs(config_dir())

  config_file = os.path.abspath(os.path.join(config_dir(), cfn))

  if not os.touch(config_file):
    config_file = os.path.abspath(os.path.join(homedir(), cfn))
    if not os.touch(config_file):
      raise errors.PermissionError('Cannot touch "%s"' % config_file)

  other_possible = \
  os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])),
    cfn))
#  print('other possible is: %s' % other_possible)
  if os.path.exists(other_possible):
#    print("config_file_path() returning: %s" % other_possible)
    return other_possible
  else:
#    print("config_file_path() returning: %s" % config_file)
    return config_file

CONFIG = COBJ.load(config_file_path(), True)

try:
  CONFIG.project_name
except AttributeError:
  CONFIG.update(DEFAULT_OPTIONS)


