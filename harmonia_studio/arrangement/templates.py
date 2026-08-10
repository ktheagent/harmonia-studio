from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy

@dataclass(frozen=True)
class EnsembleInstrument:
    id:str
    name:str
    midi_program:int
    low:int
    high:int
    transposition:int=0
    polyphony:int=1
    role:str="harmony"

@dataclass
class EnsembleTemplate:
    id:str
    name:str
    instruments:list[EnsembleInstrument]
    description:str=""

V=lambda id,name,program,lo,hi,role="harmony",poly=1,trans=0:EnsembleInstrument(id,name,program,lo,hi,trans,poly,role)

TEMPLATES={
    "satb":EnsembleTemplate("satb","SATB Choir",[
        V("s","Soprano",52,60,81,"melody"),V("a","Alto",52,53,74),
        V("t","Tenor",52,48,69),V("b","Bass",52,36,60,"bass")]),
    "piano":EnsembleTemplate("piano","Piano",[V("p","Piano",0,21,108,"harmony",10)]),
    "piano_vocal":EnsembleTemplate("piano_vocal","Piano + Vocal",[
        V("v","Vocal",52,55,84,"melody"),V("p","Piano",0,21,108,"harmony",10)]),
    "string_quartet":EnsembleTemplate("string_quartet","String Quartet",[
        V("v1","Violin I",40,55,103,"melody"),V("v2","Violin II",40,55,100),
        V("va","Viola",41,48,88),V("vc","Cello",42,36,76,"bass")]),
    "brass":EnsembleTemplate("brass","Brass",[
        V("tp","Trumpet",56,54,82,"melody"),V("hn","Horn",60,41,77),
        V("tb","Trombone",57,40,72),V("tu","Tuba",58,28,58,"bass")]),
    "worship_band":EnsembleTemplate("worship_band","Worship Band",[
        V("v","Lead Vocal",52,55,84,"melody"),V("keys","Keys",0,36,96,"harmony",8),
        V("g","Guitar",27,40,88,"rhythm",6),V("bass","Bass",33,28,67,"bass")]),
    "jazz_combo":EnsembleTemplate("jazz_combo","Jazz Combo",[
        V("lead","Lead",65,48,88,"melody"),V("p","Piano",0,28,100,"harmony",8),
        V("bass","Upright Bass",32,28,67,"bass")]),
    "full_band":EnsembleTemplate("full_band","Full Band",[
        V("v","Lead",52,55,84,"melody"),V("keys","Keys",0,28,100,"harmony",8),
        V("g","Guitar",27,40,88,"rhythm",6),V("bass","Bass",33,28,67,"bass"),
        V("brass","Brass Section",61,40,86,"harmony",4)]),
    "orchestra":EnsembleTemplate("orchestra","Orchestra",[
        V("fl","Flute",73,60,96,"melody"),V("vln","Violins",48,55,103,"harmony",8),
        V("vla","Violas",49,48,88,"harmony",6),V("vc","Cellos",50,36,76,"harmony",4),
        V("cb","Contrabass",43,28,60,"bass"),V("hn","Horns",60,41,77,"harmony",4)]),
}

def get_template(template_id:str)->EnsembleTemplate:
    if template_id not in TEMPLATES:
        raise KeyError(template_id)
    return deepcopy(TEMPLATES[template_id])

def custom_template(name:str,instruments:list[EnsembleInstrument])->EnsembleTemplate:
    if not instruments: raise ValueError("Custom ensemble requires instruments")
    return EnsembleTemplate("custom",name,list(instruments),"User-defined ensemble")
