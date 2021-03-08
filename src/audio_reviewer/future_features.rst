PyTis Audio Reviewer
====================

Features for other versions.
----------------------------


* Add Local (multi-lingual support).

* Allow the user to add their own Categories, adding folders that they can sort
audio files into.

* Add Checkboxes next to audio files, for bulk moving / sorting

* Add the ability to rename a file.

* In the program settings, there could be a checkbox that basically says
"Automatically open last project when program starts"


Bugs / Known Issues
-------------------

#1 I am using Window splitters, to allow for resizing, however, I do not want
the bottom panel (Audio/Media player) to be able to be adjusted in height.
What would be best, is if wx.NO_RESIZE actually worked in the style set for the
MediaPanel.  I tried to set it within it's INIT and as a style when adding the
sizer, but neither seemed to work.

TODO
----

I need to try to remove the requirement for my PyTis lib.  I'd like to have the
least requirements possible.

Bind Shortcuts CTRL+N, CTRL+S, CTRL+F4, etc.  Notice that the wxPythonDemo
under Book Controls, Flat Notebook, the menu has Shortcuts in it.  I do not
know how they are binding the hotkeys to actions, but have found a solution
with :
https://discuss.wxpython.org/t/action-on-ctrl-enter-in-wx-textctrl-in-msw/29217/6


  def OnKeyDown(self, event):
    keycode = event.GetKeyCode ( )
    controlDown = event.CmdDown ( )
    altDown = event.AltDown ( )
    shiftDown = event.ShiftDown ( )

    if keycode == wx.WXK_RETURN:
      if  (userSettings.CtrlEnter.ischecked() and controlDown) or
          (not userSettings.CtrlEnter.ischecked() and not controlDown):

        doStuff()
        return   # eat keystroke

    # pass all other keys
