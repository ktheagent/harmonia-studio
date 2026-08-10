import tempfile, unittest, shutil
from pathlib import Path
from harmonia_studio.importers.pdf import validate_pdf,prepare_pdf_for_omr

class PdfImportTests(unittest.TestCase):
    def test_invalid_signature(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.pdf"; p.write_text("not pdf")
            with self.assertRaises(ValueError): validate_pdf(p)
    @unittest.skipUnless(shutil.which("pdftoppm"),"pdftoppm not installed")
    def test_render_pdf_page(self):
        from reportlab.pdfgen import canvas
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.pdf"; c=canvas.Canvas(str(p)); c.drawString(100,700,"Score"); c.save()
            prep=prepare_pdf_for_omr(p,Path(d)/"pages",100)
            self.assertEqual(len(prep.pages),1)
            self.assertTrue(prep.pages[0].image_path.exists())
