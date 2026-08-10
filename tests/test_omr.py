import tempfile, unittest
from pathlib import Path
import numpy as np, cv2
from harmonia_studio.importers.omr import recognize_image

class OMRTests(unittest.TestCase):
    def synthetic(self,path):
        img=np.full((180,500),255,np.uint8)
        ys=[60,72,84,96,108]
        for y in ys: cv2.line(img,(20,y),(480,y),0,1)
        # noteheads on/near staff positions, no stems (baseline recognizer)
        for x,y in [(100,108),(180,96),(260,84),(340,72)]:
            cv2.ellipse(img,(x,y),(6,4),-15,0,360,0,-1)
        cv2.imwrite(str(path),img)
    def test_clean_staff_recognition(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"score.png"; self.synthetic(p)
            r=recognize_image(p)
            self.assertGreaterEqual(len(r.symbols),3)
            self.assertTrue(r.score.parts[0].measures)
            self.assertTrue(all(s.pitch is not None for s in r.symbols))
            self.assertTrue(0<=r.confidence<=1)
