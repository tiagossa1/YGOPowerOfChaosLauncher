"""Windows launcher for Yu-Gi-Oh! Power of Chaos editions and mods."""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from tkinter import filedialog, messagebox

from compatibility import identify_digest

APP_NAME = 'Yu-Gi-Oh! Power of Chaos Launcher'
DEFAULTS = {'windowed': True, 'mute': True, 'fast': False, 'skip_intro': False}
FLAGS = {'windowed': '-win', 'mute': '-nosound', 'fast': '-speedy'}


def validate_executable(path, launcher_path=None):
    """Check basic PE structure and return its digest, without executing it."""
    if path.suffix.lower() != '.exe' or not path.is_file():
        raise ValueError("Choose an existing .exe game file.")
    if launcher_path is not None and path.samefile(launcher_path):
        raise ValueError("This is the launcher. Choose the game's .exe file.")
    with path.open('rb') as handle:
        size = handle.seek(0, 2)
        handle.seek(0)
        dos = handle.read(64)
        if len(dos) != 64 or dos[:2] != b'MZ':
            raise ValueError('This file is not a Windows PE executable.')
        offset = struct.unpack_from('<I', dos, 60)[0]
        if offset < 64 or offset + 24 > size:
            raise ValueError('The executable has an invalid PE header.')
        handle.seek(offset)
        header = handle.read(24)
        machine, sections, _, _, _, optional_size, flags = struct.unpack_from('<HHIIIHH', header, 4)
        if header[:4] != b'PE\0\0' or machine not in (0x14c, 0x8664) or not 1 <= sections <= 96:
            raise ValueError('Choose a Windows x86 or x64 executable.')
        if not flags & 2 or flags & 0x2000:
            raise ValueError('This file is not an application executable (DLLs are not supported).')
        if optional_size < 96 or offset + 24 + optional_size + sections * 40 > size:
            raise ValueError('The executable headers are truncated.')
        optional = handle.read(optional_size)
        magic = struct.unpack_from('<H', optional)[0]
        if (machine, magic) not in ((0x14c, 0x10b), (0x8664, 0x20b)) or (magic == 0x20b and optional_size < 112):
            raise ValueError('The executable has an invalid optional header.')
        if struct.unpack_from('<H', optional, 68)[0] not in (2, 3):
            raise ValueError('Choose a Windows desktop application.')
        for _ in range(sections):
            section = handle.read(40)
            raw_size, raw_offset = struct.unpack_from('<II', section, 16)
            if raw_size and (raw_offset == 0 or raw_offset + raw_size > size):
                raise ValueError('The executable contains truncated section data.')
        handle.seek(0)
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def windows_value(key, name, default):
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as handle:
            value, kind = winreg.QueryValueEx(handle, name)
            return value if kind == winreg.REG_DWORD else default
    except (ImportError, OSError):
        return default


def windows_theme():
    light = windows_value(r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize',
                          'AppsUseLightTheme', 1)
    color = windows_value(r'Software\Microsoft\Windows\DWM', 'ColorizationColor', 0xFF245A91)
    return ('light' if light else 'dark', f'#{color & 0xFFFFFF:06x}')


def accent_text(color):
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels]
    luminance = sum(v * weight for v, weight in zip(linear, (0.2126, 0.7152, 0.0722)))
    return '#000000' if (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05) else '#ffffff'


def command(executable, settings):
    profile = executable_profile(executable)
    args = [str(executable)] + [flag for key, flag in FLAGS.items()
                               if settings[key] and (profile is None or flag in profile.arguments)]
    if settings.get('skip_intro', False) and supports_intro(executable):
        args.append('-skipintro')
    return args


def load_game(config):
    try:
        data = json.loads(config.read_text(encoding='utf-8'))
        value = data.get('game_path') if isinstance(data, dict) else None
        if isinstance(value, str) and value and Path(value).is_absolute():
            return Path(value)
    except (OSError, ValueError):
        pass
    return None


def executable_profile(executable):
    try:
        with executable.open('rb') as handle:
            return identify_digest(hashlib.file_digest(handle, 'sha256').hexdigest())
    except OSError:
        return None


def supports_intro(executable):
    profile = executable_profile(executable)
    return profile is not None and profile.skip_intro and '-skipintro' in profile.arguments


def load_settings(path):
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return DEFAULTS.copy()
    if not isinstance(data, dict):
        return DEFAULTS.copy()
    return {key: data[key] if type(data.get(key)) is bool else default
            for key, default in DEFAULTS.items()}


