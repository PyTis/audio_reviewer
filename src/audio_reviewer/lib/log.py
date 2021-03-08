
import logging, sys

from . import python_version
from .settings import _program_name, CONFIG, log_file_path
from .util import prettyNow

if python_version >= 3.0:
  from io import StringIO
else:
  from cStringIO import StringIO


import wx

class MyLog(wx.PyLog):
  def __init__(self, textCtrl, logTime=1):
    global _program_name, log

    wx.PyLog.__init__(self)
    self.tc = textCtrl
    self.logTime = logTime
    self.log = log
    
  def DoLogText(self, message):
    if self.tc:
      self.tc.AppendText(message[10:] + '\n')
    '''
    global log
    if log.use_timestamps:
      if self.tc:
        self.tc.AppendText(message + '\n')
    else:
      if self.tc:
        self.tc.AppendText(message[10:] + '\n')
    '''

# ============================================================================#
class NullLogHandler(logging.Handler):
  def emit(self, record): pass

# ============================================================================#
class MyLogger(logging.Logger):

  '''
  _use_timestamps = True
  def set_use_timestamps(self, b):
    self._use_timestamps = b
    
    datefmt="%Y%m%d %H:%M:%S"
    if self.level <= 10:
      fmt='%(asctime)s.%(msecs)03d %(name)-10s %(levelname)-8s [PID: %(process)d]  %(message)s'
    elif self.level <= 20:
      fmt='%(name)-10s %(levelname)-8s  %(message)s'
    #elf self.level < 20:
    else:
      fmt='%(levelname)-8s  %(message)s'
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(fmt, datefmt))

  def get_use_timestamps(self):
    return self._use_timestamps
  use_timestamps = property(get_use_timestamps, set_use_timestamps)
  '''

  # 0,1,2,3,4:0=quiet,1=verbose,2=more verbose,3=most verbose,4=debug & verbose
  verbosity = 0

  had_error = False
  had_warning = False
  paused = False

