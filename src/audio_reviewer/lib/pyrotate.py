#!/usr/bin/python3
"""pyrotate
========
Manually shifts a log file, moving each one back a log number.
"""

try:
  import gzip
except:
  gzip = None

import optparse
import shutil
import os
import glob
import sys


__curdir__ = os.path.abspath(os.path.dirname(__file__))
__created__ = '06:27pm 05 May, 2016'
__author__ = 'Josh Lee'
__copyright__ = 'PyTis.com'
__version__ = '1.5'

def run(args, log):
  """pyrotate run doc help"""

  for path in args:
    base = os.path.basename(path)
    fpath = os.path.abspath(path)
    stat_info = os.stat(fpath)

    # skip rotating this empty file
    fsize = stat_info.st_size
    if not fsize or fsize == 0:
      log.debug('skipping, NOT rotating EMPTY file: "%s"' % fpath)
      continue # continue=skip


    logmode = oct(os.stat(fpath).st_mode & 0o777)
    log.debug('logmode: %s' % str(logmode))

    mode = os.stat(fpath).st_mode
    log.debug('mode: %s' % str(mode))

    matches = glob.glob("%s*" % fpath)
    matches.sort()
    log.debug("MATCHES: %s" % repr(matches))
    while len(matches)>0:
      movefrom = str(matches.pop())

      number = movefrom.replace(fpath,'').replace('.gz','').replace('.','')
      next_number = None
      if number:
        next_number = str(int(number)+1)
      moveto = '%s.%s.gz' % (base, next_number)  

      if number and int(number) > 1:
        log.debug('move: %s to: %s' % (movefrom, moveto))
        shutil.move(movefrom, moveto)
        log.debug("chmod'ed: %s to %s" % (moveto,logmode))
        os.chmod(moveto, mode)
      elif number and int(number)==1:
        if gzip is None:
          log.debug('os.popen(command="gzip %s")' % movefrom)
          os.popen('gzip %s' % movefrom)
          log.debug('move: %s to: %s' % (movefrom, moveto))
          shutil.move('%s.gz' % movefrom, moveto)
        else:
          log.debug('gzip w/Python %s to: %s' % (movefrom, moveto))

          with open(movefrom, 'rb') as f_in, gzip.open(moveto, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        log.debug("chmod'ed: %s to %s" % (moveto, logmode))
        os.chmod(moveto, mode)

      else:
        log.debug("move: %s to: %s.1" % (movefrom, movefrom))
        shutil.move(movefrom, "%s.1" % movefrom)
        log.debug("chmod'ed: %s to %s" % ("%s.1" % movefrom, logmode))
        os.chmod("%s.1" % movefrom, mode)

    log.debug("truncate: %s" % fpath)

    handle = open(fpath,'wb')
    handle.truncate()
    handle.write(b'')
    handle.close()

    log.debug("chmod'ed: %s to %s" % (fpath, logmode))
    os.chmod(fpath, mode)

