#!/usr/bin/python3
# encoding=ISO-8859-1
# ##############################################################################
# The contents of this file are subject to the PyTis Public License Version    #
# 3.0 (the "License"); you may not use this file except in compliance with     #
# the License. You may obtain a copy of the License at                         #
#                                                                              #
#     http://www.PyTis.com/License/                                            #
#                                                                              #
#     Copyright © 2021 Josh Lee                                                #
#                                                                              #
# Software distributed under the License is distributed on an "AS IS" basis,   #
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License     #
# for the specific language governing rights and limitations under the         #
# License.                                                                     #
#                                                                              #
# @auto-generated by the PyTis Copyright Tool on 07:16 PM - 07 Jan, 2021       #
############################################################################## #

import readline, sys

__all__ = ['multiline_input']

def showhelp():
  print("="*80)
  print("*** Please note, for input with multi-line default values,... ")
  print("You may navigate with the LEFT and RIGHT arrows, and the HOME and END keys.")
  print("-"*80)

def do(prompt=''):
  data = []
  i=0

  while True:
    if i > 0:
      readline.set_startup_hook(lambda: readline.insert_text(''))
    i+=1
    s = input() 
    if s == '\n' or not s.strip():
      break
    else:
      data.append(s)
  return "\n".join(data)

def multiline_input(prompt='', default=''):
  if ("\n" in default):
    showhelp()
  
  sys.stdout.write(prompt)
  readline.set_startup_hook(lambda: readline.insert_text(default))

  try:
    response = do(prompt)
  finally:
    readline.set_startup_hook(None)
  return response

def main():
  data = multiline_input('Summary: ', 'default')
  print("SUMMARY FOLLOWS:")
  print(data)

  default_test = """First line
  second line"""
  data = multiline_input(default=default_test) 
  print("INPUT FOLLOWS:")
  print(data)
  return 0

if __name__ == '__main__':
  sys.exit(main())