#  def Pause(self):
#    return self.pause()

  def pause(self):
    self.paused = True
  Pause=pause

  def unPause(self):
    self.paused = False

  @property
  def hadWarning(self):
    return self.had_warning
  # setting an Alias
  hadWarnings=hadWarning


  '''
  def debug
  def info
  def warn
  def error
  def critical
  def fatal
  '''

  @property
  def hadError(self):
    return self.had_error
  # setting an Alias
  hadErrors=hadError

  @property
  def isCompiled(self):
    """
    returns boolean true if it is running from an EXE, else, returns FALSE if
    it is running from a python file via command line execution.
    """
    if str(sys.argv[0]).endswith('.py') or \
      str(sys.argv[0]).endswith('.pyc') or \
      str(sys.argv[0]).endswith('.pyw') or \
      str(sys.argv[0]).startswith('python'):
      return False
    return True


  def prnt(self, string):
    if not self.isCompiled:
      print(string)
    else:
      pass

  def debug(self, msg, *args, **kwargs):
    if self.verbosity > 4:
      self.prnt( msg)
    return logging.Logger.debug(self, msg, *args, **kwargs)
    
  def info(self, msg, *args, **kwargs):
    if self.verbosity >= 1:
      self.prnt(msg)
    return logging.Logger.info(self, msg, *args, **kwargs)

  # - ------------------------------------------------------
  def info1(self, msg, *args, **kwargs):
    if self.verbosity >= 1:
      self.prnt(msg)
      return logging.Logger.info(self, msg, *args, **kwargs)

  def info2(self, msg, *args, **kwargs):
    if self.verbosity >= 2:
      self.prnt(msg)
      return logging.Logger.info(self, msg, *args, **kwargs)

  def info3(self, msg, *args, **kwargs):
    if self.verbosity >= 3:
      self.prnt(msg)
      return logging.Logger.info(self, msg, *args, **kwargs)

  def info4(self, msg, *args, **kwargs):
    if self.verbosity >= 4:
      self.prnt(msg)
      return logging.Logger.info(self, msg, *args, **kwargs)
  # - ------------------------------------------------------

  def warn(self, msg, *args, **kwargs):
    logging.Logger.warn = logging.Logger.warning
    return self.warning(msg, *args, **kwargs)

  def warning(self, msg, *args, **kwargs):
    self.had_warning = True
    self.prnt('WARNING: %s' % str(msg))
    return logging.Logger.warning(self, msg, *args, **kwargs)

  def error(self, msg, *args, **kwargs):
    self.had_error = True

    sys.stderr.write("%s%s\n" % (('' if kwargs.get('exc_info',None) else \
      'ERROR: ') ,msg))

    return logging.Logger.error(self, msg, *args, **kwargs)

  def critical(self, msg, *args, **kwargs):
    self.had_error = True

    # if kwargs.get('exc_info',None): sys.stderr.write("%s\n" % msg)
    # else: sys.stderr.write("CRITICAL: %s\n" % msg)

    sys.stderr.write("%s%s\n" % (('' if kwargs.get('exc_info',None) else \
      'CRITICAL: ') ,msg))

    return logging.Logger.critical(self, msg, *args, **kwargs)

  def fatal(self, msg, *args, **kwargs):
    self.had_error = True

    #if kwargs.get('exc_info',None): sys.stderr.write("%s\n" % msg)
    #else: sys.stderr.write("FATAL: %s\n" % msg)

    sys.stderr.write("%s%s\n" % (('' if kwargs.get('exc_info',None) else \
      'FATAL: ') ,msg))

    logging.Logger.fatal(self, msg, *args, **kwargs)
    sys.exit(1)

  def _log(self, level, msg, args, exc_info=None):
    """
    Low-level logging routine which creates a LogRecord and then calls
    all the handlers of this logger to handle the record.
    """
    global python_version
    if self.paused:
      return

    if logging._srcfile:
      if python_version >= 3.0:
        fn, lno, func, stack_info  = self.findCaller()
      else:
        fn, lno, func  = self.findCaller()
    else:
      fn, lno, func = "(unknown file)", 0, "(unknown function)"

    if exc_info:
      if type(exc_info) != types.TupleType:
        exc_info = sys.exc_info()
    
    level_map = { 
      0 : 'ALL',
      10 : 'debug',
      20 : 'info4',
      23 : 'info3',
      24 : 'info2',
      26 : 'info1',
      28 : 'info',
      30 : 'warn',
      40 : 'error',
      50 : 'critcial'
    }

    if self.level < 20:
      wx.LogMessage("[%(level)s], %(fn)s %(lno)s - %(msg)s, %(args)s, " \
        "%(exc_info)s" % \
        dict(
          level=str(level_map[level]).upper(),
          name=self.name,
          fn=fn,
          lno=lno,
          msg=msg,
          args=args,
          exc_info=exc_info
          )
        )
    else:
      wx.LogMessage("[%(level)s], %(msg)s" % \
        dict(
          level=level_map[level],
          name=self.name,
          fn=fn,
          lno=lno,
          msg=msg,
          args=args,
          exc_info=exc_info
          )
        )

    record = self.makeRecord(self.name, level, fn, lno, msg, args, exc_info)
    self.handle(record)

  def addSeperator(self, sep='-'*80):
    wx.LogMessage(sep)
    h = open(log_file_path(), 'a+')
    h.write("%s\n" % sep)
    h.close()
    return


# ============================================================================#

def set_logging(name, debug=False):
  global log, python_version


  if debug:
    level=logging.DEBUG
  else: 
    level=logging.INFO

  if python_version >=3:
    logging.basicConfig( 
      filename=log_file_path(),
      level=level,
      format='%(asctime)s.%(msecs)03d %(name)-10s %(levelname)-8s ' \
        '[PID: %(process)d]  %(message)s',
      datefmt="%Y%m%d %H:%M:%S")
  else:
    logging.basicConfig(
      name=name,
      filename = log_file_path(),
      level=level,
      format='%(asctime)s.%(msecs)03d %(name)-10s %(levelname)-8s ' \
        '%(message)s',
      datefmt="%Y%m%d %H:%M:%S")

  logging.setLoggerClass(MyLogger)
  log = logging.getLogger(name)


  """
  # BEGIN TRICK
  # From here to the next comment is a trick to allow the log message to goto
  # only a log file, and not make it to the screen of a user.
  # we MIGHT be using this trick again, depends on the overall verbosity, look
  # further down this function for the next occurance of sys.stdout  
  buf = StringIO() 
  sys.stdout = buf
  log.info("STARTING: %s" % name)
  sys.stdout = sys.__stdout__
  del buf
  # END TRICK

    # we may be using this trick again, depends on the overall verbosity, look
  # further down this function for the next occurance of sys.stdout  
  buf = StringIO()
  sys.stdout = buf

  # and now we end our little second utilization of the output override trick.
  sys.stdout = sys.__stdout__
  del buf
  """

  return log

