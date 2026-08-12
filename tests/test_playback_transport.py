import time
import unittest

from harmonia_studio.playback import PlaybackEngine, PlaybackState
from harmonia_studio.score import Measure, Note, Part, Pitch, Score, TimeSignature


class PlaybackTransportRegressionTests(unittest.TestCase):
    def score_with_tempo_change(self):
        return Score(parts=[
            Part("P1", "Piano", measures=[
                Measure(1, notes=[Note(Pitch("C", 4), 1, onset=0)], tempo=60),
                Measure(2, notes=[Note(Pitch("D", 4), 1, onset=0)], tempo=120),
            ])
        ])

    def test_tempo_change_accumulates_measure_time(self):
        events = PlaybackEngine().schedule(self.score_with_tempo_change())
        self.assertEqual(len(events), 2)
        self.assertAlmostEqual(events[0].time_seconds, 0.0, places=4)
        self.assertAlmostEqual(events[1].time_seconds, 4.0, places=4)
        self.assertAlmostEqual(events[1].duration_seconds, 0.5, places=4)

    def test_seek_rebases_time_and_filters_earlier_measure(self):
        events = PlaybackEngine().schedule(self.score_with_tempo_change(), start_measure=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].measure_index, 1)
        self.assertAlmostEqual(events[0].time_seconds, 0.0, places=4)

    def test_event_keeps_note_index_for_canvas_highlight(self):
        score = Score(parts=[Part("P1", "P", measures=[Measure(
            1,
            notes=[
                Note(Pitch("C", 4), 1, onset=0),
                Note(Pitch("E", 4), 1, onset=1),
            ],
        )])])
        events = PlaybackEngine().schedule(score)
        self.assertEqual([event.note_index for event in events], [0, 1])

    def test_loop_repeats_until_stopped(self):
        score = Score(parts=[Part("P1", "P", measures=[Measure(
            1, notes=[Note(Pitch("C", 4), 0.01, onset=0)], tempo=600
        )])])
        heard = []
        engine = PlaybackEngine(lambda event: heard.append(event))
        engine.set_loop(0, 0)
        engine.play(score)
        deadline = time.time() + 0.25
        while len(heard) < 2 and time.time() < deadline:
            time.sleep(0.01)
        engine.stop()
        self.assertGreaterEqual(len(heard), 2)
        self.assertEqual(engine.state, PlaybackState.STOPPED)

    def test_mute_solo_and_volume_remain_supported(self):
        score = Score(parts=[
            Part("P1", "A", measures=[Measure(1, notes=[Note(Pitch("C", 4), 1)])]),
            Part("P2", "B", measures=[Measure(1, notes=[Note(Pitch("E", 4), 1)])]),
        ])
        engine = PlaybackEngine()
        engine.mute(0)
        muted = engine.schedule(score)
        self.assertEqual({event.part_index for event in muted}, {1})
        engine.mute(0, False)
        engine.solo(0)
        soloed = engine.schedule(score)
        self.assertEqual({event.part_index for event in soloed}, {0})
        engine.solo(0, False)
        engine.set_volume(0, 0.5)
        volume = engine.schedule(score)
        self.assertEqual(volume[0].velocity, 40)


if __name__ == "__main__":
    unittest.main()
