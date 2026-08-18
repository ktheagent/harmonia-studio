from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from .menu_safe_app import MenuSafeHarmoniaApp
from .playback_preferences import clamp_master_volume
from .version import get_version_info

class ProfessionalShellHarmoniaApp(MenuSafeHarmoniaApp):
    def _configure_style(self):
        super()._configure_style()
        s=ttk.Style(self)
        s.configure("HS.H1.TLabel",font=("Segoe UI",16,"bold"))
        s.configure("HS.H2.TLabel",font=("Segoe UI",9,"bold"))

    def _build_shell(self):
        self.geometry("1440x900"); self.minsize(1100,700)
        self.status_var=tk.StringVar(value="Ready")
        self.playback_measure_var=tk.StringVar(value="1")
        self.playback_loop_var=tk.BooleanVar(value=bool(self.settings.loopSelectedMeasure))
        self.playback_position_var=tk.StringVar(value="Stopped")
        self.duration_var=tk.StringVar(value="1")
        self.lyrics_var=tk.StringVar(); self.harmony_var=tk.StringVar()
        self.speaker_enabled_var=tk.BooleanVar(value=bool(self.settings.speakerOutputEnabled))
        self.master_volume_var=tk.DoubleVar(value=clamp_master_volume(self.settings.playbackMasterVolume))
        self._topbar(); self._body(); self._transport(); self._status()
        self.bind_all("<Control-z>",lambda e:self._undo_edit()); self.bind_all("<Control-y>",lambda e:self._redo_edit())

    def _topbar(self):
        b=ttk.Frame(self,padding=6); b.pack(fill="x")
        groups=[
            (("New",self._new_project),("Open",self._open_project),("Save",self._save_project)),
            (("Undo",self._undo_edit),("Redo",self._redo_edit)),
            (("Pitch −",lambda:self._transpose_selected(-1)),("Pitch +",lambda:self._transpose_selected(1)),("Delete",self._delete_selected)),
            (("Analyze",self._analyze),("Harmonize",self._harmonize),("Arrange",self._arrange)),
            (("Import",self._import_music),("Export",self._export_music))]
        for n,g in enumerate(groups):
            if n: ttk.Separator(b,orient="vertical").pack(side="left",fill="y",padx=5)
            for text,cmd in g: ttk.Button(b,text=text,command=cmd).pack(side="left",padx=2)

    def _body(self):
        p=ttk.Panedwindow(self,orient="horizontal"); p.pack(fill="both",expand=True)
        left,center,right=(ttk.Frame(p,padding=8) for _ in range(3))
        p.add(left,weight=0); p.add(center,weight=1); p.add(right,weight=0)
        ttk.Label(left,text="PROJECT",style="HS.H2.TLabel").pack(anchor="w")
        self.parts_list=tk.Listbox(left,width=24,exportselection=False); self.parts_list.pack(fill="both",expand=True,pady=(8,0))
        self.parts_list.bind("<<ListboxSelect>>",self._show_part)
        head=ttk.Frame(center); head.pack(fill="x")
        self.workspace_title=ttk.Label(head,text="Welcome to Harmonia Studio",style="HS.H1.TLabel"); self.workspace_title.pack(side="left")
        z=ttk.Frame(head); z.pack(side="right")
        ttk.Button(z,text="−",width=3,command=lambda:self._change_zoom(-.1)).pack(side="left")
        ttk.Button(z,text="100%",width=6,command=self._reset_zoom).pack(side="left",padx=4)
        ttk.Button(z,text="+",width=3,command=lambda:self._change_zoom(.1)).pack(side="left")
        vp=ttk.Frame(center); vp.pack(fill="both",expand=True,pady=(8,0))
        self.preview_canvas=tk.Canvas(vp,bg="white",highlightthickness=1)
        xb=ttk.Scrollbar(vp,orient="horizontal",command=self.preview_canvas.xview); yb=ttk.Scrollbar(vp,orient="vertical",command=self.preview_canvas.yview)
        self.preview_canvas.configure(xscrollcommand=xb.set,yscrollcommand=yb.set)
        self.preview_canvas.grid(row=0,column=0,sticky="nsew"); yb.grid(row=0,column=1,sticky="ns"); xb.grid(row=1,column=0,sticky="ew")
        vp.rowconfigure(0,weight=1); vp.columnconfigure(0,weight=1); self.workspace=self.preview_canvas
        self.preview_canvas.bind("<Button-1>",self._canvas_click)
        ttk.Label(right,text="INSPECTOR",style="HS.H2.TLabel").pack(anchor="w")
        self.inspector=tk.Text(right,width=29,state="disabled",wrap="word"); self.inspector.pack(fill="both",expand=True,pady=(8,8))
        box=ttk.LabelFrame(right,text="Selected Note",padding=8); box.pack(fill="x")
        ttk.Label(box,text="Duration").grid(row=0,column=0,sticky="w"); ttk.Entry(box,textvariable=self.duration_var,width=8).grid(row=0,column=1,padx=5); ttk.Button(box,text="Set",command=self._set_selected_duration).grid(row=0,column=2)
        ttk.Label(box,text="Lyrics").grid(row=1,column=0,sticky="w",pady=5); ttk.Entry(box,textvariable=self.lyrics_var,width=16).grid(row=1,column=1,padx=5); ttk.Button(box,text="Apply",command=self._set_selected_lyrics).grid(row=1,column=2)
        ttk.Label(box,text="Harmony").grid(row=2,column=0,sticky="w"); ttk.Entry(box,textvariable=self.harmony_var,width=16).grid(row=2,column=1,padx=5); ttk.Button(box,text="Set",command=self._set_selected_harmony).grid(row=2,column=2)

    def _transport(self):
        b=ttk.Frame(self,padding=7); b.pack(fill="x",side="bottom")
        for text,cmd in (("▶ Play",self._play_score),("❚❚ Pause",self._toggle_pause),("■ Stop",self._stop_playback)): ttk.Button(b,text=text,command=cmd).pack(side="left",padx=3)
        ttk.Separator(b,orient="vertical").pack(side="left",fill="y",padx=8)
        ttk.Label(b,text="Measure").pack(side="left"); ttk.Entry(b,textvariable=self.playback_measure_var,width=5).pack(side="left",padx=4); ttk.Button(b,text="Seek",command=self._seek_measure).pack(side="left")
        ttk.Checkbutton(b,text="Loop measure",variable=self.playback_loop_var,command=self._apply_loop_setting).pack(side="left",padx=10)
        ttk.Label(b,textvariable=self.playback_position_var).pack(side="right")

    def _status(self):
        v=get_version_info(); b=ttk.Frame(self,padding=(8,4)); b.pack(fill="x",side="bottom")
        ttk.Label(b,textvariable=self.status_var).pack(side="left"); ttk.Label(b,text=f"0.9.0 preview · build {v.build}").pack(side="right")

    def _reset_zoom(self): self.preview_zoom=1.0; self._refresh_workspace()
    def _show_part(self,e=None):
        s=self.parts_list.curselection()
        if not s or self.controller.score is None:return
        p=self.controller.score.parts[s[0]]
        self._set_text(self.inspector,f"PART\n\n{p.name}\nMeasures: {len(p.measures)}")

def main():
    ProfessionalShellHarmoniaApp().mainloop()
