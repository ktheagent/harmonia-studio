# MASTER DEVELOPMENT PROMPT

## AI Music Harmonization & Arrangement Software

Build a professional desktop music harmonization application progressively, **one feature at a time**, with a permanent checkpoint after every successfully completed feature.

Do not attempt to build the whole application in one pass.

The software should ultimately allow users to import musical material from notation files, MIDI, PDF/image scores, and audio; analyze the music; reharmonize it accurately into multiple musical styles; edit the generated score; play it back; and export it into professional music formats.

---

# 1. DEVELOPMENT PRINCIPLE

Follow this exact development cycle for EVERY feature:

1. Inspect the existing project.
2. Confirm the previous checkpoint builds and tests successfully.
3. Create only the next requested feature.
4. Do not refactor unrelated working code.
5. Add automated tests for the feature.
6. Run all existing tests.
7. Build the application.
8. Fix all errors introduced by the feature.
9. Verify previous functionality still works.
10. Update documentation.
11. Save a development checkpoint.
12. Commit the checkpoint to Git.
13. Record the commit SHA.
14. Tag major milestones where appropriate.
15. Only then proceed to the next feature.

Never begin the next feature while the current feature is failing.

---

# 2. CHECKPOINT RULES

Every feature must produce a recoverable Git checkpoint.

Use the following convention:

```
checkpoint/001-project-foundation
checkpoint/002-score-data-model
checkpoint/003-musicxml-import
checkpoint/004-midi-import
checkpoint/005-score-display
...

```

Git commit format:

```
Feature 001: Project foundation
Feature 002: Unified musical score model
Feature 003: Add MusicXML import

```

For major working releases, also create a Git tag:

```
v0.1.0-foundation
v0.2.0-notation
v0.3.0-harmonization
v0.4.0-pdf-import
v0.5.0-audio-import
v1.0.0

```

Each checkpoint must contain:

```
Checkpoint number:
Feature:
Status:
Application version:
Build number:
Git commit SHA:
Files added:
Files modified:
Tests added:
Tests passed:
Build status:
Known limitations:
Next feature:

```

Never claim that a checkpoint is complete unless the project builds and its required tests pass.

---

# 3. PROJECT IDENTITY

Product name:

AI Music Harmonizer

Working project name:

Harmonia Studio

Core purpose:

Import → Analyze → Harmonize → Arrange → Edit → Playback → Export

The architecture must be modular so individual engines can later be replaced without rewriting the whole application.

---

# 4. TARGET ARCHITECTURE

Use these major modules:

```
Application Shell
    │
    ├── Project Manager
    │
    ├── Import Engine
    │      ├── MusicXML
    │      ├── MIDI
    │      ├── PDF / Image OMR
    │      └── Audio Transcription
    │
    ├── Unified Score Engine
    │
    ├── Music Analysis Engine
    │      ├── Key detection
    │      ├── Scale analysis
    │      ├── Chord detection
    │      ├── Phrase analysis
    │      └── Cadence detection
    │
    ├── Harmonization Engine
    │      ├── Classical
    │      ├── Hymn
    │      ├── Gospel
    │      ├── Jazz
    │      ├── Pop
    │      ├── R&B / Neo-Soul
    │      ├── Highlife
    │      ├── Afrobeat
    │      ├── Blues
    │      └── Custom styles
    │
    ├── Arrangement Engine
    │
    ├── Validation Engine
    │
    ├── Score Editor
    │
    ├── Playback Engine
    │
    ├── AI Music Assistant
    │
    └── Export Engine

```

All import formats must eventually be converted into the same internal musical representation before analysis or harmonization.

---

# 5. UNIFIED MUSICAL SCORE MODEL

Design an internal music model capable of representing:

- Project
- Score
- Part
- Instrument
- Staff
- Voice
- Measure
- Beat
- Note
- Rest
- Pitch
- Octave
- Duration
- Dots
- Tuplets
- Ties
- Slurs
- Articulation
- Dynamic
- Tempo
- Time signature
- Key signature
- Chord symbol
- Harmony
- Lyrics
- Clef
- Repeat
- Volta
- Rehearsal mark
- Expression
- Transposition
- MIDI program
- Sound assignment
- Metadata

