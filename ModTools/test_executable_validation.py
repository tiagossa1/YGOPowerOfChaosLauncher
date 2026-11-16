"""Static executable validation uses synthetic headers, never real programs."""
import hashlib
import struct

import launcher
import pytest
from compatibility import KNOWN_PROFILES, CompatibilityProfile


def make_pe(path, *, dll=False):
    data = bytearray(1024)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 0x3c, 128)
    data[128:132] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', data, 132, 0x14c, 1, 0, 0, 0, 224, 0x2002 if dll else 2)
    struct.pack_into('<H', data, 152, 0x10b)
    struct.pack_into('<I', data, 168, 0x1000)
    struct.pack_into('<H', data, 220, 2)
    struct.pack_into('<IIII', data, 384, 512, 0x1000, 512, 512)
    path.write_bytes(data)
    return path


def test_valid_unknown_pe_returns_its_digest(tmp_path):
    game = make_pe(tmp_path / 'game.exe')
    assert launcher.validate_executable(game) == hashlib.sha256(game.read_bytes()).hexdigest()


@pytest.mark.parametrize('content', (b'', b'MZ', b'not a PE', b'MZ' + bytes(100)))
def test_invalid_headers_are_rejected(tmp_path, content):
    path = tmp_path / 'game.exe'
    path.write_bytes(content)
    with pytest.raises(ValueError):
        launcher.validate_executable(path)


def test_dll_self_and_truncated_sections_are_rejected(tmp_path):
    game = make_pe(tmp_path / 'game.exe', dll=True)
    with pytest.raises(ValueError):
        launcher.validate_executable(game)
    make_pe(game)
    with pytest.raises(ValueError):
        launcher.validate_executable(game, launcher_path=game)
    game.write_bytes(game.read_bytes()[:600])
    with pytest.raises(ValueError):
        launcher.validate_executable(game)


def test_skip_intro_only_passed_for_confirmed_executable(tmp_path, monkeypatch):
    game = make_pe(tmp_path / 'game.exe')
    settings = {**launcher.DEFAULTS, 'skip_intro': True}
    assert '-skipintro' not in launcher.command(game, settings)
    monkeypatch.setitem(KNOWN_PROFILES, launcher.validate_executable(game),
                        CompatibilityProfile('Test', 'flag-only', ('-win', '-nosound', '-skipintro'), True))
    assert '-skipintro' in launcher.command(game, settings)
    settings['skip_intro'] = False
    assert '-skipintro' not in launcher.command(game, settings)


def test_skip_intro_is_stored_in_json_only(tmp_path):
    config = tmp_path / 'launcher.json'
    launcher.save_settings(config, {**launcher.DEFAULTS, 'skip_intro': True})
    assert launcher.load_settings(config)['skip_intro'] is True
    assert not (tmp_path / 'reborn.ini').exists()


@pytest.mark.parametrize('scenario', ('declined', 'changed'))
def test_play_revalidates_and_respects_unknown_confirmation(tmp_path, monkeypatch, scenario):
    from unittest.mock import Mock

    import customtkinter as ctk

    game = make_pe(tmp_path / 'game.exe')
    monkeypatch.setattr(launcher, '__file__', str(tmp_path / 'ModTools' / 'launcher.py'))
    launcher.save_settings(tmp_path / 'launcher.json', {**launcher.DEFAULTS, 'game_path': str(game)})
    process, errors, confirmation = Mock(), Mock(), Mock(return_value=False)
    monkeypatch.setattr(launcher.subprocess, 'Popen', process)
    monkeypatch.setattr(launcher.messagebox, 'showerror', errors)
    monkeypatch.setattr(launcher.messagebox, 'askyesno', confirmation)

    def widgets(parent):
        for child in parent.winfo_children():
            yield child
            yield from widgets(child)

    def exercise(app):
        try:
            if scenario == 'changed':
                game.write_bytes(b'changed after selection')
            next(w for w in widgets(app) if isinstance(w, ctk.CTkButton) and w.cget('text') == 'Play').invoke()
            process.assert_not_called()
            assert app.winfo_exists()
            assert confirmation.call_count == (1 if scenario == 'declined' else 0)
            assert errors.call_count == (1 if scenario == 'changed' else 0)
        finally:
            app.destroy()

    monkeypatch.setattr(ctk.CTk, 'mainloop', exercise)
    launcher.main()
