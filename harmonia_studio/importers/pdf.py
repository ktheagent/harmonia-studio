from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import shutil, subprocess, tempfile

@dataclass(frozen=True)
class PdfPage:
    page_number:int
    image_path:Path
    dpi:int

@dataclass
class PdfImportPreparation:
    source:Path
    pages:list[PdfPage]
    working_directory:Path

def validate_pdf(path:str|Path)->None:
    p=Path(path)
    if not p.is_file():
        raise FileNotFoundError(p)
    with p.open("rb") as f:
        if f.read(5)!=b"%PDF-":
            raise ValueError("File does not have a PDF signature")

def prepare_pdf_for_omr(path:str|Path,output_dir:str|Path,dpi:int=200)->PdfImportPreparation:
    p=Path(path); validate_pdf(p)
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    exe=shutil.which("pdftoppm")
    if not exe:
        raise RuntimeError("pdftoppm (Poppler) is required for PDF page rendering")
    prefix=out/"page"
    cmd=[exe,"-png","-r",str(int(dpi)),str(p),str(prefix)]
    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
    if proc.returncode!=0:
        raise RuntimeError(f"PDF rendering failed: {proc.stderr.strip()}")
    images=sorted(out.glob("page-*.png"))
    if not images:
        raise RuntimeError("PDF renderer produced no pages")
    return PdfImportPreparation(p,[PdfPage(i+1,img,dpi) for i,img in enumerate(images)],out)
