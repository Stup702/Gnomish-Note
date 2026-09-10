# Gnomish Note — Architecture & Technical Specifications

Technical reference for Gnomish Note, covering application architecture, window mechanics, data persistence, and GNOME desktop integration.

- **Target Platforms**: Linux (GNOME 45, 46, 47, 48+)
- **Display Protocols**: Wayland and X11
- **Runtime**: Python 3.10+, PyQt6

---

## 1. System Overview

Gnomish Note provides frameless desktop sticky notes with multi-workspace persistence, on-the-fly mode switching, and GNOME Alt-Tab window filtering.

```
                     +---------------------------------------+
                     |                main.py                |
                     |  - Single-instance flock lock         |
                     |  - Desktop entry & icon generator     |
                     |  - Signal handlers (SIGINT, SIGUSR1)  |
                     +-------------------+-------------------+
                                         |
            +----------------------------+----------------------------+
            |                            |                            |
            v                            v                            v
  +--------------------+       +--------------------+       +--------------------+
  |  core.NoteManager  |       | windows.MainWindow |       |  tray.SystemTray   |
  |  - In-memory state |<------+  - Master dash     |       |  - Top panel icon  |
  |  - Debounced save  |       |  - Search filter   |       |  - Quick actions   |
  |  - Stacking logic  |       |  - Type toggle     |       +--------------------+
  +---------+----------+       +--------------------+
            |
            +---> EmergencyNoteWindow (Sticky: Always on top, all workspaces)
            +---> NormalNoteWindow    (Standard: Desktop card, collapsible ribbon)
                        |
                        v Both embed NoteContentWidget:
                        |-- TopBar (Drag header, dot badge, roll-up trigger, close)
                        |-- NoteTextEdit (Checklists, markdown shortcuts, smart Enter)
                        |-- SettingsPopover (Fonts, font steppers, colors, opacity slider)
                        \-- FramelessResizer (8-direction border and corner resizing)
```

---

## 2. Codebase Structure

```
gnomish_note/
├── main.py                        # Entry point, single-instance lock, desktop setup
├── run_tests.py                   # Headless test runner with storage sandboxing
├── README.md                      # Project documentation and user guide
├── ARCHITECTURE.md                # System technical specifications
├── icons/                         # Application icon assets
├── src/
│   ├── core/
│   │   ├── note_manager.py        # Central state and window lifecycle controller
│   │   ├── autostart.py           # XDG autostart manager (~/.config/autostart/)
│   │   └── extension_installer.py # GNOME Shell Alt-Tab extension manager
│   ├── models/
│   │   └── note_model.py          # NoteModel dataclass and serialization schema
│   ├── persistence/
│   │   ├── storage.py             # Atomic JSON file I/O and recovery
│   │   └── settings_manager.py    # Global note defaults via QSettings
│   ├── windows/
│   │   ├── main_window.py         # Main dashboard and card list
│   │   ├── emergency_note.py      # Sticky note window (always on top)
│   │   ├── normal_note.py         # Standard note window (collapsible)
│   │   └── default_settings_dialog.py # Global preferences dialog
│   ├── widgets/
│   │   ├── note_content.py        # NoteContentWidget and NoteTextEdit
│   │   ├── top_bar.py             # TopBar header ribbon and controls
│   │   ├── settings_popover.py    # Formatting popover (fonts, colors, opacity)
│   │   ├── frameless_resizer.py   # 8-direction custom window resizer
│   │   ├── font_selector.py       # Curated font dropdown
│   │   └── resize_handle.py       # Bottom-right visual grip handle
│   └── tray/
│       └── system_tray.py         # Top panel indicator for GNOME AppIndicator
└── tests/                         # Automated unit test suite (38 tests)
```

---

## 3. Core Components

### 3.1 Bootstrap & Application Lifecycle (`main.py`)
- **Single-Instance Enforcement**: Uses `fcntl.flock` on `~/.local/share/gnome_linux_note_app/app.lock`. If an instance is already running, reads its PID and sends `SIGUSR1` to bring the dashboard forward, then exits.
- **Signal Handling**: Intercepts `SIGINT` (Ctrl+C) and `SIGTERM` to gracefully commit pending notes to disk before exiting.
- **Desktop Registration**: Automatically creates `~/.local/share/applications/gnomish-note.desktop` on first run and registers high-resolution app icons with `update-desktop-database`.

