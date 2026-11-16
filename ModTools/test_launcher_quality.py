"""Launcher regression tests; never start the real game or edit its settings."""
from itertools import product
from pathlib import Path
from unittest.mock import Mock

import launcher
import pytest


def test_intro_setting_round_trip_preserves_other_ini_values(tmp_path):
    ini = tmp_path / 'reborn.ini'
    ini.write_text('[Options]\nSkipIntro=1\nOther=42\n', encoding='ascii')
    assert launcher.load_skip_intro(ini) is True
    launcher.save_skip_intro(ini, False)
    assert launcher.load_skip_intro(ini) is False
    assert 'Other=42' in ini.read_text(encoding='ascii')
    launcher.save_skip_intro(ini, True)
    assert launcher.load_skip_intro(ini) is True


def test_intro_setting_defaults_to_off_and_reports_write_failure(tmp_path):
    assert launcher.load_skip_intro(tmp_path / 'reborn.ini') is False
    with pytest.raises(OSError):
        launcher.save_skip_intro(tmp_path / 'missing' / 'reborn.ini', True)


@pytest.mark.parametrize(('windowed', 'mute', 'fast'), list(product((False, True), repeat=3)))
def test_all_flag_combinations(tmp_path, windowed, mute, fast):
    settings = {'windowed': windowed, 'mute': mute, 'fast': fast}
    expected = [str(tmp_path / launcher.GAME)]
    expected += [flag for enabled, flag in zip((windowed, mute, fast),
                                               ('-win', '-nosound', '-speedy')) if enabled]
    assert launcher.command(tmp_path, settings) == expected


def test_failed_save_preserves_preferences_and_removes_temporary_file(tmp_path, monkeypatch):
    path = tmp_path / 'launcher.json'
    path.write_text('{"mute": false}', encoding='utf-8')

    def denied(*args):
        raise PermissionError('File is locked')

    monkeypatch.setattr(Path, 'replace', denied)
    with pytest.raises(PermissionError):
        launcher.save_settings(path, launcher.DEFAULTS)
    assert path.read_text(encoding='utf-8') == '{"mute": false}'
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('scenario', ('success', 'missing', 'save_error', 'start_error'))
def test_play_button_handles_launch_and_errors(tmp_path, monkeypatch, scenario):
    import customtkinter as ctk

    monkeypatch.setattr(launcher, '__file__', str(tmp_path / 'ModTools' / 'launcher.py'))
    monkeypatch.setattr(launcher, 'windows_theme', lambda: ('light', '#245a91'))
    game = tmp_path / launcher.GAME
    if scenario != 'missing':
        game.touch()
    if scenario == 'save_error':
        (tmp_path / 'launcher.json').mkdir()
    errors = Mock()
    process = Mock(side_effect=OSError('Cannot start') if scenario == 'start_error' else None)
    monkeypatch.setattr(launcher.messagebox, 'showerror', errors)
    monkeypatch.setattr(launcher.subprocess, 'Popen', process)

    def widgets(parent):
        for child in parent.winfo_children():
            yield child
            yield from widgets(child)

    def exercise(app):
        try:
            app.update_idletasks()
            boxes = [w for w in widgets(app) if isinstance(w, ctk.CTkCheckBox)]
            assert len(boxes) == 4
            intro = next(w for w in boxes if w.cget('text') == 'Skip intro logos')
            intro.select()
            button = next(w for w in widgets(app) if isinstance(w, ctk.CTkButton))
            button.invoke()
            if scenario in ('success', 'start_error'):
                process.assert_called_once_with(launcher.command(tmp_path, launcher.DEFAULTS), cwd=tmp_path)
                assert launcher.load_skip_intro(tmp_path / 'reborn.ini') is True
            else:
                process.assert_not_called()
            assert errors.call_count == (0 if scenario == 'success' else 1)
            if scenario != 'success':
                assert app.winfo_exists()
        finally:
            if scenario != 'success':
                app.destroy()

    monkeypatch.setattr(ctk.CTk, 'mainloop', exercise)
    launcher.main()
