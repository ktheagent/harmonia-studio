import unittest
from harmonia_studio.arrangement.templates import *

class EnsembleTests(unittest.TestCase):
    def test_required_templates_exist(self):
        required={"satb","piano","piano_vocal","string_quartet","brass","worship_band","jazz_combo","full_band","orchestra"}
        self.assertTrue(required.issubset(TEMPLATES))
    def test_ranges_and_roles(self):
        for t in TEMPLATES.values():
            self.assertTrue(t.instruments)
            for i in t.instruments:
                self.assertLess(i.low,i.high)
                self.assertGreaterEqual(i.polyphony,1)
    def test_custom(self):
        x=custom_template("Duo",[EnsembleInstrument("x","X",0,40,80,role="melody")])
        self.assertEqual(x.name,"Duo")