All analysis, harmonization, playback, editing, and export systems must work against this unified representation rather than directly manipulating imported files.

---

# 6. FEATURE DEVELOPMENT ROADMAP

Build features in the following order.

## FEATURE 001 — Project Foundation

Create the application shell.

Required:

- desktop application project;
- modular folder structure;
- dependency management;
- logging;
- global error handling;
- settings infrastructure;
- test infrastructure;
- CI build;
- About screen;
- application version information.

Checkpoint:

```
checkpoint/001-project-foundation

```

Do not add harmonization yet.

---

## FEATURE 002 — Project Management

Add:

- New Project;
- Open Project;
- Save Project;
- Save As;
- recent projects;
- autosave;
- recovery after abnormal shutdown;
- project metadata;
- project version compatibility.

Project files must not destructively overwrite source music files.

Checkpoint:

```
checkpoint/002-project-management

```

---

## FEATURE 003 — Unified Score Data Model

Implement the internal score representation.

Add serialization and deserialization tests.

Required tests:

- notes preserve pitch;
- durations preserve value;
- multiple voices survive save/load;
- measures preserve meter;
- chord symbols survive round-trip;
- lyrics survive round-trip.

Checkpoint:

```
checkpoint/003-unified-score-model

```

---

## FEATURE 004 — MusicXML Import

Support:

```
.musicxml
.xml
.mxl

```

Import:

- notes;
- rests;
- measures;
- voices;
- staves;
- key signatures;
- time signatures;
- tempo;
- chord symbols;
- lyrics;
- articulations;
- dynamics;
- instrument information.

Create round-trip tests using sample scores.

Checkpoint:

```
checkpoint/004-musicxml-import

```

---

## FEATURE 005 — MIDI Import

Support:

```
.mid
.midi

```

Detect:

- tracks;
- channels;
- pitches;
- note durations;
- velocity;
- tempo;
- meter where available;
- instrument assignments.

Add quantization options.

Checkpoint:

```
checkpoint/005-midi-import

```

---

## FEATURE 006 — Score Renderer

Create professional notation display.

Required:

- staves;
- clefs;
- notes;
- rests;
- barlines;
- beams;
- ties;
- accidentals;
- lyrics;
- chord symbols;
- multiple voices;
- zoom;
- page mode;
- continuous mode.

Checkpoint:

```
checkpoint/006-score-renderer

```

---

## FEATURE 007 — Score Editing

Allow users to:

- add notes;
- remove notes;
- move notes;
- change duration;
- transpose;
- copy/paste;
- edit lyrics;
- edit chord symbols;
- add/remove measures;
- undo;
- redo.

Every destructive action must support undo.

Checkpoint:

```
checkpoint/007-score-editing

```

---

## FEATURE 008 — Playback Engine

Provide:

- Play;
- Pause;
- Stop;
- Seek;
- metronome;
- tempo adjustment;
- loop selected measures;
- solo;
- mute;
- per-part volume;
- playback cursor.

Checkpoint:

```
checkpoint/008-playback

```

---

## FEATURE 009 — Tonal Analysis

Analyze:

- global key;
- local key;
- major/minor/modal context;
- scales;
- accidentals;
- modulation candidates;
- tonal center confidence.

Results must be inspectable by the user.

Checkpoint:

```
checkpoint/009-tonal-analysis

```

---

## FEATURE 010 — Chord Analysis

Determine:

- chord root;
- quality;
- inversion;
- extensions;
- alterations;
- suspensions;
- slash bass;
- harmonic rhythm.

Display detected chord symbols above the score.

Users must be able to correct analysis manually.

Checkpoint:

```
checkpoint/010-chord-analysis

```

---

## FEATURE 011 — Functional Harmony Analysis

Add Roman numeral and functional analysis.

Support concepts such as:

