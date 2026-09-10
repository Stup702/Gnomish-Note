# 🎬 Gnomish Note Demo Assets

Place your screen recording GIFs or MP4/WebM videos in this directory to bring the README alive!

## Recommended Recording Specs:
- **Format**: GIF or MP4 (`<video>` tags are natively supported on GitHub).
- **Resolution**: 800px width (compact, crisp, fast loading).
- **Framerate**: 24 - 30 FPS.
- **Duration**: 4 - 8 seconds per clip.

## Key Feature Demos:
1. `hero_demo.gif` — Full desktop showcase: floating sticky notes, standard notes, and top bar indicator.
2. `checklists_markdown.gif` — Typing `# ` for headers, `- ` for checklists, and clicking checkboxes with auto-strikethrough.
3. `collapsible_minimode.gif` — Double-clicking top bar to roll up into ribbon mode, dragging edges in 8 directions.
4. `opacity_and_theming.gif` — Adjusting the 40%-100% opacity slider and picking pastel color swatches.
5. `dashboard_search.gif` — Searching notes in the Master Dashboard and toggling `📌` / `🗖` on the fly.

## Quick Linux GIF Recording Tools:
- **GNOME Built-in Recorder**: Press `Ctrl+Alt+Shift+R` to record screen/selection to `.webm`.
- **Kooha**: Lightweight GNOME screen recorder (`flatpak install flathub io.github.seadve.Kooha`) — supports 1-click GIF & WebM export.
- **Convert WebM to high-quality GIF with ffmpeg**:
  ```bash
  ffmpeg -i input.webm -vf "fps=25,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
  ```
