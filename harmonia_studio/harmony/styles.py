from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy
from harmonia_studio.score import Score
from .diatonic import HarmonyPlan, HarmonyChoice, harmonize_diatonic
from .satb import harmonize_satb, SATBOptions
from .voice_leading import VoiceLeadingProfile, validate_voice_leading
from harmonia_studio.analysis.tonal import NAMES

@dataclass(frozen=True)
class StyleProfile:
    id:str
    name:str
    description:str
    chord_vocabulary:tuple[str,...]
    chromaticism:float=0.0
    extension_level:int=0
    preferred_progressions:tuple[tuple[int,...],...]=()
    validation_strictness:str="normal"
    bass_behavior:str="smooth"
    rhythmic_character:str=""

@dataclass
class StyleResult:
    profile:StyleProfile
    plan:HarmonyPlan
    score:Score
    warnings:list

STYLE_REGISTRY:dict[str,StyleProfile]={
    "blues":StyleProfile(
        "blues","Blues",
        "Twelve-bar dominant-seventh blues with turnaround support.",
        ("dominant-seventh","minor-seventh"),
        chromaticism=0.35,
        extension_level=2,
        preferred_progressions=((0,0,0,0,5,5,0,0,7,5,0,7),),
        validation_strictness="blues",
        bass_behavior="walking",
        rhythmic_character="twelve-bar form with turnaround",
    ),
    "afrobeat":StyleProfile(
        "afrobeat","Afrobeat",
        "Groove-first modal/vamp harmony profile designed for long-form rhythmic arrangements.",
        ("major","minor","dominant-seventh"),
        chromaticism=0.18,
        extension_level=1,
        preferred_progressions=((0,10),(0,5)),
        validation_strictness="normal",
        bass_behavior="ostinato",
        rhythmic_character="long vamp, interlocking guitar/keys, repeated bass ostinato",
    ),
    "highlife":StyleProfile(
        "highlife","Highlife",
        "Ghanaian highlife-oriented harmonic loop with configurable guitar/keyboard accompaniment metadata.",
        ("major","minor","dominant-seventh"),
        chromaticism=0.2,
        extension_level=1,
        preferred_progressions=((0,0,5,7,0),),
        validation_strictness="normal",
        bass_behavior="active",
        rhythmic_character="interlocking guitar/keyboard highlife accompaniment",
    ),
    "rnb":StyleProfile(
        "rnb","R&B / Neo-Soul",
        "Extended harmony, slash-bass motion and chromatic voice-leading colors.",
        ("major-seventh","minor-seventh","dominant-seventh","diminished"),
        chromaticism=0.6,
        extension_level=4,
        preferred_progressions=((0,9,2,7),(0,4,5,1)),
        validation_strictness="rnb",
        bass_behavior="smooth",
        rhythmic_character="syncopated sustained voicings",
    ),
    "pop":StyleProfile(
        "pop","Pop",
        "Contemporary loop-based harmony with smooth, singable voicings.",
        ("major","minor"),
        chromaticism=0.12,
        extension_level=1,
        preferred_progressions=((0,7,9,5),(9,5,0,7)),
        validation_strictness="pop",
        bass_behavior="smooth",
        rhythmic_character="four-chord loop with optional inversions",
    ),
    "jazz":StyleProfile(
        "jazz","Jazz",
        "Extended functional harmony with ii-V-I, substitutions and altered dominant options.",
        ("major-seventh","minor-seventh","dominant-seventh","half-diminished","diminished"),
        chromaticism=0.7,
        extension_level=4,
        preferred_progressions=((2,7,0),(9,2,7,0),(10,0)),
        validation_strictness="jazz",
        bass_behavior="walking",
        rhythmic_character="two-feel to walking harmonic motion",
    ),
    "gospel":StyleProfile(
        "gospel","Gospel",
        "Functional gospel harmony with secondary-dominant, diminished and chromatic-bass vocabulary.",
        ("major","minor","diminished","dominant-seventh","major-seventh","minor-seventh"),
        chromaticism=0.45,
        extension_level=2,
        preferred_progressions=((0,9,2,7),(0,5,1,2,7,0)),
        validation_strictness="normal",
        bass_behavior="active",
        rhythmic_character="cadential pushes and passing harmony",
    ),
    "classical":StyleProfile(
        "classical","Classical Chorale",
        "Strict four-part functional harmony with restrained chromaticism.",
        ("major","minor","diminished","dominant-seventh"),
        chromaticism=0.08,
        extension_level=1,
        preferred_progressions=((0,5,2,7,0),(0,9,2,7,0)),
        validation_strictness="classical",
        bass_behavior="smooth",
        rhythmic_character="phrase-aware chordal writing",
    ),
    "hymn":StyleProfile(
        "hymn","Traditional Hymn",
        "Conservative functional four-part hymn harmony.",
        ("major","minor","diminished"),
        chromaticism=0.05,
        extension_level=0,
        preferred_progressions=((0,5,7,0),(0,2,7,0)),
        validation_strictness="strict",
        bass_behavior="smooth",
        rhythmic_character="mostly one harmony per measure",
    ),
}

def get_style(style_id:str)->StyleProfile:
    if style_id not in STYLE_REGISTRY:
        raise KeyError(f"Unknown harmony style: {style_id}")
    return STYLE_REGISTRY[style_id]

