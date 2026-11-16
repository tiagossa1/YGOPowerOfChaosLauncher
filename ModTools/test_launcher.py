import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import launcher


class LauncherTests(unittest.TestCase):
    def test_windows_theme_reads_light_mode_and_argb_accent(self):
        with patch.object(launcher, 'windows_value', side_effect=[0, 0xC478318F]):
            self.assertEqual(launcher.windows_theme(), ('dark', '#78318f'))
        with patch.object(launcher, 'windows_value', side_effect=[1, 0xFF0078D4]):
            self.assertEqual(launcher.windows_theme(), ('light', '#0078d4'))

    def test_accent_foreground_has_readable_contrast(self):
        self.assertEqual(launcher.accent_text('#ffffff'), '#000000')
        self.assertEqual(launcher.accent_text('#000000'), '#ffffff')
        self.assertEqual(launcher.accent_text('#ffff00'), '#000000')
        self.assertEqual(launcher.accent_text('#245a91'), '#ffffff')
        self.assertEqual(launcher.accent_text('#0078d4'), '#000000')

    def test_missing_windows_setting_uses_fallback(self):
        self.assertEqual(launcher.windows_value('Software\\LegendRebornMissingTestKey', 'Missing', 123), 123)

    def test_command_targets_modified_game_and_only_selected_flags(self):
        root = Path('C:/Games/Legend Reborn')
        self.assertEqual(launcher.command(root, launcher.DEFAULTS),
                         [str(root / launcher.GAME), '-win', '-nosound'])
        self.assertEqual(launcher.command(root, dict(windowed=False, mute=False, fast=True)),
                         [str(root / launcher.GAME), '-speedy'])

    def test_preferences_round_trip_without_touching_game_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'launcher.json'
            self.assertEqual(launcher.load_settings(path), launcher.DEFAULTS)
            settings = dict(windowed=False, mute=False, fast=True)
            launcher.save_settings(path, settings)
            self.assertEqual(launcher.load_settings(path), settings)
            self.assertFalse((path.parent / 'reborn.ini').exists())

    def test_invalid_preferences_fall_back_to_safe_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'launcher.json'
            for content in ('broken', '[]', '{"windowed":"false","mute":0}'):
                path.write_text(content, encoding='utf-8')
                self.assertEqual(launcher.load_settings(path), launcher.DEFAULTS)


if __name__ == '__main__':
    unittest.main()
