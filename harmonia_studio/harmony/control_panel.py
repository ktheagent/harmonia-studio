from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from .options import HarmonizationSettings
from .styles import STYLE_REGISTRY

class HarmonizationControlPanel(ttk.Frame):
    """Reusable UI panel. It does not run harmonization directly."""
    def __init__(self, master, settings:HarmonizationSettings|None=None, on_change=None):
        super().__init__(master,padding=8)
        self.settings=settings or HarmonizationSettings()
        self.on_change=on_change
        self.vars={
            "style":tk.StringVar(value=self.settings.style),
            "complexity":tk.StringVar(value=self.settings.complexity),
            "harmonic_density":tk.StringVar(value=self.settings.harmonic_density),
            "chromaticism":tk.DoubleVar(value=self.settings.chromaticism),
            "bass_movement":tk.StringVar(value=self.settings.bass_movement),
            "voice_leading_strictness":tk.StringVar(value=self.settings.voice_leading_strictness),
            "number_of_voices":tk.IntVar(value=self.settings.number_of_voices),
            "preserve_melody":tk.BooleanVar(value=self.settings.preserve_melody),
            "preserve_original_harmony":tk.BooleanVar(value=self.settings.preserve_original_harmony),
            "modulation_level":tk.DoubleVar(value=self.settings.modulation_level),
            "chord_extensions":tk.IntVar(value=self.settings.chord_extensions),
            "rhythmic_density":tk.DoubleVar(value=self.settings.rhythmic_density),
        }
        row=0
        def combo(label,key,values):
            nonlocal row
            ttk.Label(self,text=label).grid(row=row,column=0,sticky="w",pady=3)
            w=ttk.Combobox(self,textvariable=self.vars[key],values=list(values),state="readonly")
            w.grid(row=row,column=1,sticky="ew",pady=3); w.bind("<<ComboboxSelected>>",lambda e:self._changed())
            row+=1
        combo("Style","style",STYLE_REGISTRY.keys())
        combo("Complexity","complexity",["conservative","balanced","stylistic","creative","advanced"])
        combo("Harmonic density","harmonic_density",["measure","beat"])
        combo("Bass movement","bass_movement",["smooth","active","walking","ostinato"])
        combo("Voice leading","voice_leading_strictness",["strict","normal","relaxed"])
        for label,key,lo,hi in [
            ("Chromaticism","chromaticism",0,1),
            ("Modulation","modulation_level",0,1),
            ("Rhythmic density","rhythmic_density",0,1),
        ]:
            ttk.Label(self,text=label).grid(row=row,column=0,sticky="w")
            ttk.Scale(self,from_=lo,to=hi,variable=self.vars[key],command=lambda _=None:self._changed()).grid(row=row,column=1,sticky="ew")
            row+=1
        for label,key in [("Preserve melody","preserve_melody"),("Preserve original harmony","preserve_original_harmony")]:
            ttk.Checkbutton(self,text=label,variable=self.vars[key],command=self._changed).grid(row=row,column=0,columnspan=2,sticky="w")
            row+=1
        self.columnconfigure(1,weight=1)

    def value(self)->HarmonizationSettings:
        d=self.settings.to_dict()
        for k,v in self.vars.items(): d[k]=v.get()
        return HarmonizationSettings(**d).validate()

    def _changed(self):
        if self.on_change:
            self.on_change(self.value())
