import unittest
from harmonia_studio.score import *
from harmonia_studio.harmony.styles import get_style,harmonize_style

def sample():
    ms=[Measure(i+1,notes=[Note(Pitch.from_midi(p),4,onset=0)]) for i,p in enumerate([72,74,71,72])]
    return Score("Hymn","",[Part("P1","Melody",measures=ms)])

class StyleTests(unittest.TestCase):
    def test_hymn_style(self):
        p=get_style("hymn")
        self.assertEqual(p.validation_strictness,"strict")
        r=harmonize_style(sample(),"hymn")
        self.assertEqual(r.score.metadata["harmonyStyle"],"hymn")
        self.assertEqual(len(r.score.parts),4)
        self.assertTrue(r.plan.preserve_melody)

    def test_classical_style(self):
        p=get_style("classical")
        self.assertEqual(p.validation_strictness,"classical")
        r=harmonize_style(sample(),"classical")
        self.assertEqual(r.score.metadata["harmonyStyle"],"classical")
        self.assertEqual(len(r.score.parts),4)

    def test_gospel_levels(self):
        for level in ["simple","modern","advanced"]:
            r=harmonize_style(sample(),"gospel",level)
            self.assertEqual(r.score.metadata["harmonyStyle"],"gospel")
            self.assertTrue(any(c.quality=="dominant-seventh" for c in r.plan.choices))
        advanced=harmonize_style(sample(),"gospel","advanced")
        self.assertTrue(any(c.quality in {"diminished","dominant-seventh"} for c in advanced.plan.choices))

    def test_jazz_style_ii_v_and_extensions(self):
        r=harmonize_style(sample(),"jazz","balanced")
        qualities=[c.quality for c in r.plan.choices]
        self.assertIn("minor-seventh",qualities)
        self.assertIn("dominant-seventh",qualities)
        self.assertEqual(r.plan.choices[-1].quality,"major-seventh")
        creative=harmonize_style(sample(),"jazz","creative")
        self.assertTrue(any(c.root_name=="C#" for c in creative.plan.choices))

    def test_pop_four_chord_loop(self):
        r=harmonize_style(sample(),"pop")
        rel=[(c.root_pc-r.plan.choices[0].root_pc)%12 for c in r.plan.choices]
        self.assertEqual([c.root_name for c in r.plan.choices[:4]],["C","G","A","F"])
        self.assertEqual(r.score.metadata["harmonyStyle"],"pop")

    def test_rnb_extended_and_slash_motion(self):
        r=harmonize_style(sample(),"rnb","balanced")
        self.assertTrue(all(c.quality in {"major-seventh","minor-seventh","dominant-seventh","diminished"} for c in r.plan.choices))
        self.assertTrue(any(c.inversion==1 for c in r.plan.choices))
        self.assertEqual(r.score.metadata["harmonyStyle"],"rnb")

    def test_highlife_profile_progression(self):
        # Five-measure source for I-I-IV-V-I loop.
        s=sample()
        s.parts[0].measures.append(Measure(5,notes=[Note(Pitch("C",5),4,onset=0)]))
        r=harmonize_style(s,"highlife","balanced")
        self.assertEqual([c.root_name for c in r.plan.choices[:5]],["C","C","F","G","C"])
        self.assertIn("guitar",r.profile.rhythmic_character)

    def test_afrobeat_sparse_vamp(self):
        s=sample()
        # duplicate to make 8 measures
        s.parts[0].measures += [Measure(i+5,notes=[Note(Pitch("C",5),4,onset=0)]) for i in range(4)]
        r=harmonize_style(s,"afrobeat","balanced")
        roots=[c.root_name for c in r.plan.choices[:8]]
        self.assertEqual(roots[:4],["C","C","Bb","Bb"])
        self.assertEqual(r.profile.bass_behavior,"ostinato")

    def test_blues_twelve_bar(self):
        measures=[Measure(i+1,notes=[Note(Pitch("C",5),4,onset=0)]) for i in range(12)]
        s=Score("Blues","",[Part("P1","Melody",measures=measures)])
        r=harmonize_style(s,"blues","balanced")
        self.assertEqual(len(r.plan.choices),12)
        self.assertTrue(all(c.quality=="dominant-seventh" for c in r.plan.choices))
        self.assertEqual([c.root_name for c in r.plan.choices[8:12]],["G","F","C","G"])
