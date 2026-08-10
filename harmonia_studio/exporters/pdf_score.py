from __future__ import annotations
from pathlib import Path
from harmonia_studio.score import Score

MODES={"full_score","individual_part","lead_sheet","chord_chart","satb"}

def export_pdf_score(score:Score,path:str|Path,mode:str="full_score",part_index:int|None=None)->Path:
    if mode not in MODES: raise ValueError(f"Unknown PDF export mode: {mode}")
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    p=Path(path)
    if p.suffix.lower()!=".pdf": p=p.with_suffix(".pdf")
    p.parent.mkdir(parents=True,exist_ok=True)
    c=canvas.Canvas(str(p),pagesize=A4)
    width,height=A4
    margin=42
    c.setTitle(score.title or "Harmonia Studio Score")
    c.setAuthor(score.composer or "Harmonia Studio")
    c.setFont("Helvetica-Bold",18); c.drawString(margin,height-margin,score.title or "Untitled")
    if score.composer:
        c.setFont("Helvetica",10); c.drawRightString(width-margin,height-margin,score.composer)
    y=height-margin-45

    if mode=="individual_part":
        if part_index is None or not (0<=part_index<len(score.parts)): raise ValueError("Valid part_index required")
        parts=[score.parts[part_index]]
    elif mode=="lead_sheet":
        parts=score.parts[:1]
    elif mode=="satb":
        parts=score.parts[:4]
    else:
        parts=score.parts

    if mode=="chord_chart":
        c.setFont("Helvetica-Bold",12); c.drawString(margin,y,"Chord Chart"); y-=24
        if score.parts:
            for m in score.parts[0].measures:
                symbols="  ".join(h.symbol or h.root for h in m.harmonies) or "(no chord)"
                c.setFont("Helvetica",11); c.drawString(margin,y,f"Measure {m.number}: {symbols}"); y-=18
                if y<margin+30: c.showPage(); y=height-margin
        c.save(); return p

    for part in parts:
        c.setFont("Helvetica-Bold",10)
        if y<margin+90: c.showPage(); y=height-margin
        c.drawString(margin,y,part.name); y-=14
        for m in part.measures:
            if y<margin+90:
                c.showPage(); y=height-margin
                c.setFont("Helvetica-Bold",10); c.drawString(margin,y,part.name+" (cont.)"); y-=14
            staff_top=y
            spacing=8
            x0=margin+20; x1=width-margin
            for i in range(5):
                yy=staff_top-i*spacing
                c.setLineWidth(.5); c.line(x0,yy,x1,yy)
            c.setFont("Helvetica",7); c.drawString(margin,staff_top,f"{m.number}")
            if m.harmonies:
                c.setFont("Helvetica-Bold",9)
                step=max(55,(x1-x0)/max(1,len(m.harmonies)))
                for hi,harm in enumerate(m.harmonies):
                    c.drawString(x0+hi*step,staff_top+12,harm.symbol or harm.root)
            length=max(1.0,m.time.beats*4.0/m.time.beat_type)
            for n in m.notes:
                x=x0+20+(n.onset/length)*(x1-x0-35)
                if n.pitch is None:
                    c.rect(x-3,staff_top-2*spacing-2,6,3,fill=1,stroke=0)
                else:
                    # Treble-oriented staff mapping: B4 middle line.
                    y_note=(staff_top-2*spacing)-((n.pitch.midi()-71)*(spacing/2))
                    c.saveState(); c.translate(x,y_note); c.rotate(-15); c.ellipse(-4,-2.7,4,2.7,fill=1,stroke=0); c.restoreState()
                    if n.duration<=2: c.line(x+3,y_note,x+3,y_note+24)
                    if n.lyrics and mode in {"full_score","individual_part","lead_sheet","satb"}:
                        text=" ".join(l.text for l in n.lyrics if l.text)
                        c.setFont("Helvetica",8); c.drawCentredString(x,staff_top-5*spacing-14,text)
            y-=75
        y-=12
    c.save()
    return p

def validate_pdf_file(path:str|Path)->bool:
    p=Path(path)
    if not p.is_file() or p.stat().st_size<100: return False
    with p.open("rb") as f:
        return f.read(5)==b"%PDF-"
