from __future__ import annotations
from dataclasses import dataclass
from .chords import DetectedChord, analyze_chords
from .tonal import KeyEstimate, analyze_tonality, NAMES
from harmonia_studio.score import Score

ROMANS_MAJOR={0:"I",2:"ii",4:"iii",5:"IV",7:"V",9:"vi",11:"vii°"}
ROMANS_MINOR={0:"i",2:"ii°",3:"III",5:"iv",7:"V",8:"VI",10:"VII"}
FUNCTIONS={
    "I":"tonic","i":"tonic","vi":"tonic","III":"tonic",
    "ii":"predominant","ii°":"predominant","IV":"predominant","iv":"predominant",
    "V":"dominant","vii°":"dominant","VII":"dominant"
}

@dataclass(frozen=True)
class FunctionalChord:
    chord:DetectedChord
    roman:str
    function:str
    secondary_target:str=""
    borrowed:bool=False
    tonicization:bool=False

def _tonic_pc(key:KeyEstimate)->int:
    return NAMES.index(key.tonic)

def _expected_quality(roman:str)->str:
    if roman in {"I","IV","V","III","VI","VII"}: return "major"
    if roman in {"i","ii","iii","iv","vi"}: return "minor"
    if "°" in roman: return "diminished"
    return ""

def analyze_function(chord:DetectedChord,key:KeyEstimate)->FunctionalChord:
    tonic=_tonic_pc(key)
    rel=(chord.root-tonic)%12
    table=ROMANS_MAJOR if key.mode=="major" else ROMANS_MINOR
    roman=table.get(rel,"")
    secondary_target=""
    borrowed=False
    tonicization=False

    # A dominant-seventh chord a fifth above a diatonic target is V/x.
    if chord.quality=="dominant-seventh":
        target=(chord.root+5)%12
        target_rel=(target-tonic)%12
        target_roman=table.get(target_rel,"")
        if target_roman and target_rel!=0:
            clean=target_roman.replace("°","")
            roman=f"V/{clean}"
            secondary_target=clean
            tonicization=True

    if not roman:
        # Common chromatic/borrowed root representation.
        degree_names={1:"♭II",3:"♭III",6:"♭V",8:"♭VI",10:"♭VII"}
        roman=degree_names.get(rel,f"chrom({rel})")
        borrowed=True
    elif "/" not in roman:
        expected=_expected_quality(roman)
        if expected and not chord.quality.startswith(expected) and not (
            roman=="V" and chord.quality=="dominant-seventh"
        ):
            borrowed=True

    base=roman.split("/")[0]
    function="chromatic"
    if base=="V": function="dominant"
    elif roman in FUNCTIONS: function=FUNCTIONS[roman]
    elif borrowed: function="borrowed"
    return FunctionalChord(chord,roman,function,secondary_target,borrowed,tonicization)

def analyze_functional_harmony(score:Score)->list[FunctionalChord]:
    tonal=analyze_tonality(score)
    chords=analyze_chords(score)
    out=[]
    for chord in chords:
        key=tonal.local_keys[chord.measure_index] if chord.measure_index<len(tonal.local_keys) else tonal.global_key
        out.append(analyze_function(chord,key))
    return out
