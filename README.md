# Yu-Gi-Oh! Power of Chaos Launcher

A Windows launcher for Yu-Gi-Oh! Power of Chaos, built with Python and
CustomTkinter. Choose your launch options, then start the game. The interface
follows your Windows light/dark theme and accent color.

The goal is to support Yugi the Destiny, Kaiba the Revenge, Joey the Passion,
and community mods.

Development and testing have focused on Legend Reborn. Support for other editions
still needs executable selection and compatibility checks.

## Features

- Windowed mode, audio muting, and fast mode through game launch arguments.
- Skip intro logos when used with the supported patched executable.
- Automatic Windows application theme and accent color, updated while open.
- Saved preferences between sessions.
- A standalone executable that does not require Python on the player's machine.

## Compatibility

| Game or edition | Current status |
| --- | --- |
| Legend Reborn with the supported intro patch | Developed and tested against this version |
| Yugi the Destiny | Launcher compatibility not yet verified |
| Kaiba the Revenge | Launcher compatibility not yet verified |
| Joey the Passion | Launcher compatibility not yet verified |
| Other community mods | Not yet verified; behavior may differ by executable |

The launcher currently looks for `Yugi Reborn - Skip Intro.exe`, with no executable
picker or automatic game detection. Do not rename another game's executable to
match: the filename alone does not make it compatible.

### Launch options

| Option | Mechanism | Notes |
| --- | --- | --- |
| Windowed mode | `-win` | Requests windowed mode. |
| Mute all audio | `-nosound` | Disables music, sound effects, and voices. |
| Fast mode | `-speedy` | Enables the game's built-in speedy option. |
| Skip intro logos | `[Options] SkipIntro` in `reborn.ini` | Requires the supported game patch; not a standard feature of every edition. |

Argument support and behavior must be checked for each additional edition.
The launcher does not patch game executables or install the intro patch.
Unmodified games are not expected to read the custom `SkipIntro` setting.

## Usage

1. Use your own Legend Reborn installation with the supported patched executable.
2. Place the compiled launcher next to `Yugi Reborn - Skip Intro.exe`.
3. Open the launcher, choose your options, and select **Play**.

The build is still named Legend Reborn Launcher, and the window title is
Legend Reborn. These names will change when support extends to other editions.

Settings are saved when you select **Play** or close the launcher:

- `launcher.json` stores windowed mode, audio muting, and fast mode.
- `reborn.ini` stores the intro-logo preference for the supported patch.

Keep the launcher in a writable game folder. If it cannot save settings, it
shows an error and leaves the game closed.

## Development

Development and packaging have been tested with Python 3.14 on Windows.
Run the following commands from the repository root.

### Install dependencies

Use a dedicated Python environment, then install:

```powershell
python -m pip install -r ModTools/launcher-requirements.txt
```

### Run from source

```powershell
python ModTools/launcher.py
```

When run from source, the launcher looks for the game in the repository root,
regardless of the current working directory. You can open the interface without
the game installed, but selecting **Play** requires it.

Do not commit game binaries, assets, or personal settings to the repository.

### Build a standalone executable

```powershell
python -m PyInstaller --onefile --windowed --collect-all customtkinter --name "Legend Reborn Launcher" ModTools/launcher.py
```

Copy `dist/Legend Reborn Launcher.exe` into the game folder. The packaged launcher
looks for the game beside its own executable.

### Tests and linting

With [uv](https://docs.astral.sh/uv/) installed:

```powershell
python -m uv run --no-project --with pytest --with customtkinter==6.0.0 pytest ModTools -q
python -m uv run --no-project --with ruff ruff check ModTools/launcher.py ModTools/test_launcher_quality.py
```

Tests cover argument combinations, saved settings, intro preferences, color
contrast, and errors when selecting Play. They use temporary settings and mock
process creation, so the real game stays closed. UI tests open Tk windows and
need a Windows desktop session.

## Roadmap

- Select and remember the game executable without renaming it.
- Replace Legend Reborn-specific application naming.
- Verify launch arguments across the three original games and community mods.
- Make edition-specific options explicit and unavailable where unsupported.
- Separate general launcher preferences from mod-specific configuration.

## Reporting issues

Include your Windows version, game edition or mod, executable filename, selected
options, and steps to reproduce the problem. Error text or a screenshot can help.
Do not upload game executables or copyrighted assets.

## Disclaimer

This is an unofficial fan project, not affiliated with or endorsed by Konami.
No game executables, patches, or game assets are included in this repository.
You must provide your own game installation.

Local builds are unsigned, so Windows or antivirus software may request
confirmation. Do not disable system protection to run the launcher.
