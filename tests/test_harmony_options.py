import unittest
from harmonia_studio.harmony.options import HarmonizationSettings

class HarmonyOptionsTests(unittest.TestCase):
    def test_defaults_and_serialization(self):
        s=HarmonizationSettings().validate()
        self.assertTrue(s.preserve_melody)
        self.assertEqual(s.to_dict()["style"],"hymn")
    def test_validation(self):
        with self.assertRaises(ValueError):
            HarmonizationSettings(number_of_voices=0).validate()
        with self.assertRaises(ValueError):
            HarmonizationSettings(chromaticism=2).validate()
