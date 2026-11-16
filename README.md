# Yu-Gi-Oh! Power of Chaos Launcher

A Windows launcher for Yu-Gi-Oh! Power of Chaos, built with Python and
CustomTkinter. Choose your launch options, then start the game. The interface
follows your Windows light/dark theme and accent color.

The goal is to support Yugi the Destiny, Kaiba the Revenge, Joey the Passion,
and community mods.

Choose the executable for your installation with Browse. Development and testing
have focused on Legend Reborn; launch behavior in other editions still needs
verification.

## Features

- Windowed mode, audio muting, and fast mode through game launch arguments.
- Skip intro logos when used with the supported patched executable.
- Automatic Windows application theme and accent color, updated while open.
- Saved preferences between sessions.
- A game picker that remembers the executable without renaming it.
- A standalone executable that does not require Python on the player's machine.

## Compatibility

| Game or edition | Current status |
| --- | --- |
| Legend Reborn with the supported intro patch | Developed and tested against this version |
| Yugi the Destiny | Launcher compatibility not yet verified |
| Kaiba the Revenge | Launcher compatibility not yet verified |
| Joey the Passion | Launcher compatibility not yet verified |
| Other community mods | Not yet verified; behavior may differ by executable |

You can select any game's `.exe` without renaming it. The launcher uses that
file's directory as the working directory. Selecting a file does not verify its
edition or which launch arguments it supports.

### Launch options

| Option | Mechanism | Notes |
| --- | --- | --- |
| Windowed mode | `-win` | Requests windowed mode. |
| Mute all audio | `-nosound` | Disables music, sound effects, and voices. |
| Fast mode | `-speedy` | Enables the game's built-in speedy option. |
| Skip intro logos | `-skipintro` | Only for the confirmed flag-only patch. |

Argument support and behavior must be checked for each additional edition.
The launcher does not patch game executables or install the intro patch.
The Skip intro logos control appears only for the confirmed patched executable,
identified by SHA-256. Renaming that file does not affect detection; changing its
contents does. The launcher no longer reads or writes `reborn.ini`.
The flag-only patch ignores that file too. Starting the patched game directly
shows the intro unless you supply `-skipintro` yourself.

### Executable checks

Browse and Play check the file's basic Windows PE structure, architecture,
application flags, and section bounds without executing it. DLLs, malformed
headers, and the packaged launcher itself are rejected.

`ModTools/compatibility.py` maps exact SHA-256 digests to edition profiles and
supported arguments. It currently contains the normal Legend Reborn executable
and the flag-only intro patch. Known profiles restrict which arguments are sent.
Unknown executables require confirmation and have no edition-specific features.
The three general launch flags remain available for manual use on unknown files;
their behavior has not been verified for those files. Play checks again even if
you accepted the file in Browse.

A valid PE header does not prove that a file is a Power of Chaos game or free of
malware. A known digest identifies the cataloged version, not a security audit.

### Unverified executable references

These sample hashes were supplied by a contributor, with the source attributions
below. The source pages and samples have not been independently checked for this
project. They are research references, not confirmed compatibility profiles or
evidence that a file is an authentic, unmodified game executable.

| Executable | Reported hashes | Source attribution and limitations |
| --- | --- | --- |
| `Joey_Pc.exe` | MD5: `6bb361cd96a6a1964a35c00625bad82b` | Reported as the game executable by AppQuantify. Another database reportedly labels the same sample “Trojan.Packed”; this reference alone establishes neither authenticity nor safety. |
| `Kaiba_Pc.exe` | MD5: `b4160ad7b97d3c28cfb484ad53e7f4e1`; SHA-1: `67367f7fca2218fda4959837ab0f2696e091b77a`; SHA-256: `a829b16eee11356159850029f5a809886b47c33498ce1d849dd1591a603c0309` | Sample reportedly identified by GridinSoft; FreeFixer reportedly places it in a crack folder. It has not been confirmed as an original, clean Kaiba executable. |

