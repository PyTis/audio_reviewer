PyTis Audio Reviewer
====================


Features for this version.
--------------------------

* When Summary has focus, catch TAB keypress, then enable Description (if
summary has value) and move focus there).

Features for other versions.
----------------------------


* Add Local (multi-lingual support).

* Allow the user to add their own Categories, adding folders that they can sort
audio files into.

* Add Checkboxes next to audio files, for bulk moving / sorting

* Add the ability to rename a file.

* In the program settings, there could be a checkbox that basically says
"Automatically open last project when program starts"

* Mute Functionality: I would like to change it so that Mute doesn't set the
volume to "0", just mutes (stops sound) by making it appear as if the volume
stayed, but it was muted.  Then, tbe user could adjust the volume down, then
unmute.  OR, turn the volume up, possibly immediately unmuting, or still
waiting for the user to unmute.  I'd like to try both ways out and see which
feels right.

* add actions menu, then add within it "move to KEEP", "move to REVIEW", "move
to REMOVE", and "move to OTHER" menu items, so that hot-keys can be binded, to
these actions.


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


More Windows/Controls wx.InfoBar
Show Error messages with the wx.InfoBar

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


        box = wx.StaticBox(self, -1, "This is a wx.StaticBox")
        bsizer = wx.StaticBoxSizer(box, wx.VERTICAL)

        t = wx.StaticText(self, -1, "Controls placed \"inside\" the box are really its siblings")
        bsizer.Add(t, 0, wx.TOP|wx.LEFT, 10)


        border = wx.BoxSizer()
        border.Add(bsizer, 1, wx.EXPAND|wx.ALL, 25)
        self.SetSizer(border)



https://github.com/Metallicow/wxPython-Sample-Apps-and-Demos/tree/master/111_Miscellaneous/DragScroller
