from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass
class HarmonizationSettings:
    style:str="hymn"
    complexity:str="balanced"
    harmonic_density:str="measure"
    chromaticism:float=0.2
    chord_substitutions:bool=True
    bass_movement:str="smooth"
    voice_leading_strictness:str="normal"
    number_of_voices:int=4
    preserve_melody:bool=True
    preserve_original_harmony:bool=False
    modulation_level:float=0.2
    chord_extensions:int=1
    rhythmic_density:float=0.5

    def validate(self)->"HarmonizationSettings":
        if self.complexity not in {"conservative","simple","balanced","stylistic","modern","creative","advanced"}:
            raise ValueError("Invalid complexity")
        if self.harmonic_density not in {"measure","beat"}:
            raise ValueError("Invalid harmonic density")
        if not 1<=self.number_of_voices<=16:
            raise ValueError("number_of_voices must be 1..16")
        for name in ["chromaticism","modulation_level","rhythmic_density"]:
            val=float(getattr(self,name))
            if not 0<=val<=1:
                raise ValueError(f"{name} must be 0..1")
        if not 0<=self.chord_extensions<=4:
            raise ValueError("chord_extensions must be 0..4")
        return self

    def to_dict(self)->dict:
        self.validate()
        return asdict(self)