def save_settings(path, settings):
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                prefix='launcher-', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json.dumps(settings, indent=2) + '\n')
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    import customtkinter as ctk

    root = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
    config = root / 'launcher.json'
    saved = load_settings(config)
    selected_game = load_game(config)
    mode, accent = windows_theme()
    ctk.set_appearance_mode(mode)
    app = ctk.CTk(fg_color=('#f3f4f6', '#202124'))
    app.title(APP_NAME)
    app.geometry('620x410')
    app.resizable(False, False)
    app.update_idletasks()
    app.geometry(f'+{max(0, (app.winfo_screenwidth() - app.winfo_width()) // 2)}'
                 f'+{max(0, (app.winfo_screenheight() - app.winfo_height()) // 2)}')
    variables = {key: ctk.BooleanVar(value=value) for key, value in saved.items()}
    ctk.CTkLabel(app, text='Yu-Gi-Oh! Power of Chaos', text_color=('#20242a', '#f0f1f3'),
                 font=('Segoe UI', 25, 'bold')).pack(anchor='w', padx=28, pady=(22, 12))
    selector = ctk.CTkFrame(app, fg_color='transparent')
    selector.pack(fill='x', padx=28, pady=(0, 20))
    game_text = ctk.StringVar(value=str(selected_game) if selected_game else 'Choose a game (.exe)')
    game_entry = ctk.CTkEntry(selector, textvariable=game_text, state='readonly', height=32)
    game_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
    panel = ctk.CTkFrame(app, fg_color='transparent', corner_radius=0)
    panel.pack(fill='x', padx=28)
    descriptions = (
        ('windowed', 'Windowed mode', 'Run in a window.'),
        ('mute', 'Mute all audio', 'Turn off music, effects and voices.'),
        ('fast', 'Fast mode', "Use the game's fast mode."),
        ('skip_intro', 'Skip intro logos', 'Skip the startup logos.'),
    )
    checkboxes = []
    intro_frame = None
    for key, title, description in descriptions:
        frame = ctk.CTkFrame(panel, fg_color='transparent')
        frame.pack(fill='x', pady=(0, 12))
        checkbox = ctk.CTkCheckBox(
            frame, text=title, variable=variables[key], font=('Segoe UI', 14),
            text_color=('#20242a', '#f0f1f3'), checkbox_width=18, checkbox_height=18,
            corner_radius=3, border_width=1, border_color=('#697480', '#a8afb8'),
            fg_color=accent, hover_color=accent, checkmark_color=accent_text(accent))
        checkboxes.append(checkbox)
        checkbox.grid(row=0, column=0, sticky='w')
        ctk.CTkLabel(frame, text=description, font=('Segoe UI', 11),
                     text_color=('#59636e', '#b6bec8')).grid(row=0, column=1, sticky='w', padx=(18, 0))
        frame.grid_columnconfigure(0, minsize=160)
        if key == 'skip_intro':
            intro_frame = frame

    def refresh_intro():
        intro_frame.pack_forget()
        if selected_game is not None and supports_intro(selected_game):
            intro_frame.pack(fill='x', pady=(0, 12))

    def confirm_executable(candidate):
        try:
            own_path = Path(sys.executable) if getattr(sys, 'frozen', False) else None
            digest = validate_executable(candidate, launcher_path=own_path)
        except (OSError, ValueError) as error:
            messagebox.showerror('Invalid game file', str(error), parent=app)
            return False
        if identify_digest(digest) is None:
            return messagebox.askyesno(
                'Unrecognized executable',
                'This executable has not been verified as a supported game.\n\n'
                'A valid PE file is not a guarantee of safety. Only continue if you trust its source.\n\n'
                f'{candidate}\n\nContinue?', parent=app, default='no')
        return True

    def browse():
        nonlocal selected_game
        filename = filedialog.askopenfilename(
            parent=app, title='Select game executable',
            initialdir=str(selected_game.parent if selected_game else root),
            filetypes=[('Windows executable', '*.exe')])
        if not filename:
            return
        candidate = Path(filename).resolve()
        if not confirm_executable(candidate):
            return
        selected_game = candidate
        game_text.set(str(candidate))
        refresh_intro()

    browse_button = ctk.CTkButton(selector, text='Browse…', width=90, height=32,
                                 fg_color=accent, hover_color=accent,
                                 text_color=accent_text(accent), command=browse)
    browse_button.pack(side='right')
    refresh_intro()

    def settings():
        return {key: variables[key].get() for key in DEFAULTS}

    def save():
        try:
            save_settings(config, {**settings(), 'game_path': str(selected_game) if selected_game else ''})
            return True
        except OSError as error:
            messagebox.showerror('Could not save settings', str(error), parent=app)
            return False

    def play():
        if selected_game is None or not selected_game.is_file() or selected_game.suffix.lower() != '.exe':
            messagebox.showerror('Game not found', 'Click Browse to choose the game\'s .exe file.', parent=app)
            return
        if not confirm_executable(selected_game):
            refresh_intro()
            return
        refresh_intro()
        if not save():
            return
        try:
            subprocess.Popen(command(selected_game, settings()), cwd=selected_game.parent)
        except OSError as error:
            messagebox.showerror('Could not start game', str(error), parent=app)
            return
        app.destroy()

    def close():
        if save():
            app.destroy()

    footer = ctk.CTkFrame(app, fg_color=('#e9ecf0', '#292b30'), corner_radius=0)
    footer.pack(side='bottom', fill='x')
    play_button = ctk.CTkButton(footer, text='Play', width=100, height=36, corner_radius=4,
                               fg_color=accent, hover_color=accent, text_color=accent_text(accent),
                               font=('Segoe UI', 14), command=play)
    play_button.pack(side='right', padx=(0, 28), pady=18)

    current_theme = (mode, accent)

    def update_theme():
        nonlocal current_theme
        theme = windows_theme()
        if theme != current_theme:
            mode, color = theme
            ctk.set_appearance_mode(mode)
            play_button.configure(fg_color=color, hover_color=color, text_color=accent_text(color))
            browse_button.configure(fg_color=color, hover_color=color, text_color=accent_text(color))
            for checkbox in checkboxes:
                checkbox.configure(fg_color=color, hover_color=color, checkmark_color=accent_text(color))
            current_theme = theme
        app.after(1000, update_theme)

    app.after(1000, update_theme)
    app.protocol('WM_DELETE_WINDOW', close)
    app.mainloop()


if __name__ == '__main__':
    main()
