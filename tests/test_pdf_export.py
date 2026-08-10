import tempfile,unittest,subprocess,shutil
from pathlib import Path
from harmonia_studio.score import *
from harmonia_studio.exporters.pdf_score import export_pdf_score,validate_pdf_file

class PdfExportTests(unittest.TestCase):
    def sample(self):
        m=Measure(1,notes=[Note(Pitch("C",4),1,onset=0,lyrics=[Lyric("Hi")])],harmonies=[Harmony("C",symbol="C")])
        return Score("PDF Test","Composer",[Part("P1","Voice",measures=[m])])
    def test_pdf_modes_and_signature(self):
        with tempfile.TemporaryDirectory() as d:
            for mode in ["full_score","lead_sheet","chord_chart","satb"]:
                p=export_pdf_score(self.sample(),Path(d)/f"{mode}.pdf",mode)
                self.assertTrue(validate_pdf_file(p))
    @unittest.skipUnless(shutil.which("pdftoppm"),"pdftoppm not installed")
    def test_pdf_renders(self):
        with tempfile.TemporaryDirectory() as d:
            p=export_pdf_score(self.sample(),Path(d)/"score.pdf")
            out=Path(d)/"render"
            proc=subprocess.run([shutil.which("pdftoppm"),"-png","-f","1","-singlefile",str(p),str(out)],capture_output=True,timeout=60)
            self.assertEqual(proc.returncode,0)
            png=Path(str(out)+".png")
            self.assertTrue(png.exists())
            self.assertGreater(png.stat().st_size,1000)