- tonic;
- predominant;
- dominant;
- secondary dominant;
- borrowed chords;
- modal interchange;
- diminished functions;
- tonicization;
- modulation;
- cadences.

Checkpoint:

```
checkpoint/011-functional-analysis

```

---

## FEATURE 012 — Phrase and Cadence Detection

Analyze:

- phrases;
- phrase boundaries;
- motifs;
- cadences;
- repetitions;
- sections.

Support:

- authentic cadence;
- imperfect cadence;
- plagal cadence;
- deceptive cadence;
- half cadence.

Checkpoint:

```
checkpoint/012-phrase-analysis

```

---

# 7. HARMONIZATION ENGINE

The melody must normally remain unchanged unless the user explicitly allows melodic modification.

The harmonizer must generate several candidate harmonizations.

Default modes:

```
Conservative
Balanced
Creative

```

Each candidate receives a quality score.

---

## FEATURE 013 — Basic Diatonic Harmonization

Generate harmony using diatonic chords.

Support:

- triads;
- inversions;
- functional progression;
- cadence-aware choices;
- smooth bass movement.

Checkpoint:

```
checkpoint/013-basic-harmonization

```

---

## FEATURE 014 — Voice Leading Engine

Implement voice-leading validation.

Check:

- voice crossing;
- overlapping;
- range violations;
- excessive leaps;
- unresolved leading tones;
- unresolved sevenths;
- parallel fifths;
- parallel octaves;
- hidden/direct perfect intervals;
- spacing.

Allow rules to vary by musical style.

Checkpoint:

```
checkpoint/014-voice-leading

```

---

## FEATURE 015 — SATB Harmonization

Create soprano/alto/tenor/bass arrangements.

Controls:

- vocal ranges;
- maximum intervals;
- doubling;
- closed/open position;
- melody voice selection;
- bass movement preference.

Checkpoint:

```
checkpoint/015-satb

```

---

## FEATURE 016 — Traditional Hymn Style

Implement hymn harmonization.

Characteristics:

- strong functional harmony;
- four-part writing;
- conservative chromaticism;
- controlled inversions;
- appropriate cadences.

Checkpoint:

```
checkpoint/016-hymn-style

```

---

## FEATURE 017 — Classical Chorale Style

Implement stricter contrapuntal/chorale rules.

Add validation profiles suitable for classical four-part writing.

Checkpoint:

```
checkpoint/017-classical-style

```

---

## FEATURE 018 — Gospel Harmonization

Support:

- passing diminished chords;
- secondary dominants;
- dominant chains;
- chromatic bass movement;
- slash chords;
- altered dominants;
- gospel cadences;
- richer voicing.

Controls:

```
Simple Gospel
Modern Gospel
Advanced Gospel

```

Checkpoint:

```
checkpoint/018-gospel-style

```

---

## FEATURE 019 — Jazz Harmonization

Support:

- 7th chords;
- 9ths;
- 11ths;
- 13ths;
- altered dominants;
- ii-V-I;
- tritone substitution;
- backdoor progressions;
- secondary dominants;
- diminished substitutions;
- modal interchange;
- chromatic approach harmony.

Checkpoint:

```
checkpoint/019-jazz-style

```

---

## FEATURE 020 — Pop Harmonization

Support contemporary pop progressions and smooth modern voicings.

Checkpoint:

```
checkpoint/020-pop-style

```

---

## FEATURE 021 — R&B / Neo-Soul

Support:

- extended harmony;
- slash chords;
- chromatic voice movement;
- upper structures;
- maj7/9/11 harmony;
- sophisticated substitutions.

Checkpoint:

```
checkpoint/021-rnb-neosoul

```

---

## FEATURE 022 — Highlife Harmonization

Develop style rules for Highlife harmonic movement, guitar/piano voicings, rhythmic characteristics, and appropriate dominant-tonic relationships.

Keep the musical-style rules in configurable data rather than hard-coding them throughout the application.

Checkpoint:

```
checkpoint/022-highlife-style

```

