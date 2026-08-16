#!/usr/bin/env python3
import sys
import os
import fcntl
import signal
import atexit

# Allow Ctrl+C (SIGINT) to terminate the app immediately from terminal
signal.signal(signal.SIGINT, signal.SIG_DFL)
signal.signal(signal.SIGTERM, signal.SIG_DFL)

# Force XCB (XWayland) platform so WindowStaysOnTopHint and ToolTip stickiness work natively on GNOME
# (Matches setup_systemd.sh in Personal_Permanent_Sticky_Timer)
if os.environ.get('WAYLAND_DISPLAY') and 'QT_QPA_PLATFORM' not in os.environ:
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from note_manager import NoteManager
from windows.main_window import MainWindow
from tray.system_tray import SystemTrayIcon
import persistence.storage as storage
import extension_installer

import atexit

LOCK_FILE = os.path.expanduser("~/.local/share/gnome_linux_note_app/app.lock")
LOCK_FD = None

def cleanup():
    global LOCK_FD
    if LOCK_FD:
        try:
            fcntl.flock(LOCK_FD, fcntl.LOCK_UN)
            LOCK_FD.close()
            LOCK_FD = None
        except Exception:
            pass
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception:
        pass

atexit.register(cleanup)

def acquire_lock():
    global LOCK_FD
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    LOCK_FD = open(LOCK_FILE, 'w')
    try:
        fcntl.flock(LOCK_FD, fcntl.LOCK_EX | fcntl.LOCK_NB)
        LOCK_FD.write(str(os.getpid()))
        LOCK_FD.flush()
        return True
    except (IOError, OSError):
        return False

def main():
    if not acquire_lock():
        print("Application is already running. Exiting.")
        sys.exit(1)

    app = QApplication(sys.argv)
    app.setApplicationName("gnome-sticky-notes")
    app.setDesktopFileName("gnome-sticky-notes")
    app.aboutToQuit.connect(cleanup)

    note_manager = NoteManager()
    main_window = MainWindow(note_manager)
    tray_icon = SystemTrayIcon(note_manager, main_window)

    note_manager.load_all()

    if not extension_installer.is_extension_installed():
        extension_installer.install_and_enable_extension(main_window)

    if tray_icon.isSystemTrayAvailable():
        tray_icon.show()
    else:
        QMessageBox.warning(
            main_window,
            "System Tray Unavailable",
            "The system tray is not available. Please install the 'AppIndicator and KStatusNotifierItem Support' GNOME extension to see the tray icon. The app is fully functional from the Main Window."
        )

    main_window.show()

    def on_quit():
        if hasattr(note_manager, '_notes'):
            storage.save_notes(list(note_manager._notes.values()))

    app.aboutToQuit.connect(on_quit)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