def _stylize_plan(plan:HarmonyPlan,profile:StyleProfile,complexity:str)->HarmonyPlan:
    choices=list(plan.choices)
    if not choices:
        return plan
    tonic=NAMES.index(plan.key)
    updated=[]
    for idx,c in enumerate(choices):
        root=c.root_pc; quality=c.quality
        if profile.id=="gospel":
            level={"simple":0,"balanced":1,"modern":1,"advanced":2,"creative":2}.get(complexity.lower(),1)
            # Retain melody-safe baseline but add characteristic dominant/diminished motion.
            if idx % 4 == 2:
                root=(tonic+7)%12; quality="dominant-seventh"
            elif level>=1 and idx % 4 == 1:
                root=(tonic+2)%12; quality="minor-seventh"
            elif level>=2 and idx % 4 == 3 and idx != len(choices)-1:
                root=(tonic+1)%12; quality="diminished"
        elif profile.id=="jazz":
            level={"conservative":0,"simple":0,"balanced":1,"stylistic":1,"creative":2,"advanced":2}.get(complexity.lower(),1)
            cycle=idx % 4
            if cycle==0:
                root=tonic; quality="major-seventh" if plan.mode=="major" else "minor-seventh"
            elif cycle==1:
                root=(tonic+2)%12; quality="minor-seventh"
            elif cycle==2:
                root=(tonic+7)%12; quality="dominant-seventh"
                if level>=2 and idx!=len(choices)-1:
                    root=(tonic+1)%12  # tritone substitute for V in major context
            else:
                root=tonic; quality="major-seventh" if plan.mode=="major" else "minor-seventh"
            if level>=1 and idx%8==6:
                root=(tonic+10)%12; quality="dominant-seventh"  # backdoor dominant color
        elif profile.id=="pop":
            progression=(0,7,9,5) if plan.mode=="major" else (0,8,3,10)
            rel=progression[idx%len(progression)]
            root=(tonic+rel)%12
            if plan.mode=="major":
                quality="minor" if rel==9 else "major"
            else:
                quality="major" if rel in {3,8,10} else "minor"
        elif profile.id=="rnb":
            level={"conservative":0,"simple":0,"balanced":1,"stylistic":1,"creative":2,"advanced":2}.get(complexity.lower(),1)
            progression=(0,9,2,7)
            rel=progression[idx%4]; root=(tonic+rel)%12
            quality={0:"major-seventh",9:"minor-seventh",2:"minor-seventh",7:"dominant-seventh"}[rel]
            inversion=1 if level>=1 and idx%4 in {1,3} else c.inversion
            if level>=2 and idx%8==3:
                root=(root+1)%12; quality="diminished"
            c=HarmonyChoice(c.measure_index,c.onset,root,NAMES[root],quality,inversion,c.score)
            root=c.root_pc; quality=c.quality
        elif profile.id=="highlife":
            progression=(0,0,5,7,0)
            rel=progression[idx%len(progression)]
            root=(tonic+rel)%12
            quality="dominant-seventh" if rel==7 and complexity.lower() in {"advanced","creative"} else "major"
        elif profile.id=="afrobeat":
            # Keep harmony intentionally sparse; rhythm/ostinato carries much of the style.
            progression=(0,10) if plan.mode=="major" else (0,10)
            rel=progression[(idx//2)%len(progression)]
            root=(tonic+rel)%12
            quality="major" if rel in {0,10} and plan.mode=="major" else ("minor" if rel==0 else "major")
        elif profile.id=="blues":
            progression=(0,0,0,0,5,5,0,0,7,5,0,7)
            rel=progression[idx%12]
            root=(tonic+rel)%12
            quality="dominant-seventh"
        updated.append(HarmonyChoice(c.measure_index,c.onset,root,NAMES[root],quality,c.inversion,c.score))
    # Preserve final tonic resolution.
    if profile.id in {"gospel","jazz"} and updated:
        c=updated[-1]; root=tonic
        end_quality=("major-seventh" if profile.id=="jazz" and plan.mode=="major" else
                     "minor-seventh" if profile.id=="jazz" and plan.mode=="minor" else
                     "major" if plan.mode=="major" else "minor")
        updated[-1]=HarmonyChoice(c.measure_index,c.onset,root,NAMES[root],end_quality,0,c.score)
    return HarmonyPlan(plan.key,plan.mode,updated,plan.preserve_melody)

def harmonize_style(score:Score,style_id:str,complexity:str="balanced")->StyleResult:
    profile=get_style(style_id)
    density="measure"
    plan=harmonize_diatonic(score,density)
    plan=_stylize_plan(plan,profile,complexity)
    options=SATBOptions(bass_movement=profile.bass_behavior)
    arranged=harmonize_satb(score,plan,options)
    vp=VoiceLeadingProfile()
    if profile.validation_strictness=="strict":
        vp.max_leap=10
        vp.max_upper_spacing=12
    elif profile.validation_strictness=="classical":
        vp.max_leap=8
        vp.max_upper_spacing=12
        vp.forbid_parallel_fifths=True
        vp.forbid_parallel_octaves=True
        vp.check_hidden_perfects=True
    elif profile.validation_strictness=="jazz":
        vp.max_leap=14
        vp.forbid_parallel_fifths=False
        vp.check_hidden_perfects=False
    elif profile.validation_strictness=="rnb":
        vp.max_leap=14
        vp.forbid_parallel_fifths=False
        vp.check_hidden_perfects=False
    elif profile.validation_strictness=="blues":
        vp.max_leap=14
        vp.forbid_parallel_fifths=False
        vp.check_hidden_perfects=False
    warnings=validate_voice_leading(arranged,vp)
    arranged.metadata["harmonyStyle"]=profile.id
    arranged.metadata["harmonyComplexity"]=complexity
    return StyleResult(profile,plan,arranged,warnings)