---

## FEATURE 023 — Afrobeat Harmonization

Implement appropriate:

- harmonic loops;
- modal harmony;
- rhythmic accompaniment;
- bass relationships;
- keyboard/guitar patterns.

Checkpoint:

```
checkpoint/023-afrobeat-style

```

---

## FEATURE 024 — Blues Harmonization

Support:

- blues form;
- dominant seventh harmony;
- turnarounds;
- substitutions;
- jazz-blues options.

Checkpoint:

```
checkpoint/024-blues-style

```

---

# 8. HARMONIZATION CONTROLS

## FEATURE 025 — Harmonization Control Panel

Provide user controls for:

- style;
- complexity;
- harmonic density;
- chromaticism;
- chord substitutions;
- bass movement;
- voice-leading strictness;
- number of voices;
- preserve melody;
- preserve original harmony;
- modulation level;
- chord extensions;
- rhythmic density.

Checkpoint:

```
checkpoint/025-harmonization-controls

```

---

## FEATURE 026 — Multiple Harmony Candidates

Generate at least three options:

```
Candidate A — Conservative
Candidate B — Stylistic
Candidate C — Creative

```

Allow A/B comparison and instant playback.

Checkpoint:

```
checkpoint/026-harmony-candidates

```

---

## FEATURE 027 — Measure-Level Reharmonization

Allow users to select specific measures and regenerate only that region.

Never alter unselected music.

Checkpoint:

```
checkpoint/027-region-reharmonization

```

---

# 9. ARRANGEMENT

## FEATURE 028 — Instrument/Ensemble Templates

Provide:

- SATB Choir;
- Piano;
- Piano + Vocal;
- String Quartet;
- Brass;
- Worship Band;
- Jazz Combo;
- Full Band;
- Orchestra;
- Custom Ensemble.

Checkpoint:

```
checkpoint/028-ensemble-templates

```

---

## FEATURE 029 — Automatic Arrangement

Generate playable parts from harmony.

Respect:

- instrument ranges;
- transposition;
- polyphony;
- playability;
- voice distribution.

Checkpoint:

```
checkpoint/029-auto-arrangement

```

---

# 10. PDF AND IMAGE IMPORT

## FEATURE 030 — PDF Import Framework

Import PDF pages and prepare them for optical music recognition.

Do NOT attempt harmonization directly from PDF pixels.

Checkpoint:

```
checkpoint/030-pdf-framework

```

---

## FEATURE 031 — Optical Music Recognition

Convert printed notation into the unified score model.

Support:

```
PDF
PNG
JPG
JPEG
TIFF

```

Detect recognition confidence.

Checkpoint:

```
checkpoint/031-omr

```

---

## FEATURE 032 — OMR Verification Workspace

Show:

```
Original Score | Recognized Score

```

Highlight uncertain symbols.

Allow manual correction before harmonization.

Checkpoint:

```
checkpoint/032-omr-verification

```

---

# 11. AUDIO TRANSCRIPTION

## FEATURE 033 — Audio Import

Support:

```
WAV
MP3
FLAC
AAC
M4A

```

Checkpoint:

```
checkpoint/033-audio-import

```

---

## FEATURE 034 — Melody Transcription

Detect predominant melody and convert it into editable notation.

Show confidence values.

Checkpoint:

```
checkpoint/034-melody-transcription

```

---

## FEATURE 035 — Audio Chord Recognition

Detect chord progressions from audio.

Allow manual correction.

Checkpoint:

```
checkpoint/035-audio-chords

```

---

## FEATURE 036 — Tempo and Meter Detection

Detect:

- BPM;
- beat positions;
- meter;
- pickup measures where possible.

Checkpoint:

```
checkpoint/036-tempo-meter

```

---

# 12. EXPORT

## FEATURE 037 — MusicXML Export

Export the complete editable score.

Validate exported files by re-importing them.

Checkpoint:

```
checkpoint/037-musicxml-export

```

---

## FEATURE 038 — MIDI Export