These samples do not represent every legitimate release. None of these hashes
grants a trusted compatibility profile or enables edition-specific features in
the launcher. MD5 and SHA-1 references are not substitutes for the executable
SHA-256 catalog.

### Disc image references

The following CD data-track checksums were supplied by a contributor and
attributed to Redump. The source records have not been independently checked for
this project. They identify disc tracks, not installers or installed executables,
and are not used by the launcher's SHA-256 compatibility catalog.

| Game | Track size (bytes) | CRC-32 | MD5 | SHA-1 |
| --- | ---: | --- | --- | --- |
| Yugi the Destiny | 253456224 | `7782a6dd` | `0ad472e7360f46535e0c0983872e297b` | `f21cb0d90ab2348e11eb9429ad8524f3ab755f84` |
| Kaiba the Revenge | 438568032 | `e7d0def7` | `1e2f07c5d481f8d79682a1ec0da52875` | `c43545b0eece8c861deeed4e5b3ceafea99fafc2` |
| Joey the Passion | 444664416 | `a076e875` | `d68bebe33b5f9d29939a930e86d4c339` | `89872adf97ff8c67020ab410e0eb882e9e5ab188` |

These values apply only to the corresponding disc images. Regions, releases,
installers, and modified builds may differ. They are not Legend Reborn v2 hashes.

## Usage

1. Open `Yu-Gi-Oh! Power of Chaos Launcher.exe`.
2. Click Browse and select your game's `.exe` file.
3. Choose your launch options and select Play.

Settings are saved when you select **Play** or close the launcher:

- `launcher.json` stores the selected game path and all four launch options.
  It is saved beside the launcher. Skip intro defaults to off when upgrading
  from the INI-based version; enable it again after installing the flag-only patch.

Keep the launcher in a writable folder; it does not need to be beside the game.
If settings cannot be saved, the launcher shows an error and leaves the game closed.
Existing launch options are preserved. When upgrading from a build without the
game picker, select your executable once to save its path.

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

When run from source, the launcher saves `launcher.json` in the repository root.
Use Browse to select the game wherever it is installed. You can open the
interface without the game installed, but selecting Play requires it.

Do not commit game binaries, assets, or personal settings to the repository.

### Build a standalone executable

```powershell
python -m PyInstaller --onefile --windowed --collect-all customtkinter --name "Yu-Gi-Oh! Power of Chaos Launcher" ModTools/launcher.py
```

Run `dist/Yu-Gi-Oh! Power of Chaos Launcher.exe` from a writable folder and select
the game with Browse.

### Tests and linting

Install the pinned development dependencies to use the same tool versions as CI:

```powershell
python -m pip install -r ModTools/dev-requirements.txt
python -m pytest ModTools -q
python -m ruff check ModTools
```

Tests cover argument combinations, saved settings, intro preferences, color
contrast, and errors when selecting Play. They use temporary settings and mock
process creation, so the real game stays closed. UI tests open Tk windows and
need a Windows desktop session.

GitHub Actions runs these checks on Windows with Python 3.14 for pull requests
and pushes to `main`. You can also start the workflow manually. Test reports are
available as workflow artifacts for seven days.

### Automated builds and releases

The **Build Windows launcher** workflow runs manually or when launcher code,
dependencies, the README, or its build workflow changes on `main`. It runs tests
and linting before packaging the executable and README into a Windows x64 ZIP.
The ZIP and its SHA-256 checksum are available as workflow artifacts for 14 days.
Builds are unsigned and do not include game files or personal settings.

Pushing a tag beginning with `v`, such as `v0.1.0`, starts the **Draft release**
workflow. It reuses the tested Windows build, verifies the archive checksum, and
creates a draft GitHub release with the ZIP, checksum, and generated release notes.
Review the draft and document compatibility limits before publishing it manually.
Tags should identify reviewed commits; the workflow builds the tagged revision.

Rerunning a completed release will not overwrite an existing release. Manage an
existing draft in GitHub rather than deleting and recreating its tag.

## Roadmap

- Verify launch arguments across the three original games and community mods.
- Add confirmed edition-specific options as compatibility testing progresses.

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