### 3.2 Data Model (`src/models/note_model.py`)
Each note is encapsulated in a dataclass:
```python
@dataclass
class NoteModel:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    note_type: str = NOTE_TYPE_NORMAL  # "emergency" (sticky) or "normal" (standard)
    content_html: str = ""
    color: str = "#fdf5c9"
    font_color: str = "#333333"
    font_family: str = "Sans Serif"
    font_size: int = 11
    pos_x: int = 100
    pos_y: int = 100
    width: int = 280
    height: int = 320
    minimized: bool = False
    collapsed: bool = False
    opacity: float = 1.0
    z_index: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
```
- Fully serializable to/from JSON via `to_dict()` and `from_dict()`.
- Backward compatible: missing fields in older saves automatically fall back to configured defaults.

### 3.3 State Management (`src/core/note_manager.py`)
- **Central Authority**: Manages in-memory note models and maps them to active window instances (`_notes` and `_windows`).
- **Debounced Save**: Changes trigger a 500ms debounced QTimer to batch disk writes and minimize SSD wear.
- **Z-Order Layering**: Tracks `z_index`. Clicking any note calls `bring_to_front(note_id)`, incrementing the Z-index and ordering window raises.
- **Type Toggle**: Converts notes between `"normal"` and `"emergency"` on the fly, swapping window classes while preserving position, dimensions, text formatting, and cursor focus.

### 3.4 Window Implementations (`src/windows/`)
- **Sticky Notes (`emergency_note.py`)**:
  - Flags: `Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint`.
  - Stays pinned across all virtual workspaces.
  - Excludes close button on the top bar to prevent accidental deletion.
- **Standard Notes (`normal_note.py`)**:
  - Flags: `Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool`.
  - Normal workspace behavior.
  - Supports roll-up mini mode: double-clicking the header collapses the window to a ~36px ribbon displaying the note title or first line of text.
- **Main Dashboard (`main_window.py`)**:
  - Central manager with real-time text and title search.
  - Card controls: open, rename, delete, and 1-click type promotion (`📌` / `🗖`).

### 3.5 Custom Widgets (`src/widgets/`)
- **`NoteTextEdit` (`note_content.py`)**:
  - Intercepts keystrokes for instant markdown conversion (`# `, `## `, `- `, `* `).
  - Checkbox hit-testing: clicking a checkbox (`☐`) toggles it to `☑` and applies strikethrough styling to the line.
  - Smart Enter: auto-continues checkboxes on the next line; exits checklist mode on an empty checkbox.
- **`FramelessResizer` (`frameless_resizer.py`)**:
  - Event filter providing 8-direction border and corner resizing without OS window borders.
  - 6px edge zones, 20px corner zones for comfortable grab tolerance.
  - Enforces a minimum dimension clamp of 100×60px.
- **`TopBar` (`top_bar.py`)**:
  - Header ribbon handling window dragging, roll-up double-click, and minimalist type dot indicators (orange for sticky, green for standard).
- **`SettingsPopover` (`settings_popover.py`)**:
  - Lightweight formatting popover attached to the note's gear button.
  - Houses font selection, size steppers, color swatches, and 40%–100% opacity slider.

---

## 4. Storage & Persistence (`src/persistence/`)

- **Location**: `~/.local/share/gnome_linux_note_app/notes.json`
- **Atomic File Writes**: Serializes data to a temporary file (`notes.json.tmp`) and executes an atomic OS replacement via `os.replace()`, preventing corrupt partial writes on power loss or system crash.
- **Corruption Safeguard**: If JSON decoding fails upon load, the damaged file is automatically quarantined to `notes.json.bak` and a clean workspace is initialized.

---

## 5. GNOME Shell Integration

### Alt-Tab Window Filtering (`src/core/extension_installer.py`)
- Companion GNOME Shell extension: `linux-note-app-integration@stup`.
- Intercepts GNOME Shell's window tracker to hide sticky note windows from the `Alt+Tab` switcher while keeping them visible on screen.
- Managed directly from the settings dialog (install, repair, uninstall).

### Top Panel Indicator (`src/tray/system_tray.py`)
- Leverages the `AppIndicator` standard.
- Provides a tray menu for quick note creation, toggling the dashboard, and hiding/showing all notes.

---

## 6. Automated Testing Suite

- Run with: `python3 run_tests.py`
- Headless execution using `QT_QPA_PLATFORM=offscreen`.
- **Zero-Leakage Isolation**: `run_tests.py` and test classes globally redirect `storage.DATA_DIR` to a temporary directory (`tempfile.TemporaryDirectory()`), guaranteeing live user data is never touched or modified during test runs.