Export all appropriate parts, instruments, tempo, and timing.

Checkpoint:

```
checkpoint/038-midi-export

```

---

## FEATURE 039 — PDF Score Export

Create printable engraved scores.

Options:

- Full Score;
- Individual Parts;
- Lead Sheet;
- Chord Chart;
- SATB Score.

Checkpoint:

```
checkpoint/039-pdf-export

```

---

## FEATURE 040 — Audio Export

Export playback as:

```
WAV
MP3

```

Checkpoint:

```
checkpoint/040-audio-export

```

---

## FEATURE 041 — Practice Track Export

Create individual rehearsal tracks.

Examples:

```
Soprano emphasized
Alto emphasized
Tenor emphasized
Bass emphasized
Instrument-only
Full mix

```

Checkpoint:

```
checkpoint/041-practice-tracks

```

---

# 13. QUALITY VALIDATION

## FEATURE 042 — Harmony Quality Analyzer

Score each generated arrangement for:

```
Melody preservation
Voice leading
Range compliance
Harmonic consistency
Cadence quality
Style consistency
Playability
Rhythmic consistency

```

Present results such as:

```
Melody preservation: 100%
Voice leading: 96%
Style consistency: 93%
Playability: 98%

Warnings:
Parallel fifths: 1
Range violations: 0
Unresolved tendency tones: 1

```

Checkpoint:

```
checkpoint/042-quality-analysis

```

---

# 14. AI MUSIC ASSISTANT

## FEATURE 043 — Natural Language Music Commands

Users should eventually be able to enter commands such as:

```
Reharmonize measures 9–16 in modern gospel style.

Keep the soprano exactly the same.

Make the tenor easier.

Give the bass more movement.

Change the final cadence to a richer jazz ending.

Turn this melody into SATB.

Add a piano accompaniment.

Create three alternatives for bars 17–24.

```

The AI layer must translate requests into structured musical operations.

It must NOT directly bypass the validation engine.

Checkpoint:

```
checkpoint/043-ai-assistant

```

---

# 15. HISTORY AND NON-DESTRUCTIVE EDITING

## FEATURE 044 — Complete Project History

Maintain:

- undo;
- redo;
- snapshots;
- named versions;
- harmony generations;
- imported source versions.

Users must be able to restore previous harmonizations.

Checkpoint:

```
checkpoint/044-project-history

```

---

# 16. AUTOMATIC FEATURE CHECKPOINT FILE

At the completion of each feature, create/update:

```
docs/CHECKPOINTS.md

```

Use this structure:

```
# Development Checkpoints

## Feature 001 — Project Foundation

Status: PASSED

Version:
Build:

Commit:

Implemented:
- ...

Tests:
- ...

Build:
- Passed/Failed

Known limitations:
- ...

Next:
- Feature 002

```

Also create:

```
docs/ARCHITECTURE.md
docs/FEATURES.md
docs/TESTING.md
docs/FILE_FORMAT_SUPPORT.md

```

Keep these synchronized with the implementation.

---

# 17. TESTING REQUIREMENTS

For every feature create:

1. unit tests;
2. integration tests where appropriate;
3. regression tests for previously discovered bugs.

Before checkpoint creation run the complete test suite.

Never disable a failing test merely to create a passing build.

Never mark a test skipped unless its reason is explicitly documented.

---

# 18. MUSICAL VALIDATION TEST LIBRARY

Maintain reference test scores covering:

- major keys;
- minor keys;
- common meters;
- compound meters;
- chromatic melodies;
- modulating music;
- hymn melodies;
- jazz standards/test progressions;
- gospel progressions;
- SATB examples;
- monophonic melody;
- polyphonic scores.

Where copyright applies, use original or public-domain test material.

---

# 19. IMPORT/EXPORT ROUND-TRIP TESTING

When applicable use:

```
Original
   ↓
Import
   ↓
Unified Score
   ↓
Export
   ↓
Re-import
   ↓
Compare

```

Test preservation of:

- pitches;
- durations;
- measure count;
- voices;
- tempo;
- key;
- meter;
- lyrics;
- chord symbols.

---

# 20. FAILURE POLICY

If implementation fails:

STOP.

Do not begin another feature.

Report:

```
Feature:
Checkpoint:
Failure:
Exact error:
Affected files:
Tests failing:
Build result:
Suspected cause:
Recommended fix:
Repository state:
Last known good checkpoint:

```

Restore the last working checkpoint if necessary.

Never hide an error by removing functionality.

---

# 21. SOURCE CONTROL SAFETY

Before modifying a feature:

```
git status
git log

```

Confirm that the project is at the expected checkpoint.

Never use:

```
git reset --hard
git clean -fd
git push --force

```

unless explicitly authorized.

Never delete user-created music projects during application development.

---

# 22. DATA SAFETY

Source music files must be treated as read-only unless the user explicitly chooses overwrite.

Imported files should create internal project copies/references.

Autosave application projects independently from source material.

Protect:

- user compositions;
- lyrics;
- generated arrangements;
- custom style definitions;
- settings;
- instrument libraries.

---

# 23. PLUGIN-READY DESIGN

Do not tightly couple music-analysis engines to the UI.

Design interfaces so future engines can be added for:

- OMR;
- audio transcription;
- chord recognition;
- AI models;
- synthesizers;
- notation rendering;
- export formats;
- harmonization styles.

---

# 24. CUSTOM STYLE ENGINE

Eventually allow style definitions such as:

```
Style name
Allowed chord types
Preferred progressions
Substitution rules
Voice-leading rules
Cadence patterns
Bass behavior
Chromaticism level
Extension preferences
Rhythm rules
Voicing density
Instrument-specific rules

```

Users should eventually be able to save and share their own style presets.

---

# 25. ACCURACY POLICY

Never describe a generated harmony as objectively correct simply because it was generated successfully.

Distinguish:

```
Technically valid
Voice-leading compliant
Stylistically consistent
Highly rated
User approved

```

These are separate states.

Music has artistic ambiguity.

---

# 26. COMPLETION GATE FOR EVERY FEATURE

A feature is COMPLETE only when all of the following are true:

```
[ ] Feature implemented
[ ] UI integrated where required
[ ] Unit tests added
[ ] Integration tests added where required
[ ] Existing tests still pass
[ ] Feature tests pass
[ ] Application builds
[ ] No new critical warnings
[ ] Documentation updated
[ ] CHECKPOINTS.md updated
[ ] Version/build reviewed
[ ] Git commit created
[ ] Commit SHA recorded
[ ] Working tree clean

```

If any item fails, the feature remains IN PROGRESS.

---

# 27. AGENT RESPONSE AFTER EACH FEATURE

After completing every feature, report exactly:

```
FEATURE CHECKPOINT REPORT

Feature:
Checkpoint:
Status:

Version:
Build:

Implemented:
1.
2.
3.

Files added:
-

Files modified:
-

Tests added:
-

Test result:

Build result:

Regression result:

Known limitations:

Git commit:
Git SHA:

Rollback checkpoint:

Next planned feature:

```

Do not continue automatically if a major architectural problem has been discovered.

Otherwise proceed sequentially.

---

# 28. FIRST DEVELOPMENT TARGET

Begin only with:

FEATURE 001 — Project Foundation

Do not implement MIDI, PDF, AI, audio transcription, harmonization, or notation recognition during Feature 001.

The purpose of Feature 001 is to establish a reliable application architecture, testing environment, source-control process, automated build, version system, logging, settings infrastructure, and checkpoint mechanism upon which every following feature will depend.

Once Feature 001 passes its completion gate, create:

```
checkpoint/001-project-foundation

```

Record the Git commit SHA and then proceed to Feature 002.

---

# FINAL ENGINEERING RULE

Build the smallest correctly working version of each capability before increasing sophistication.

At all times:

```
Working software
    >
large unfinished implementation.

```

Every completed feature must leave the repository in a buildable, testable, recoverable state.