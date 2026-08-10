from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from harmonia_studio.score import Score, Note, Pitch
from harmonia_studio.importers.omr import OMRResult, OMRSymbol

@dataclass
class VerificationEdit:
    action:str
    measure_index:int
    note_index:int
    before:str=""
    after:str=""

class OMRVerificationSession:
    def __init__(self,result:OMRResult,uncertain_threshold:float=0.7):
        self.original_result=result
        self.score=deepcopy(result.score)
        self.symbols=list(result.symbols)
        self.uncertain_threshold=uncertain_threshold
        self.edits:list[VerificationEdit]=[]
        self.approved=False

    def uncertain_symbols(self)->list[OMRSymbol]:
        return [s for s in self.symbols if s.confidence<self.uncertain_threshold]

    def correct_pitch(self,measure_index:int,note_index:int,pitch:Pitch)->None:
        note=self.score.parts[0].measures[measure_index].notes[note_index]
        before="" if note.pitch is None else f"{note.pitch.step}{note.pitch.octave}"
        note.pitch=deepcopy(pitch)
        self.edits.append(VerificationEdit("pitch",measure_index,note_index,before,f"{pitch.step}{pitch.octave}"))

    def delete_note(self,measure_index:int,note_index:int)->Note:
        note=self.score.parts[0].measures[measure_index].notes.pop(note_index)
        before="" if note.pitch is None else f"{note.pitch.step}{note.pitch.octave}"
        self.edits.append(VerificationEdit("delete",measure_index,note_index,before,""))
        return note

    def add_note(self,measure_index:int,note:Note)->None:
        self.score.parts[0].measures[measure_index].notes.append(deepcopy(note))
        idx=len(self.score.parts[0].measures[measure_index].notes)-1
        after="" if note.pitch is None else f"{note.pitch.step}{note.pitch.octave}"
        self.edits.append(VerificationEdit("add",measure_index,idx,"",after))

    def approve(self)->Score:
        self.approved=True
        self.score.metadata["omrVerified"]=True
        self.score.metadata["omrEditCount"]=len(self.edits)
        return deepcopy(self.score)
