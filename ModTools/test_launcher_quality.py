"""Launcher regression tests; never start the real game or edit its settings."""
import hashlib
import json
from itertools import product
from pathlib import Path
from unittest.mock import Mock

import launcher
import pytest
from compatibility import KNOWN_PROFILES, CompatibilityProfile
from test_executable_validation import make_pe


@pytest.mark.parametrize(('windowed', 'mute', 'fast'), list(product((False, True), repeat=3)))
def test_all_flag_combinations(tmp_path, windowed, mute, fast):
    settings = {'windowed': windowed, 'mute': mute, 'fast': fast}
    executable = tmp_path / 'joey_pc.exe'
    expected = [str(executable)]
    expected += [flag for enabled, flag in zip((windowed, mute, fast),
                                               ('-win', '-nosound', '-speedy')) if enabled]
    assert launcher.command(executable, settings) == expected


def test_executable_selection_round_trip_and_invalid_data(tmp_path):
    config = tmp_path / 'launcher.json'
    assert launcher.load_game(config) is None
    game = tmp_path / 'Other game' / 'kaiba_pc.exe'
    launcher.save_settings(config, {**launcher.DEFAULTS, 'game_path': str(game)})
    assert launcher.load_game(config) == game
    for data in ({'game_path': 123}, {'game_path': 'relative.exe'}, []):
        config.write_text(json.dumps(data), encoding='utf-8')
        assert launcher.load_game(config) is None


def test_intro_support_requires_exact_content_not_filename(tmp_path, monkeypatch):
    game = tmp_path / 'Yugi Reborn - Skip Intro.exe'
    game.write_bytes(b'unknown executable')
    assert launcher.supports_intro(game) is False
    monkeypatch.setitem(KNOWN_PROFILES, hashlib.sha256(game.read_bytes()).hexdigest(),
                        CompatibilityProfile('Test', 'flag-only', ('-skipintro',), True))
    assert launcher.supports_intro(game) is True
    renamed = game.rename(tmp_path / 'renamed.exe')
    assert launcher.supports_intro(renamed) is True
    renamed.write_bytes(b'changed')
    assert launcher.supports_intro(renamed) is False
    assert launcher.supports_intro(tmp_path / 'missing.exe') is False


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


def test_browse_updates_game_hides_intro_and_leaves_unknown_ini_untouched(tmp_path, monkeypatch):
    import customtkinter as ctk

    monkeypatch.setattr(launcher, '__file__', str(tmp_path / 'ModTools' / 'launcher.py'))
    supported = tmp_path / 'supported.exe'
    make_pe(supported)
    other = tmp_path / 'other' / 'yugi_pc.exe'
    other.parent.mkdir()
    make_pe(other)
    ini = other.parent / 'reborn.ini'
    ini.write_bytes(b'[Options]\r\nSkipIntro=1\r\n')
    before = ini.read_bytes()
    launcher.save_settings(tmp_path / 'launcher.json', {**launcher.DEFAULTS, 'game_path': str(supported)})
    monkeypatch.setattr(launcher, 'supports_intro', lambda path: path == supported)
    monkeypatch.setattr(launcher.filedialog, 'askopenfilename', lambda **kwargs: str(other))
    monkeypatch.setattr(launcher.messagebox, 'askyesno', lambda *args, **kwargs: True)
    process = Mock()
    monkeypatch.setattr(launcher.subprocess, 'Popen', process)

    def widgets(parent):
        for child in parent.winfo_children():
            yield child
            yield from widgets(child)

    def exercise(app):
        app.update_idletasks()
        assert app.title() == launcher.APP_NAME
        controls = list(widgets(app))
        intro = next(w for w in controls if isinstance(w, ctk.CTkCheckBox) and w.cget('text') == 'Skip intro logos')
        assert intro.master.winfo_manager() == 'pack'
        next(w for w in controls if isinstance(w, ctk.CTkButton) and w.cget('text') == 'Browse…').invoke()
        assert intro.master.winfo_manager() == ''
        next(w for w in controls if isinstance(w, ctk.CTkButton) and w.cget('text') == 'Play').invoke()

    monkeypatch.setattr(ctk.CTk, 'mainloop', exercise)
    launcher.main()
    process.assert_called_once_with(launcher.command(other, launcher.DEFAULTS), cwd=other.parent)
    assert launcher.load_game(tmp_path / 'launcher.json') == other
    assert ini.read_bytes() == before


@pytest.mark.parametrize('scenario', ('success', 'missing', 'save_error', 'start_error'))
def test_play_button_handles_launch_and_errors(tmp_path, monkeypatch, scenario):
    import customtkinter as ctk

    monkeypatch.setattr(launcher, '__file__', str(tmp_path / 'ModTools' / 'launcher.py'))
    monkeypatch.setattr(launcher, 'windows_theme', lambda: ('light', '#245a91'))
    game = tmp_path / 'games' / 'custom.exe'
    game.parent.mkdir()
    if scenario != 'missing':
        make_pe(game)
    if scenario == 'save_error':
        (tmp_path / 'launcher.json').mkdir()
    else:
        launcher.save_settings(tmp_path / 'launcher.json', {**launcher.DEFAULTS, 'game_path': str(game)})
    monkeypatch.setattr(launcher, 'supports_intro', lambda path: True)
    monkeypatch.setattr(launcher.messagebox, 'askyesno', lambda *args, **kwargs: True)
    if scenario == 'save_error':
        monkeypatch.setattr(launcher, 'load_game', lambda path: game)
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
            button = next(w for w in widgets(app) if isinstance(w, ctk.CTkButton) and w.cget('text') == 'Play')
            button.invoke()
            if scenario in ('success', 'start_error'):
                expected_settings = {**launcher.DEFAULTS, 'skip_intro': True}
                process.assert_called_once_with(launcher.command(game, expected_settings), cwd=game.parent)
                assert launcher.load_settings(tmp_path / 'launcher.json')['skip_intro'] is True
                assert not (game.parent / 'reborn.ini').exists()
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
