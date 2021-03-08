#!/usr/bin/python
# encoding=ISO-8859-1
import wx
from gui.main_frame import MainFrame
import test



class MyApp(wx.App):
  def OnInit(self):
    wx.SystemOptions.SetOptionInt("mac.window-plain-transition", 1)
    self.SetAppName("wxPyDemo")

    # Create and show the splash screen.  It will then create and
    # show the main frame when it is time to do so.  Normally when
    # using a SplashScreen you would create it, show it and then
    # continue on with the applicaiton's initialization, finally
    # creating and showing the main application window(s).  In
    # this case we have nothing else to do so we'll delay showing
    # the main frame until later (see ShowMain above) so the users
    # can see the SplashScreen effect.

    #splash = MySplashScreen()
    #splash.Show()

    return True

    app = wx.App()

app = MyApp(False)

f = MainFrame(None, "Audio Reviewer -  :: 2004-2020 (c) PyTis, LLC.")
f.Show()
#f.MainLoop()

app.MainLoop()

