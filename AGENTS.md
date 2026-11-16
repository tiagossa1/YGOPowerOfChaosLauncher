# Project guidance

## Scope

Build a small Windows launcher for Yu-Gi-Oh! Power of Chaos and community mods.
Universal compatibility is the goal, not an implemented feature. The current
launcher targets `Yugi Reborn - Skip Intro.exe`. Do not claim support for other
editions without testing them.

## Structure

- `ModTools/launcher.py`: CustomTkinter interface, settings, Windows theme, launch logic.
- `ModTools/test_launcher.py`: standard-library unit tests.
- `ModTools/test_launcher_quality.py`: pytest regression and UI tests.
- `ModTools/launcher-requirements.txt`: pinned runtime and packaging dependencies.
- `README.md`: installation, limitations, development, and roadmap.

## Changes

- Read files before editing; preserve concurrent user changes.
- Prefer small changes and standard-library solutions. Avoid unnecessary layers.
- Keep user-facing text and project documentation in English.
- Preserve the compact layout, Windows light/dark theme, accent color, and contrast.
- Keep UI operations on the Tk thread. Do not block the event loop.
- Preserve existing settings and unrelated INI sections and keys.
- Keep JSON writes atomic and clean up temporary files after failures.
- Show actionable errors; do not launch after a settings-save failure.
- Launch with an argument list, without a shell, using the game folder as `cwd`.
- In packaged builds, resolve the game beside the launcher executable. Source mode
  resolves it relative to the repository root.
- Skip intro uses `[Options] SkipIntro` in `reborn.ini`; it requires a compatible
  patched game. Do not force `-skipintro` or present it as universally supported.
- Do not patch game binaries as part of the launcher.
- Do not add game binaries, assets, saves, personal settings, secrets, or local
  absolute paths to tracked files.

## Tests and verification

Add regression tests before fixing bugs. Prefer behavior assertions, temporary
directories, parameterized cases, and mocks only at external boundaries.
Tests must not launch the real game, change real Windows preferences, or write
to the user's game installation. UI tests need a Windows desktop session.

Run from the repository root with Python 3.14 and uv:

```powershell
python -m uv run --no-project --with pytest --with customtkinter==6.0.0 pytest ModTools -q
python -m uv run --no-project --with ruff ruff check ModTools/launcher.py ModTools/test_launcher_quality.py
```

Run the full suite before claiming success. Report failures and untested behavior.
Do not treat simulated process creation as a real-game launch test.

## Packaging

Install dependencies into a dedicated environment:

```powershell
python -m pip install -r ModTools/launcher-requirements.txt
python -m PyInstaller --onefile --windowed --collect-all customtkinter --name "Legend Reborn Launcher" ModTools/launcher.py
```

Build output belongs in `dist/`, not version control. The current build name is
intentional until application naming is generalized. Update the README when
compatibility, configuration, commands, or packaging change.

## Git

Use concise Conventional Commits. Review staged files for accidental game files,
local configuration, caches, and secrets. Commit and push only when requested.
