"""
A simple script to encode all the images the ZPin needs into a Python module
"""
import sys, os, glob
import img2py

python_version = float("%s.%s"%(sys.version_info.major,sys.version_info.minor))
output = '../src/audio_reviewer/gui/images.py'

def main():
  global output
  doc = '''"""
  This file was auto-generated by compile-images.py in the
  res/images directory. 
  
  DO NOT MAKE CHANGES TO THIS FILE MANUALLY!
  If you do make changes, they will be overriden the next time
  someone runs compile-images.pty
"""

  '''
  # get the list of PNG files
  files = glob.glob('src-images/*.png')

  # get the list of JPEG files
  files.extend(glob.glob('src-images/*.jpg'))
  # get the list of ICON files
  files.extend(glob.glob('src-images/*.ico'))
  files.sort()
  # Truncate the inages module
  handle = open(output, 'w')
  #handle.write(doc)
  # call img2py on each file
  for file in files:
    # extract the basename to be used as the image name
    name = os.path.splitext(os.path.basename(file))[0]
    # encode it
    if file == files[0]:
      cmd = " -u -i -n %s %s %s" % (name, file, output)
    else:
      cmd = " -a -u -i -n %s %s %s" % (name, file, output)
    img2py.main(cmd.split())
  return files

def wrap(text, width=79):
  """
  A word-wrap function that preserves existing line breaks
  and most spaces in the text. Expects that existing line
  breaks are posix newlines (\n).
  """
  global python_version
  if python_version >= 3.0:
    return functools.reduce(lambda line, word, width=width: '%s%s%s' % (line,
    ' \n'[(len(line)-line.rfind('\n')-1 + len(word.split('\n',1)[0])>=width)],
    word), text.split(' '))
  else:
    return reduce(lambda line, word, width=width: '%s%s%s' % (line,
    ' \n'[(len(line)-line.rfind('\n')-1 + len(word.split('\n',1)[0])>=width)],
    word), text.split(' '))

def doRep(files):
  global output
  
  all = []
  for file in files:
    name = os.path.basename(file).split('.')[0]
    
    all.append("get%sData" % name)
    all.append("get%sBitmap" % name)
    all.append("get%sImage" % name)
    all.append("get%sIcon" % name)
  
  h = open(output, 'r')
  lines = h.readlines(-1)
  h.close()
  h =  open(output, 'w')
  h.write("# This file was generated by encoding_bitmaps.py\n")
  h.write("#----------------------------------------------------------------------\n")
  h.write("# ALL functions auto-created are as follows:\n")
  
  xx = wrap(', '.join(all), 77).split("\n")
  print("len of xx is %s" % len(xx))
  for i, x in enumerate(xx):
    if i == 0:
      h.write("# all = %s\n" %  x)
    else:
      h.write("# %s\n" % x)

  for line in lines:
    h.write(line)
  h.close()

if __name__ == "__main__":
  files = main()
  doRep(files)
