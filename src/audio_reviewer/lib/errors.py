#!/usr/bin/python
# encoding=utf-8
"""
Universal Errors Module

So Far we have:
  Function: Die

Exceptions: 
  User Warnings:
    FileExists, DuplicateCopyright, FileNotFound, InvalidInput, InputError

  Error (Exception) Classes:
    DieNow, NoFiles, QuitNow, IdiotError, EmptyString, FutureFeature, APIError
    ProgrammerError, ConfigurationError

    *NOTE: PermissionError is added to Python < 3.0

  Exception FileNotFound Classes:
    EmptyTemplate

"""
# =============================================================================
# Begin Imports
# -----------------------------------------------------------------------------
# builtin
try:
  import sys
except KeyboardInterrupt as e:
  # Depending on what OS you run this on, I've learned you need to do this.
  # On CYGWIN I can cause a cygwin segfault, thus a blue-screen on my Winblows
  # laptop, simply by pressing CTRL+C if this file is being interpreted into
  # scope as I press CTRL+C, UNLESS, I do this.  Therefore, for windows users
  # like me, this MUST STAY HERE!
  print("KeyboardInterrupt: %s" % str(repr(e)))
  print("Script terminated by Control-C")
  print("bye!")
  exit(1)

import atexit, os
# Now this path manipulation is done sothat I can run errors.py from within
# CSISUTILS to see the auto-generated pydoc output.
sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath( \
  os.path.dirname(os.path.normpath(__file__))))))

# ########
# Internal

# ###########
# Third-Party


# -----------------------------------------------------------------------------
# End Imports
# =============================================================================
# =============================================================================
# Begin VARIABLE DEFINITIONS (XXX-vars)
# -----------------------------------------------------------------------------

__all__ = ['Die', 'DieNow', 'NoFiles', 'QuitNow', 'IdiotError', 'FileExists',
  'EmptyString', 'FileNotFound', 'InvalidInput', 'InputError', 'FutureFeature',
  'EmptyTemplate', 'ProgrammerError', 'ConfigurationError',
  'DuplicateCopyright', 'IdiotError', 'APIError']

if float("%s.%s"%(sys.version_info.major,sys.version_info.minor)) < 3.0:
  __all__.append('PermissionError')


# -----------------------------------------------------------------------------
# End VARIABLE DEFINITIONS
# =============================================================================
# =============================================================================
# Begin HELPER Functions
# -----------------------------------------------------------------------------

def Die(m=None):
  atexit._clear()
  sys.stderr.write('='*80); sys.stderr.write("\n")
  sys.stderr.write('='*80); sys.stderr.write("\n")
  sys.stderr.write("TYPE OF INPUT: %s\n" % type(m))
  sys.stderr.write('INPUT FOLLOWS:\n');
  sys.stderr.write('-'*80); sys.stderr.write("\n")

  if type(m) is type(''): sys.stderr.write(str(m))
  else: sys.stderr.write(repr(m))

  sys.stderr.write("\n")
  sys.stderr.write('='*80); sys.stderr.write("\n")
  sys.stderr.write('='*80); sys.stderr.write("\n")
  sys.stderr.write('='*80); sys.stderr.write("\n")

  sys.stderr.flush()
  sys.exit(1)

# -----------------------------------------------------------------------------
# End HELPER Functions
# =============================================================================

# =============================================================================
# Begin Class Helpers
# -----------------------------------------------------------------------------
class DieNow(Exception): # Egregious Error has occured, must exit now.
  def __init__(self, e, *args, **kwargs):
    Exception.__init__(self, e, *args, **kwargs)
    sys.stderr.write('='*80); sys.stderr.write("\n")
    sys.stderr.write("EGREGIOS FATAL ERROR!\n")
    sys.stderr.write('='*80); sys.stderr.write("\n")
    sys.stderr.flush()
    Die(e)
    sys.exit(1)

if float("%s.%s"%(sys.version_info.major,sys.version_info.minor)) < 3.0:
  class PermissionError(Exception): pass

class FileExists(UserWarning): pass
class DuplicateCopyright(UserWarning): pass
class FileNotFound(UserWarning): pass
class EmptyTemplate(FileNotFound): pass

class InvalidInput(UserWarning): pass
InputError=InvalidInput
class NoFiles(Exception): pass
class QuitNow(Exception): pass
class IdiotError(Exception): pass
class FutureFeature(Exception): pass
class EmptyString(Exception): pass
class ProgrammerError(Exception): pass
class IdiotError(Exception): pass # (as a joke)
class APIError(Exception): pass
class ConfigurationError(Exception): pass

# -----------------------------------------------------------------------------
# End Class Helpers
# =============================================================================


# -----------------------------------------------------------------------------
# Begin MAIN 
# -----------------------------------------------------------------------------
def main():
  try:
    import pydoc
    pydoc.doc(os.path.basename(__file__).split('.')[0])
  except:
    print(__doc__)
    return 1
  else:
    return 0

# -----------------------------------------------------------------------------
# End MAIN 
# =============================================================================

if __name__ == '__main__':
  sys.exit(main())

