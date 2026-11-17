import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).resolve().parents[1] / "extras/new_popular_preset.py"


class PresetTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "profile/new-popular-preset-backup.json"
        self.dialog = SimpleNamespace(yesno=Mock(return_value=True), ok=Mock(), notification=Mock())
        modules = {
            "xbmc": SimpleNamespace(getSkinDir=lambda: "skin.titan.bingie.mod", log=Mock(), LOGERROR=4),
            "xbmcaddon": SimpleNamespace(Addon=lambda _: SimpleNamespace(getLocalizedString=str)),
            "xbmcgui": SimpleNamespace(Dialog=lambda: self.dialog),
            "xbmcvfs": SimpleNamespace(translatePath=lambda _: str(self.path)),
        }
        spec = importlib.util.spec_from_file_location("preset_under_test", SCRIPT)
        self.preset = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, modules):
            spec.loader.exec_module(self.preset)
        self.original = {key: 'Custom, ("عربي") \\ {}'.format(key) for key in self.preset.KEYS}
        self.current = dict(self.original)
        self.preset.current_values = lambda: dict(self.current)
        self.preset.set_values = Mock(side_effect=self.current.update)

    def test_cancel_does_not_write_or_change_rows(self):
        self.dialog.yesno.return_value = False
        self.preset.main()
        self.assertEqual(self.current, self.original)
        self.assertFalse(self.path.exists())
        self.preset.set_values.assert_not_called()

    def test_apply_and_restore_preserve_previous_values(self):
        self.preset.main()
        self.assertEqual(json.loads(self.path.read_text()), self.original)
        self.assertEqual(len(self.current), 20)
        for row in (510, 520, 530, 540):
            prefix = "bingiehub-new-{}.".format(row)
            self.assertTrue(self.current[prefix + "path"].startswith(
                "plugin://plugin.video.themoviedb.helper/?"))
            self.assertEqual(self.current[prefix + "target"], "videos")
            self.assertEqual(self.current[prefix + "sortby"], "")
            self.assertEqual(self.current[prefix + "sortorder"], "")
        self.preset.main("restore")
        self.assertEqual(self.current, self.original)

    def test_reapply_does_not_replace_original_undo_state(self):
        self.preset.main()
        first_backup = self.path.read_bytes()
        self.preset.main()
        self.assertEqual(self.path.read_bytes(), first_backup)

    def test_apply_after_edit_saves_the_edited_rows(self):
        self.preset.main()
        self.current["bingiehub-new-510.label"] = "Edited label"
        edited = dict(self.current)
        self.preset.main()
        self.preset.main("restore")
        self.assertEqual(self.current, edited)

    def test_cancel_restore_preserves_current_shelves(self):
        self.preset.main()
        current = dict(self.current)
        self.dialog.yesno.return_value = False
        self.preset.main("restore")
        self.assertEqual(self.current, current)

    def test_failed_backup_prevents_any_settings_change(self):
        with patch.object(self.preset, "save_backup", side_effect=OSError("Read-only profile")):
            self.preset.main()
        self.preset.set_values.assert_not_called()
        self.assertEqual(self.current, self.original)
        self.dialog.ok.assert_called_once()

    def test_bad_backup_cannot_change_unrelated_settings(self):
        self.path.parent.mkdir()
        self.path.write_text(json.dumps({"unrelated.setting": "value"}))
        self.preset.main("restore")
        self.preset.set_values.assert_not_called()
        self.dialog.ok.assert_called_once()

    def test_missing_backup_does_not_change_rows(self):
        self.preset.main("restore")
        self.preset.set_values.assert_not_called()
        self.dialog.ok.assert_called_once()

    def test_atomic_backup_failure_retains_previous_file(self):
        self.preset.save_backup(str(self.path), self.original)
        with patch.object(self.preset.os, "replace", side_effect=OSError("Write failed")):
            with self.assertRaises(OSError):
                self.preset.save_backup(str(self.path), {"different": "values"})
        self.assertEqual(json.loads(self.path.read_text()), self.original)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_inactive_skin_and_unknown_mode_are_ignored(self):
        self.preset.main("unexpected")
        self.preset.xbmc.getSkinDir = lambda: "skin.estuary"
        self.preset.main()
        self.dialog.yesno.assert_not_called()
        self.preset.set_values.assert_not_called()


if __name__ == "__main__":
    unittest.main()
