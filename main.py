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

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from core.note_manager import NoteManager
from windows.main_window import MainWindow
from tray.system_tray import SystemTrayIcon
from core import extension_installer
import persistence.storage as storage

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
    try:
        LOCK_FD = open(LOCK_FILE, 'r+')
    except FileNotFoundError:
        LOCK_FD = open(LOCK_FILE, 'w+')

    try:
        fcntl.flock(LOCK_FD, fcntl.LOCK_EX | fcntl.LOCK_NB)
        LOCK_FD.seek(0)
        LOCK_FD.truncate()
        LOCK_FD.write(str(os.getpid()))
        LOCK_FD.flush()
        return True
    except (IOError, OSError):
        # Lock held by running instance — signal it to show dashboard
        try:
            LOCK_FD.seek(0)
            pid_str = LOCK_FD.read().strip()
            if pid_str.isdigit():
                pid = int(pid_str)
                os.kill(pid, signal.SIGUSR1)
        except Exception:
            pass
        return False

def ensure_desktop_entry():
    home = os.path.expanduser("~")
    desktop_dir = os.path.join(home, ".local", "share", "applications")
    icon_dir = os.path.join(home, ".local", "share", "icons", "hicolor", "512x512", "apps")
    os.makedirs(desktop_dir, exist_ok=True)
    os.makedirs(icon_dir, exist_ok=True)
    
    png_src = os.path.join(os.path.dirname(__file__), "icons", "gnomish-note-v4.png")
    png_dst = os.path.join(icon_dir, "gnomish-note-v4.png")
    if os.path.exists(png_src):
        import shutil
        shutil.copyfile(png_src, png_dst)
        
    desktop_file = os.path.join(desktop_dir, "gnomish-note.desktop")
    main_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
    
    content = f"""[Desktop Entry]
Name=Gnomish Note
GenericName=Sticky Notes
Comment=Sticky & Standard Notes for GNOME Linux
Exec=python3 {main_py}
Icon={png_src}
Terminal=false
Type=Application
Categories=Utility;TextEditor;
StartupWMClass=gnomish-note
"""
    with open(desktop_file, "w") as f:
        f.write(content)

    try:
        import subprocess
        subprocess.run(["update-desktop-database", desktop_dir], capture_output=True, check=False)
    except Exception:
        pass

def main():
    if not acquire_lock():
        print("Application is already running. Activated existing instance.")
        sys.exit(0)

    ensure_desktop_entry()

    from PyQt6.QtCore import QTimer
    app = QApplication(sys.argv)
    app.setApplicationName("gnomish-note")
    app.setDesktopFileName("gnomish-note.desktop")
    
    icon_path = os.path.join(os.path.dirname(__file__), "icons", "gnomish-note-v4.png")
    if os.path.exists(icon_path):
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))
        
    app.aboutToQuit.connect(cleanup)

    note_manager = NoteManager()
    main_window = MainWindow(note_manager)
    tray_icon = SystemTrayIcon(note_manager, main_window)

    note_manager.load_all()

    if not extension_installer.is_extension_installed():
        extension_installer.install_and_enable_extension(main_window)

    tray_icon.show()

    # Set up SIGUSR1 handler to show/focus dashboard when app is launched again
    def handle_sigusr1(sig, frame):
        QTimer.singleShot(0, lambda: (
            main_window.showNormal() if main_window.isMinimized() else None,
            main_window.show(),
            main_window.raise_(),
            main_window.activateWindow()
        ))

    try:
        signal.signal(signal.SIGUSR1, handle_sigusr1)
    except Exception:
        pass

    # Periodic timer to allow Python signal handling within the Qt event loop
    sig_timer = QTimer()
    sig_timer.start(500)
    sig_timer.timeout.connect(lambda: None)

    # By default on startup, keep main dashboard minimized / hidden to keep desktop clean.
    # Only show immediately if explicitly requested via CLI flag.
    if any(arg in sys.argv for arg in ("--show", "--dashboard", "-s")):
        main_window.show()

    def on_quit():
        if hasattr(note_manager, '_notes'):
            storage.save_notes(list(note_manager._notes.values()))

    app.aboutToQuit.connect(on_quit)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
