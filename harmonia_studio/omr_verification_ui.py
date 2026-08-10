from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from .omr_verification import OMRVerificationSession

class OMRVerificationPanel(ttk.Frame):
    """Simple side-by-side verification surface: source-page identity and editable recognized note list."""
    def __init__(self,master,session:OMRVerificationSession):
        super().__init__(master,padding=8)
        self.session=session
        left=ttk.LabelFrame(self,text="Original Score",padding=8)
        right=ttk.LabelFrame(self,text="Recognized Score",padding=8)
        left.pack(side="left",fill="both",expand=True,padx=(0,4))
        right.pack(side="left",fill="both",expand=True,padx=(4,0))
        page=session.original_result.source_pages[0] if session.original_result.source_pages else "Source page unavailable"
        ttk.Label(left,text=page,wraplength=300).pack(anchor="nw")
        self.listbox=tk.Listbox(right)
        self.listbox.pack(fill="both",expand=True)
        self.refresh()
        ttk.Button(right,text="Approve Recognition",command=self._approve).pack(pady=6)

    def refresh(self):
        self.listbox.delete(0,"end")
        if not self.session.score.parts: return
        for mi,m in enumerate(self.session.score.parts[0].measures):
            for ni,n in enumerate(m.notes):
                pitch="Rest" if n.pitch is None else f"{n.pitch.step}{'#' if n.pitch.alter>0 else 'b' if n.pitch.alter<0 else ''}{n.pitch.octave}"
                self.listbox.insert("end",f"M{mi+1} N{ni+1}: {pitch}")

    def _approve(self):
        self.session.approve()
