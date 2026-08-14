import tempfile
import unittest
from pathlib import Path

from harmonia_studio.playback_preferences import clamp_master_volume, scale_part_volumes
from harmonia_studio.settings import AppSettings, SettingsService


class PlaybackPreferenceTests(unittest.TestCase):
    def test_legacy_settings_default_new_playback_fields(self):
        settings = AppSettings.from_dict({"schemaVersion": 1, "theme": "system"})
        self.assertTrue(settings.speakerOutputEnabled)
        self.assertEqual(settings.playbackMasterVolume, 1.0)
        self.assertFalse(settings.loopSelectedMeasure)

    def test_master_volume_is_clamped_and_nonfinite_falls_back(self):
        self.assertEqual(clamp_master_volume(-1), 0.0)
        self.assertEqual(clamp_master_volume(2), 1.0)
        self.assertEqual(clamp_master_volume(float("inf")), 1.0)

    def test_scale_part_volumes_honors_master(self):
        self.assertEqual(scale_part_volumes({0: 1.0, 1: 0.5}, 0.5), {0: 0.5, 1: 0.25})

    def test_settings_round_trip_persists_playback_preferences(self):
        with tempfile.TemporaryDirectory() as d:
            service = SettingsService(Path(d) / "settings.json")
            settings = AppSettings(
                speakerOutputEnabled=False,
                playbackMasterVolume=0.35,
                loopSelectedMeasure=True,
            )
            service.save(settings)
            loaded = service.load()
            self.assertFalse(loaded.speakerOutputEnabled)
            self.assertAlmostEqual(loaded.playbackMasterVolume, 0.35)
            self.assertTrue(loaded.loopSelectedMeasure)


if __name__ == "__main__":
    unittest.main()
