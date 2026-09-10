<div align="center">

<img src="icons/gnomish-note.png" width="120" height="120" alt="Gnomish Note Icon" />

# Gnomish Note

A fast, lightweight sticky note and desktop scratchpad built for GNOME on Linux (Wayland and X11) that can make the notes stay on top, and hide them from alt-tab switcher.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52?style=flat-square&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![GNOME Shell](https://img.shields.io/badge/GNOME-45%20|%2046%20|%2047%20|%2048+-4a86cf?style=flat-square&logo=gnome&logoColor=white)](https://www.gnome.org/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square)](LICENSE)

<br/>

</div>

---

## Features

### Sticky Notes
I needed important things always visible on screen so I wouldn't forget them — deadlines, quick reminders, whatever needed to stay in front of me.

Sticky notes float over everything, stay pinned across all GNOME workspaces, and have no close button — so you can't accidentally kill one while typing. Notes are deleted from the main window only.

<p align="center">
  <img src="assets/demos/sticky_notes.gif" width="750" alt="Sticky Notes Demo" onerror="this.onerror=null; this.style.display='none';" />
</p>

### Main Window & Mode Switching
The main window serves as the CRUD interface. It is hidden by default on startup and can be summoned anytime from the top panel indicator or by launching Gnomish Note from your app grid. Persistent themes for the notes can also be set from the settings. 

<p align="center">
  <img src="assets/demos/main_window.png" width="400" alt="Main window and alt-tab Demo" onerror="this.onerror=null; this.style.display='none';" />
</p>

#### Alt-Tab Switcher Hiding
I didn't want to cycle through 10 note windows every time I needed to get back to my browser. Gnomish Note includes a companion GNOME Shell extension that keeps sticky notes on your screen but out of the Alt-Tab switcher entirely. You can install, verify, or remove the extension from the settings dialog.

<p align="center">
  <img src="assets/demos/alt-tab_demo.gif" width="750" alt="Main window and alt-tab Demo" onerror="this.onerror=null; this.style.display='none';" />
</p>

#### Instant Mode Switching
Not all notes are emergencies. Some are normal things to remember. Normal notes sit on your current workspace and don't float over everything. Sticky notes do. You can switch any note between the two modes from the dashboard without losing anything.

<p align="center">
  <img src="assets/demos/mode_switch.gif" width="750" alt="Mode switch demo" onerror="this.onerror=null; this.style.display='none';" />
</p>



### Roll-Up Mode
During classes and presentations, my private notes kept showing up on screen while I was sharing. To fix this, notes have a roll-up mode: double-click the top bar and the note collapses into a slim ribbon showing only the title. Double-click again to expand back.

<p align="center">
  <img src="assets/demos/rollup_mode.gif" width="750" alt="Roll-Up Mode Demo" onerror="this.onerror=null; this.style.display='none';" />
</p>

### Quick Checklists & Markdown
I needed to track the day's to-do list. Notes support interactive checkboxes, headings, and strikethrough — all keyboard-driven, no toolbar.
- `-` or `*` for checkboxes, click to mark done. 
- `#`and `##` for simple headers

<p align="center">
  <img src="assets/demos/checklists.gif"  alt="Checklists and Markdown Demo" onerror="this.onerror=null; this.style.display='none';" />
</p>

### Sizing, Opacity, and Window Controls
Notes are borderless. Resize from any edge or corner — corners have larger hit zones so precision can jump out the window. Opacity goes from 40% to 100% so you can read what's under a note. Click any overlapping note to bring it to front, order is saved across restarts.

<p align="center">
  <img src="assets/demos/dashboard.png" alt="Dashboard Demo" onerror="this.onerror=null; this.style.display='none';" />
</p>

---

## Shortcuts Reference

| Shortcut | Context | Action |
| :--- | :--- | :--- |
| `Ctrl+Shift+C` | Note Editor | Toggle interactive checklist on current line |
| `Ctrl+Shift+X` | Note Editor | Toggle strikethrough formatting |
| `Enter` | Checklist Item | Auto-insert new checkbox on next line |
| `Enter` | Empty Checkbox | Exit checklist mode |
| `Double-Click` | Note Header | Collapse note into roll-up ribbon / Expand back |
| `Escape` | Settings Popover | Dismiss settings popover |

---

## Installation & Setup

### Option 1: Standalone Binary (Recommended)
Download the latest pre-compiled Linux binary from [GitHub Releases](https://github.com/Stup702/Gnomish-Note/releases/latest):

```bash
# Make the downloaded binary executable and run
chmod +x gnomish-note
./gnomish-note
```
*(On first run, Gnomish Note automatically installs its icon and registers a desktop launcher in `~/.local/share/applications/` so you can launch it directly from your GNOME App Grid).*

### Option 2: Run from Source
If you prefer running directly with Python:
- **OS**: Linux with GNOME 45, 46, 47, or 48+ (Wayland or X11)
- **Runtime**: Python 3.10+
- **Dependencies**: PyQt6

```bash
# Clone the repository
git clone https://github.com/Stup702/Gnomish-Note.git
cd Gnomish-Note

# Install dependencies and run
pip install PyQt6
python3 main.py
```

### Option 3: Build Binary from Source
To compile your own standalone single-file executable using PyInstaller:
```bash
python3 build_binary.py
./dist/gnomish-note
```

---

## Automated Tests

Includes a test suite of the bugs I had to face during development and some use cases I thought would occur.
Uses mock storage isolation and headless rendering to not mess up actual notes. 
```bash
python3 run_tests.py
```

## Future Plans
- Add note lock system
- Add note organization feature to the main window

## License & Credits

- **License**: [GPL-3.0 License](LICENSE)
- **Inspiration**: Special thanks to [koter84/AltTabHide](https://github.com/koter84/AltTabHide) for the GNOME Shell Alt-Tab filtering concepts.
- **Framework**: Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/).
