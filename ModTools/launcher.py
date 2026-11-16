"""Small, standalone launcher for the modified executable."""
import ctypes
import json
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile
from tkinter import messagebox

GAME = 'Yugi Reborn - Skip Intro.exe'
DEFAULTS = {'windowed': True, 'mute': True, 'fast': False}
FLAGS = {'windowed': '-win', 'mute': '-nosound', 'fast': '-speedy'}


def load_skip_intro(path):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    read = kernel.GetPrivateProfileIntW
    read.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_int, ctypes.c_wchar_p]
    read.restype = ctypes.c_uint
    return bool(read('Options', 'SkipIntro', 0, str(path.resolve())))


def save_skip_intro(path, enabled):
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    write = kernel.WritePrivateProfileStringW
    write.argtypes = [ctypes.c_wchar_p] * 4
    write.restype = ctypes.c_int
    if not write('Options', 'SkipIntro', '1' if enabled else '0', str(path.resolve())):
        raise ctypes.WinError(ctypes.get_last_error())


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


def command(root, settings):
    return [str(root / GAME)] + [flag for key, flag in FLAGS.items() if settings[key]]


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
    with NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                            prefix='launcher-', suffix='.tmp', delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(json.dumps(settings, indent=2) + '\n')
        except BaseException:
            handle.close()
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    import customtkinter as ctk

    root = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent
    config = root / 'launcher.json'
    saved = load_settings(config)
    mode, accent = windows_theme()
    ctk.set_appearance_mode(mode)
    app = ctk.CTk(fg_color=('#f3f4f6', '#202124'))
    app.title('Legend Reborn')
    app.geometry('580x340')
    app.resizable(False, False)
    app.update_idletasks()
    app.geometry(f'+{max(0, (app.winfo_screenwidth() - app.winfo_width()) // 2)}'
                 f'+{max(0, (app.winfo_screenheight() - app.winfo_height()) // 2)}')
    variables = {key: ctk.BooleanVar(value=value) for key, value in saved.items()}
    variables['skip_intro'] = ctk.BooleanVar(value=load_skip_intro(root / 'reborn.ini'))
    ctk.CTkLabel(app, text='Legend Reborn', text_color=('#20242a', '#f0f1f3'),
                 font=('Segoe UI', 25, 'bold')).pack(anchor='w', padx=28, pady=(22, 18))
    panel = ctk.CTkFrame(app, fg_color='transparent', corner_radius=0)
    panel.pack(fill='x', padx=28)
    descriptions = (
        ('windowed', 'Windowed mode', 'Play in a window instead of fullscreen.'),
        ('mute', 'Mute all audio', 'Disable music, sound effects and voices.'),
        ('fast', 'Fast mode', 'Use the game’s built-in speedy option.'),
        ('skip_intro', 'Skip intro logos', 'Go straight to the title screen.'),
    )
    checkboxes = []
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

    def settings():
        return {key: variables[key].get() for key in DEFAULTS}

    def save():
        try:
            save_settings(config, settings())
            save_skip_intro(root / 'reborn.ini', variables['skip_intro'].get())
            return True
        except OSError as error:
            messagebox.showerror('Could not save settings', str(error), parent=app)
            return False

    def play():
        if not (root / GAME).is_file():
            messagebox.showerror('Game not found', f'Keep this launcher in the game folder, next to:\n\n{GAME}', parent=app)
            return
        if not save():
            return
        try:
            subprocess.Popen(command(root, settings()), cwd=root)
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
            for checkbox in checkboxes:
                checkbox.configure(fg_color=color, hover_color=color, checkmark_color=accent_text(color))
            current_theme = theme
        app.after(1000, update_theme)

    app.after(1000, update_theme)
    app.protocol('WM_DELETE_WINDOW', close)
    app.mainloop()


if __name__ == '__main__':
    main()
