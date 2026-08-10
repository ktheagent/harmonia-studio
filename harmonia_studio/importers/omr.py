from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
import math
from harmonia_studio.score import Score, Part, Instrument, Measure, Note, Pitch, TimeSignature, KeySignature
from .pdf import prepare_pdf_for_omr

@dataclass(frozen=True)
class OMRSymbol:
    page:int
    kind:str
    bbox:tuple[int,int,int,int]
    confidence:float
    pitch:Pitch|None=None

@dataclass
class OMRResult:
    score:Score
    symbols:list[OMRSymbol]
    confidence:float
    warnings:list[str]=field(default_factory=list)
    source_pages:list[str]=field(default_factory=list)

def _cluster_rows(rows:list[int],max_gap:int=2)->list[float]:
    if not rows: return []
    groups=[[rows[0]]]
    for r in rows[1:]:
        if r-groups[-1][-1]<=max_gap:
            groups[-1].append(r)
        else:
            groups.append([r])
    return [sum(g)/len(g) for g in groups]

def _group_staff_lines(lines:list[float])->list[list[float]]:
    groups=[]
    i=0
    while i+4<len(lines):
        candidate=lines[i:i+5]
        gaps=[candidate[j+1]-candidate[j] for j in range(4)]
        avg=sum(gaps)/4
        if avg>=4 and max(abs(g-avg) for g in gaps)<=max(2.5,avg*.3):
            groups.append(candidate); i+=5
        else:
            i+=1
    return groups

_STEPS=["C","D","E","F","G","A","B"]
def _pitch_from_staff_y(cy:float,staff:list[float])->Pitch:
    spacing=sum(staff[i+1]-staff[i] for i in range(4))/4
    bottom=staff[-1]
    diatonic_steps=round((bottom-cy)/(spacing/2))
    base_index=4*7+2  # E4
    idx=base_index+diatonic_steps
    octave=idx//7
    step=_STEPS[idx%7]
    return Pitch(step,octave,0)

def recognize_image(path:str|Path,page_number:int=1)->OMRResult:
    try:
        import cv2
        import numpy as np
    except ImportError as e:
        raise RuntimeError("OpenCV and NumPy are required for built-in OMR") from e
    p=Path(path)
    image=cv2.imread(str(p),cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError(f"Unable to read score image: {p}")
    # Black notation -> white foreground.
    _,bw=cv2.threshold(image,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    h,w=bw.shape
    row_counts=(bw>0).sum(axis=1)
    rows=[int(i) for i,c in enumerate(row_counts) if c>max(20,int(w*0.35))]
    lines=_cluster_rows(rows,2)
    staves=_group_staff_lines(lines)
    warnings=[]
    if not staves:
        return OMRResult(Score(p.stem,"",[Part("P1","Recognized",Instrument("Piano"),[])]),[],0.0,
                         ["No five-line staff system detected."],[str(p)])

    cleaned=bw.copy()
    for y in lines:
        yy=int(round(y))
        cleaned[max(0,yy-1):min(h,yy+2),:]=0
    # Reconnect notehead halves split by staff-line removal without recreating long staff lines.
    cleaned=cv2.morphologyEx(cleaned,cv2.MORPH_CLOSE,np.ones((5,3),np.uint8))
    contours,_=cv2.findContours(cleaned,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    symbols=[]
    staff_notes=[[] for _ in staves]
    for contour in contours:
        x,y,cw,ch=cv2.boundingRect(contour)
        area=cv2.contourArea(contour)
        cy=y+ch/2
        # Assign to nearest staff.
        si=min(range(len(staves)),key=lambda j:abs(cy-sum(staves[j])/5))
        staff=staves[si]
        spacing=sum(staff[k+1]-staff[k] for k in range(4))/4
        staff_top=staff[0]-3*spacing
        staff_bottom=staff[-1]+3*spacing
        if not (staff_top<=cy<=staff_bottom): continue
        # Filled/outline notehead baseline. This intentionally avoids claiming stems/flags yet.
        if not (0.35*spacing <= ch <= 1.55*spacing and 0.35*spacing <= cw <= 2.0*spacing):
            continue
        if area < max(4,0.08*spacing*spacing):
            continue
        aspect=cw/max(ch,1)
        if not (0.45<=aspect<=2.4): continue
        pitch=_pitch_from_staff_y(cy,staff)
        grid=spacing/2
        dist=abs(((staff[-1]-cy)/grid)-round((staff[-1]-cy)/grid))
        grid_conf=max(0.0,1.0-dist/0.5)
        aspect_conf=max(0.0,1.0-abs(aspect-1.25)/1.25)
        conf=max(0.1,min(0.98,0.55*grid_conf+0.45*aspect_conf))
        sym=OMRSymbol(page_number,"notehead",(x,y,cw,ch),conf,pitch)
        symbols.append(sym)
        staff_notes[si].append((x,sym))

    measures=[]
    number=1
    for notes in staff_notes:
        notes.sort(key=lambda pair:pair[0])
        note_objs=[]
        for idx,(_,sym) in enumerate(notes):
            note_objs.append(Note(sym.pitch,1.0,onset=float(idx)))
        if note_objs:
            measures.append(Measure(number,notes=note_objs,time=TimeSignature(4,4),key=KeySignature(),tempo=120))
            number+=1
    if not measures:
        warnings.append("Staff lines were detected but no noteheads met recognition thresholds.")
    part=Part("P1","Recognized Score",Instrument("Piano"),measures)
    overall=sum(s.confidence for s in symbols)/len(symbols) if symbols else 0.0
    if overall<0.65 and symbols:
        warnings.append("Recognition confidence is low; verify the score before harmonizing.")
    return OMRResult(Score(p.stem,"",[part],{"sourceFormat":"OMR"}),symbols,overall,warnings,[str(p)])

def recognize_score(path:str|Path,working_directory:str|Path|None=None)->OMRResult:
    p=Path(path)
    if p.suffix.lower()!=".pdf":
        if p.suffix.lower() not in {".png",".jpg",".jpeg",".tif",".tiff"}:
            raise ValueError("Built-in OMR supports PDF, PNG, JPG/JPEG and TIFF")
        return recognize_image(p,1)

    if working_directory is None:
        with TemporaryDirectory(prefix="harmonia-omr-") as td:
            return _recognize_pdf(p,Path(td))
    return _recognize_pdf(p,Path(working_directory))

def _recognize_pdf(path:Path,workdir:Path)->OMRResult:
    prep=prepare_pdf_for_omr(path,workdir)
    all_symbols=[]; all_measures=[]; warnings=[]; pages=[]
    number=1
    for page in prep.pages:
        r=recognize_image(page.image_path,page.page_number)
        pages.append(str(page.image_path)); warnings.extend(r.warnings); all_symbols.extend(r.symbols)
        for m in (r.score.parts[0].measures if r.score.parts else []):
            m.number=number; number+=1; all_measures.append(m)
    score=Score(path.stem,"",[Part("P1","Recognized Score",Instrument("Piano"),all_measures)],{"sourceFormat":"PDF-OMR","sourcePath":str(path)})
    overall=sum(s.confidence for s in all_symbols)/len(all_symbols) if all_symbols else 0.0
    return OMRResult(score,all_symbols,overall,warnings,pages)
