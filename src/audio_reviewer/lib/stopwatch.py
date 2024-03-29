#!/usr/bin/python3
# encoding=utf-8
# ##############################################################################
# The contents of this file are subject to the PyTis Public License Version    #
# 2.0 (the "License"); you may not use this file except in compliance with     #
# the License. You may obtain a copy of the License at                         #
#                                                                              #
#     http://www.PyTis.com/License/                                            #
#                                                                              #
#     Copyright (c) 2009, 2014-2019 Josh Lee                                   #
#                                                                              #
# Software distributed under the License is distributed on an "AS IS" basis,   #
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License     #
# for the specific language governing rights and limitations under the         #
# License.                                                                     #
#                                                                              #
# @auto-generated by the PyTis Copyright Tool on 11:55 PM - 06 Feb, 2019       #
############################################################################## #
""" This is a simple class that is used to time how long commands take to run.

EXAMPLE CODE:

  #############################################################################
  # Passing True into the constructor, tells the stopwatch to reset it's timer
  # each and every time it is used/called.
  s=StopWatch(True)

  print("DynamoDB cleanup is now running %s " % \\
    datetime.datetime.now().strftime("%I:%M%%s %m %b, %Y") % \\
    datetime.datetime.now().strftime("%p").lower())
  sts_session, dynamo_client = gather_resources(account_number, region, s)
  print("obtaining dynamodb client - %s" % s)
  dynamo_client = sts_session.client('dynamodb')
  print("deleting resource dynamodb table: '%s' - %s" % (table_name, s))
  dynamo_client.delete_table(TableName=table_name)
  print('please wait (up to 2 minutes) - ', s)
  oops_count = 0
  while does_it_still_exist(dynamo_client, table_name, s) == True:
    sys.stdout.write('.')
    time.sleep(1)
    oops_count+=1
    if oops_count > 120:
      break
    sys.stdout.flush()
  sys.stdout.flush()
  print("\\ntable %s has been deleted - ( it took %s) " % (table_name, s))

EXAMPLE OUTPUT:
->./cleanup.py
  DynamoDB cleanup is now running 12:46pm 02 Feb, 2020
  creating STS connection
  STS connection created - 0.304 seconds
  obtaining dynamodb client -  27.22024918 miliseconds OR 0.0272 seconds
  obtaining dynamodb client - 0.0001 Âµ microseconds
  deleting resource dynamodb table: 'test_users' - 3.63469124 miliseconds OR
  0.0036 seconds
  please wait (up to 2 minutes) -  0.214 seconds
  ...........................................................
  table test_users has been deleted - ( it took 60.9334 seconds)

  #############################################################################
  # Passing True into the second argument of the constructor, tells the primary
  # stopwatch to have a child stopwatch, this is used to track total time.

  EXAMPLE OF REMEDIATION BOOTSTRAP:
  import stopwatch

  stopwatch=StopWatch(True, True)
  stopwatch.setDefaultPrefixes()
  
  Output from a child instance of AWSLambda has the following output (small
  snippet).

EXAMPLE OUTPUT:
 --> ./bootstrap.py -v -d
AwsLambda.__init__() called || Time elapsed since last call 209.5699 Âµ microseconds || Total Time 209.3315 Âµ microseconds
GlueBootstrap bootstraper is now running for account: 084135731370 at 10:56 PM on Nov 3, 2020
AwsLambda.run() called || Time elapsed since last call 0.3243 seconds || Total Time 0.3245 seconds
GlueBootstrap.Run() called || Time elapsed since last call 44.5843 Âµ microseconds || Total Time 0.3246 seconds
GlueBootstrap.Clean() called || Time elapsed since last call 25.7492 Âµ microseconds || Total Time 0.3246 seconds
GlueBootstrap.cleanGlue() called || Time elapsed since last call 20.9808 Âµ microseconds || Total Time 0.3246 seconds
GlueBootstrap.cleanDatabase() called || Time elapsed since last call 28.1334 Âµ microseconds || Total Time 0.3246 seconds
GlueBootstrap.cleanCrawler() called || Time elapsed since last call 18.3582 Âµ microseconds || Total Time 0.3247 seconds
GlueBootstrap.cleanJob() called || Time elapsed since last call 17.4046 Âµ microseconds || Total Time 0.3247 seconds
GlueBootstrap.cleanConnection() called || Time elapsed since last call 16.6893 Âµ microseconds || Total Time 0.3247 seconds
AwsLambda.closingDown() called || Time elapsed since last call 0.3242 seconds || Total Time 0.5621 seconds
AwsLambda.printExit() called || Time elapsed since last call 48.399 Âµ microseconds || Total Time 0.5621 seconds

  # As seen above, by passing a second "True" into the constructor, we get a
  # second stopwatch, allowing us to also track the total time.


"""
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
import time
# builtin continued,...
import os

