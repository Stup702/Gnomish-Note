#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

class HiddenAppWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Barebones Hidden App")
        self.set_default_size(300, 200)

        # Attempt to set the window hints to skip taskbar and pager
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        
        # We also set it to always be on top just for visibility in this test
        self.set_keep_above(True)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_top(20)
        box.set_margin_bottom(20)
        box.set_margin_start(20)
        box.set_margin_end(20)

        label = Gtk.Label(label="This window is trying to hide from Alt-Tab.\n\n"
                                "If you are on X11 (or running via XWayland), it is hidden.\n"
                                "If you are on native Wayland, GNOME ignores this hint.")
        label.set_line_wrap(True)
        box.pack_start(label, True, True, 0)

        button = Gtk.Button(label="Close")
        button.connect("clicked", self.on_close_clicked)
        box.pack_start(button, False, False, 0)

        self.add(box)

    def on_close_clicked(self, widget):
        Gtk.main_quit()

if __name__ == '__main__':
    win = HiddenAppWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
