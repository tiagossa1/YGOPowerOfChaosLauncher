# Project guidance

## Scope

Build a small Windows launcher for Yu-Gi-Oh! Power of Chaos and community mods.
Users select and save the game executable through Browse. Compatibility testing
has focused on Legend Reborn; do not claim verified support for other editions.

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
- Store the selected absolute game path in `launcher.json`, beside the packaged
  launcher or in the repository root in source mode. Use the selected game's
  directory for game-specific settings and the process working directory.
- Store Skip Intro in JSON and pass `-skipintro` only for confirmed compatible
  executable profiles. Never read or write `reborn.ini`.
- Validate PE structure and reject DLLs and the launcher itself at Browse and Play.
  Unknown SHA-256 digests require confirmation and gain no edition-specific features.
- Keep executable SHA-256 profiles in `ModTools/compatibility.py`. Disc-image
  checksums are reference data only; never treat them as executable identities.
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
python -m uv run --no-project --with ruff ruff check ModTools
```

Run the full suite before claiming success. Report failures and untested behavior.
Do not treat simulated process creation as a real-game launch test.

## Packaging

Install dependencies into a dedicated environment:

```powershell
python -m pip install -r ModTools/launcher-requirements.txt
python -m PyInstaller --onefile --windowed --collect-all customtkinter --name "Yu-Gi-Oh! Power of Chaos Launcher" ModTools/launcher.py
```

Build output belongs in `dist/`, not version control. Update the README when
compatibility, configuration, commands, or packaging change.

## Git

Use concise Conventional Commits. Review staged files for accidental game files,
local configuration, caches, and secrets. Commit and push only when requested.