# Now this path manipulation is done sothat I can run stopwatch.py from
# within CSISUTILS to see the auto-generated pydoc output.
sys.path.append(os.path.realpath(os.path.dirname(os.path.normpath(__file__))))

sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath( \
  os.path.dirname(os.path.normpath(__file__))))))

import errors as errors

__all__ = ('StopWatch','Stopwatch', 'stopwatch')

# copied from my  (PyTis) library, slightly modified for Verizon Wireless.
__copyright__ = 'PyTis.com'
__author__ = 'Josh Lee'
__created__ = '06:14pm 09 Sep, 2009'
__version__ = 1.2


# Copied from my personal coding library.
class StopWatch():
  """
  Refer to __init__ for more documentation.
  """
  # the exact time this class was initialized, or time since reset was called.
  t = 0
  # there is a way to pause this, I don't know why I coded it, I'm not going
  # any further (adding in start, restart, etc.).
  _stopped=False
  # do you want this to show the total time since initialized, or since last
  # used?  If since last used, then pass True into the instance as you
  # initialize it.
  reset_each_call=False

  # decimals is used when formatting the output to be more "human-readable"
  _decimals=4

  _advanced_mode = False
  StopWatch = None
  parent = False

  # displayed before time is output
  _prefix = '|| '

  def __init__(self, reset_each_call=False, advanced_mode=False):
    """

    The intention is for this class's instance to be treated as almost a
    singleton.  Look closely at the internal methods that I am overridding.

    Args:
      reset_each_call (boolean) : Tells this class instnace if it should call
        self.reset() each time the instance is referenced, even printed (look
        at the self.__str__ and self.__repr__) as examples.

    Returns:
      None

    Example usage:
      sw = StopWatch()
      print(dosomething(), sw)
      print(dosomething_else(), sw)
      print(and_done(), sw)

    Example (copy/paste) of REAL output:

     --> ./dynamodb.py
 >> Event Id: 07c3cbee-ec83-4451-963c-d80d85000ef6...0.0 Âµ microseconds..
 >> DynamoDB auto remediation function has been called 0.0001 Âµ microseconds
 >> obtaining dynamodb client - 7.6639 seconds
 >> obtaining dynamodb resource - 23.67544174 miliseconds OR 0.0237 seconds
 >> grabbing 'test_users' to read - 14.90569115 miliseconds OR 0.0149 seconds
 >> dynamodb.Table(name='test_users')
 >> describing table 'test_users' - 2.56061554 miliseconds OR 0.0026 seconds


    """
    self.t=time.time()
    self.reset_each_call=reset_each_call
    self.setAdvancedMode(advanced_mode)

  @property
  def hasParent(self):
    return self.parent

  def setAdvancedMode(self,bol):
    """
    Show two timers
    """
    self._advanced_mode = bol
    if bool(self._advanced_mode) and not self.hasParent:
      self.StopWatch = StopWatch(False)
      self.StopWatch.parent=True
      self.reset_each_call = True

  def getAdvancedMode(self):
    return self._advanced_mode

  def __call__(self):
    """
    Returns the time passed thusfar.
    """
    return self.read()

  def __str__(self):
    """
    Print the time as a string (human readable / formatted)
    """
    return self.beautify(self.read())

  def __repr__(self):
    """
    Print the time as a string (unformatted)
    """
    return str( self.read()  )

  def __ne__(self, other):
    return float(self.read()) != float(other)

  def __eq__(self, other):
    return float(self.read()) == float(other)

  def __le__(self, other):
    return float(self.read()) <= float(other)

  def __lt__(self, other):
    return float(self.read()) < float(other)

  def __ge__(self, other):
    return float(self.read()) >= float(other)

  def __gt__(self, other):
    return float(self.read()) > float(other)

  def read(self):
    """
    Calculate the current value from the timer, then reset the timer if the
    reset_each_call option is selected. 
    """
    if self._stopped:
      return self.t
    else:
      if self.reset_each_call: 
        r=(time.time()-self.t)
        self.reset()
        return r
      return (time.time()-self.t)

  def reset(self):
    """
    pretty self explanitory here.
    we evaluate how much time has been tracked, then reset the timmer it is
    running again.
    """
    self.t=time.time()
    self._stopped=False

  def stop(self):
    """
    pretty self explanitory here.
    we evaluate how much time has been tracked, then tell the timmer it is
    stopped.
    """
    self.t=time.time()-self.t
    self._stopped=True

  def beautify(self, t):
    if self.getAdvancedMode():
      return self.fullBeauty(t, self.StopWatch.read())
    else:
      return self.singleBeauty(t)
    
  def fullBeauty(self, t, tt):
    """
      Display both clocks/timers.
      Time since last call || Total time since object was instantiated.
    """
    return "%s%s" % ( self.singleBeauty(t), self.StopWatch.singleBeauty(tt) )

  def singleBeauty(self, t):
    """
    Args:
      t (float) : float representation of time.time instnace value

    Returns:
      Human readable value of time tracked.

    Make the output human friendly / readable.  
    Examples of Output:
      > 14.8730278 miliseconds OR 0.0149 seconds
      > 24.6193409 miliseconds OR 0.0246 seconds
      > 16.13354683 miliseconds OR 0.0161 seconds
      > 0.2569 seconds
      > 20.0882 seconds
    """
    t=float(t)
    # IF t is greater than 1 tenth of a second.
    if t > 0.1: 
      return "%s%s seconds" % (self.prefix, round(t, self.decimals))

    # IF t is greater than 1 thousandth of a second.
    elif t >= 0.001:
      # IF t is exactly 1 thousandth of a second, no plural label
      if float(t) == float(0.001): label = ''
      # else set label to a plural s
      else: label = 's'
      
      return "%s%s milisecond%s OR %s seconds" % (self.prefix,
        round(1000*t, self.decimals),
        label, str(round(t, self.decimals)) )

    # IF t is greater than 1 milionth of a second.
    elif t >= 0.000001:
      if float(t) == float(0.000001): label = " Âµs microsecd"
      else: label = 'Âµ microseconds'
      return "%s%s %s" % (self.prefix, round(1000000*t, self.decimals), label)
    else:
      return "%s%s seconds" % (self.prefix, round(t, self.decimals))

  def clearPrefixes(self):
    self.prefix = '|| '
    if self.StopWatch:
      self.StopWatch.prefix = '|| '

  def setDefaultPrefixes(self):
    self.prefix = '|| Time elapsed since last call ' # 'Elapsed'
    if self.StopWatch:
      self.StopWatch.prefix = ' || Total Time '

  def set_prefix(self, prefix):
    self._prefix = prefix
  def get_prefix(self):
    return self._prefix
  prefix=property(get_prefix, set_prefix)

  def setDefaultDecimals(self):
    self.setDecimals(4)
    
  def set_decimals(self, decimals):
    self._decimals = decimals
  def get_decimals(self):
    """
    The unique IF statement, where decimals is set to None, is because 
    round( float(0.222) , 0 ) returns 0.2 instead of 0
    Apparently, even though logic would dictate that 0 would mean Zero digits, 
    the only way to display NO digits after the decimal is to set decimals to
    None.
    """
    if not self._decimals and self._decimals == 0: self.decimals = None
    return self._decimals
  decimals=property(get_decimals, set_decimals)

  def setChildDecimals(self, decimals):
    if self.StopWatch:
      self.StopWatch.decimals = decimals
    else:
      raise errors.ProgrammerError('There is not a child StopWatch object ' \
        'to set decimals on.')

  def setDecimals(self, decimals):
    """ 
    This can be called to set the decimal places to be used in all cases
    (parent and child) or, you can utilize them individually.
    """
    self.decimals=decimals
    if self.StopWatch:
      self.StopWatch.decimals=decimals

Stopwatch=StopWatch
# singleton
stopwatch=StopWatch(True, True)
stopwatch.setDefaultPrefixes()

if __name__ == '__main__':
  import pydoc, sys
  pydoc.doc('stopwatch')
  sys.exit(0)

