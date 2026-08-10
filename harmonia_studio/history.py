from __future__ import annotations
from dataclasses import dataclass,field,asdict
from datetime import datetime,timezone
from uuid import uuid4
from copy import deepcopy
from harmonia_studio.score import Score

def _now(): return datetime.now(timezone.utc).isoformat()

@dataclass
class HistorySnapshot:
    id:str
    name:str
    kind:str
    timestamp:str
    score:dict
    metadata:dict=field(default_factory=dict)

@dataclass
class ProjectHistory:
    snapshots:list[HistorySnapshot]=field(default_factory=list)
    current_index:int=-1
    limit:int=100

    def commit(self,score:Score,name:str,kind:str="manual",metadata:dict|None=None)->HistorySnapshot:
        if self.current_index < len(self.snapshots)-1:
            self.snapshots=self.snapshots[:self.current_index+1]
        snap=HistorySnapshot(str(uuid4()),name,kind,_now(),deepcopy(score.to_dict()),deepcopy(metadata or {}))
        self.snapshots.append(snap)
        if len(self.snapshots)>self.limit:
            self.snapshots=self.snapshots[-self.limit:]
        self.current_index=len(self.snapshots)-1
        return snap

    def record_harmony_generation(self,score:Score,style:str)->HistorySnapshot:
        return self.commit(score,f"Harmony: {style}","harmony-generation",{"style":style})

    def record_import(self,score:Score,source_path:str)->HistorySnapshot:
        return self.commit(score,"Imported source","import-source",{"sourcePath":source_path})

    def named_version(self,score:Score,name:str)->HistorySnapshot:
        return self.commit(score,name,"named-version")

    def current(self)->Score|None:
        if 0<=self.current_index<len(self.snapshots):
            return Score.from_dict(deepcopy(self.snapshots[self.current_index].score))
        return None

    def undo(self)->Score|None:
        if self.current_index>0: self.current_index-=1
        return self.current()

    def redo(self)->Score|None:
        if self.current_index+1<len(self.snapshots): self.current_index+=1
        return self.current()

    def restore(self,identifier:str)->Score:
        for i,s in enumerate(self.snapshots):
            if s.id==identifier or s.name==identifier:
                self.current_index=i
                return Score.from_dict(deepcopy(s.score))
        raise KeyError(identifier)

    def to_dict(self)->dict:
        return {"currentIndex":self.current_index,"limit":self.limit,"snapshots":[asdict(s) for s in self.snapshots]}

    @classmethod
    def from_dict(cls,data:dict)->"ProjectHistory":
        snaps=[HistorySnapshot(**s) for s in data.get("snapshots",[])]
        idx=int(data.get("currentIndex",len(snaps)-1))
        idx=min(max(-1,idx),len(snaps)-1)
        return cls(snaps,idx,int(data.get("limit",100)))
