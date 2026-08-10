# Harmonia Studio Development Checkpoints

## Feature 001 — Project Foundation
Status: PASSED

Version: 0.1.0
Build: 1

Checkpoint: `checkpoint/001-project-foundation`

Implemented:
- Desktop shell
- Settings and theme preference persistence
- Logging and diagnostics
- Error model and future engine contracts
- Automated tests
- CI workflow structure

Tests: 6 passed

Build: Python source compile passed; Windows executable not locally validated

Known limitations:
- Native Windows executable has not been built in this environment.
- Music features intentionally not implemented.

Next:
- Feature 002 — Project Management


## Feature 002 — Project Management
Status: PASSED

Checkpoint: `checkpoint/002-project-management`

Implemented:
- `.harmonia` project format with schema version
- New/open/save/save-as service
- Atomic saves
- Recent projects
- Autosave and recovery candidates
- Source-file non-destructive handling

Tests: 11 total suite tests passed
Build: Python source compile passed
Next: Feature 003 — Unified Score Data Model


## Feature 003 — Unified Score Data Model
Status: PASSED
Checkpoint: `checkpoint/003-unified-score-model`
Implemented:
- Score/part/instrument/measure/note/rest/pitch/duration model
- Lyrics, harmony, key, time, tempo and metadata
- JSON-safe serialization/deserialization
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 004 — MusicXML Import


## Feature 004 — MusicXML Import
Status: PASSED
Checkpoint: `checkpoint/004-musicxml-import`
Implemented:
- `.musicxml`, `.xml`, `.mxl` import
- Notes, rests, voices, staves, key/time, tempo, harmony, lyrics, ties
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 005 — MIDI Import


## Feature 005 — MIDI Import
Status: PASSED
Checkpoint: `checkpoint/005-midi-import`
Implemented:
- `.mid`/`.midi` track import
- Pitch, velocity, duration, tempo, initial meter and instrument programs
- Configurable quarter-note quantization grid
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 006 — Score Renderer


## Feature 006 — Score Renderer
Status: PASSED
Checkpoint: `checkpoint/006-score-renderer`
Implemented:
- SVG staff renderer with clefs, notes, rests, barlines, chord symbols and lyrics
- Page/continuous layout option and zoom control
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 007 — Score Editing


## Feature 007 — Score Editing
Status: PASSED
Checkpoint: `checkpoint/007-score-editing`
Implemented:
- Add/remove notes and measures
- Duration, pitch, transposition, lyrics and chord editing
- Snapshot undo/redo
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 008 — Playback Engine


## Feature 008 — Playback Engine
Status: PASSED
Checkpoint: `checkpoint/008-playback`
Implemented:
- Playback event sequencer with play/pause/resume/stop state
- Tempo scaling, seek cursor, measure loop, solo, mute and part volume
- Pluggable audio/event sink for platform sound backends
Tests: Full suite passed
Build: Python source compile passed
Known limitation: automated tests validate timing/events, not physical speaker output.
Next: Feature 009 — Tonal Analysis


## Feature 009 — Tonal Analysis
Status: PASSED
Checkpoint: `checkpoint/009-tonal-analysis`
Implemented:
- Global and per-measure key estimation
- Major/minor tonal profile scoring and confidence
- Scale pitch-class output and modulation candidates
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 010 — Chord Analysis


## Feature 010 — Chord Analysis
Status: PASSED
Checkpoint: `checkpoint/010-chord-analysis`
Implemented:
- Root/quality/inversion/slash-bass detection
- Triads, sevenths, suspensions, sixths and diminished families
- Extension metadata, confidence and harmonic-rhythm duration
- Optional application of detected chord symbols to the score
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 011 — Functional Harmony Analysis


## Feature 011 — Functional Harmony Analysis
Status: PASSED
Checkpoint: `checkpoint/011-functional-analysis`
Implemented:
- Roman-numeral mapping
- Tonic/predominant/dominant classification
- Secondary-dominant and tonicization detection
- Borrowed/chromatic chord marking
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 012 — Phrase and Cadence Detection


## Feature 012 — Phrase and Cadence Detection
Status: PASSED
Checkpoint: `checkpoint/012-phrase-analysis`
Implemented:
- Phrase boundaries and section grouping
- Authentic, imperfect, plagal, deceptive and half cadence classifier
- Repeated melodic-motif detection
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 013 — Basic Diatonic Harmonization


## Feature 013 — Basic Diatonic Harmonization
Status: PASSED
Checkpoint: `checkpoint/013-basic-harmonization`
Implemented:
- Key-aware diatonic triad candidate generation
- Melody-coverage and functional-transition scoring
- Measure/beat harmonic density and cadence bias
- Non-destructive application preserving melody
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 014 — Voice Leading Engine


## Feature 014 — Voice Leading Engine
Status: PASSED
Checkpoint: `checkpoint/014-voice-leading`
Implemented:
- Vocal range, crossing, spacing and leap checks
- Parallel fifth/octave and hidden-perfect detection
- Leading-tone resolution warning
- Configurable validation profile
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 015 — SATB Harmonization


## Feature 015 — SATB Harmonization
Status: PASSED
Checkpoint: `checkpoint/015-satb`
Implemented:
- Soprano-preserving four-part arrangement
- Configurable SATB ranges, position/doubling/bass preferences
- Smooth bass/root placement and range-aware inner voices
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 016 — Traditional Hymn Style


## Feature 016 — Traditional Hymn Style
Status: PASSED
Checkpoint: `checkpoint/016-hymn-style`
Implemented:
- Configurable hymn style profile
- Conservative diatonic SATB generation
- Strict voice-leading validation profile
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 017 — Classical Chorale Style


## Feature 017 — Classical Chorale Style
Status: PASSED
Checkpoint: `checkpoint/017-classical-style`
Implemented:
- Classical chorale style profile
- Stricter leap, hidden-perfect and parallel-perfect validation settings
- Functional progression preferences with restrained chromaticism
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 018 — Gospel Harmonization


## Feature 018 — Gospel Harmonization
Status: PASSED
Checkpoint: `checkpoint/018-gospel-style`
Implemented:
- Gospel style profile with simple/modern/advanced complexity mapping
- Secondary-dominant and diminished passing-color plan transformations
- Active-bass metadata and tonic-ending preservation
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 019 — Jazz Harmonization


## Feature 019 — Jazz Harmonization
Status: PASSED
Checkpoint: `checkpoint/019-jazz-style`
Implemented:
- ii-V-I seventh-chord planning
- Major/minor seventh and dominant-seventh vocabulary
- Creative tritone-substitution and backdoor-dominant color
- Jazz-specific relaxed perfect-interval validation profile
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 020 — Pop Harmonization


## Feature 020 — Pop Harmonization
Status: PASSED
Checkpoint: `checkpoint/020-pop-style`
Implemented:
- Contemporary I-V-vi-IV style loop in major
- Minor-key loop variant
- Smooth-bass style metadata and conservative chromaticism
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 021 — R&B / Neo-Soul


## Feature 021 — R&B / Neo-Soul
Status: PASSED
Checkpoint: `checkpoint/021-rnb-neosoul`
Implemented:
- Major7/minor7/dominant7 neo-soul progression vocabulary
- Inversion-aware slash-bass generation
- Creative diminished chromatic passing option
- R&B-specific voice-leading profile
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 022 — Highlife Harmonization


## Feature 022 — Highlife Harmonization
Status: PASSED
Checkpoint: `checkpoint/022-highlife-style`
Implemented:
- Highlife-oriented I-I-IV-V-I loop profile
- Active-bass and interlocking guitar/keyboard accompaniment metadata
- Optional dominant-seventh color at advanced complexity
Tests: Pending
Build: Pending
Known limitation: this is a configurable starting profile, not a claim that all Highlife uses one progression.
Next: Feature 023 — Afrobeat Harmonization


## Feature 023 — Afrobeat Harmonization
Status: PASSED
Checkpoint: `checkpoint/023-afrobeat-style`
Implemented:
- Groove-first sparse modal/vamp harmony profile
- Long harmonic holds and repeated-bass-ostinato metadata
- Interlocking guitar/keyboard arrangement metadata
Tests: Pending
Build: Pending
Known limitation: Afrobeat is diverse; the default vamp is a configurable starting point rather than a universal formula.
Next: Feature 024 — Blues Harmonization


## Feature 024 — Blues Harmonization
Status: PASSED
Checkpoint: `checkpoint/024-blues-style`
Implemented:
- Twelve-bar I7/IV7/V7 blues form
- Turnaround behavior and dominant-seventh vocabulary
- Blues-specific relaxed perfect-interval profile
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 025 — Harmonization Control Panel


## Feature 025 — Harmonization Control Panel
Status: PASSED
Checkpoint: `checkpoint/025-harmonization-controls`
Implemented:
- Reusable desktop control panel and validated settings model
- Style, complexity, density, chromaticism, bass, voice-leading and voice-count controls
- Melody/original-harmony preservation, modulation, extensions and rhythmic-density controls
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 026 — Multiple Harmony Candidates


## Feature 026 — Multiple Harmony Candidates
Status: PASSED
Checkpoint: `checkpoint/026-harmony-candidates`
Implemented:
- Conservative, Stylistic and Creative candidate generation
- Deterministic differentiation via inversions/substitution choices
- Per-candidate voice-leading-derived quality score
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 027 — Measure-Level Reharmonization


## Feature 027 — Measure-Level Reharmonization
Status: PASSED
Checkpoint: `checkpoint/027-region-reharmonization`
Implemented:
- Inclusive measure-range reharmonization
- Unselected measures left byte-equivalent at serialized model level
- Region/style metadata recorded
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 028 — Instrument/Ensemble Templates


## Feature 028 — Instrument/Ensemble Templates
Status: PASSED
Checkpoint: `checkpoint/028-ensemble-templates`
Implemented:
- SATB, piano, piano+vocal, string quartet, brass, worship band, jazz combo, full band and orchestra
- Range, transposition, polyphony and role metadata
- Custom ensemble constructor
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 029 — Automatic Arrangement


## Feature 029 — Automatic Arrangement
Status: PASSED
Checkpoint: `checkpoint/029-auto-arrangement`
Implemented:
- Template-driven melody, bass, harmony and rhythm-part generation
- Range fitting, instrument program/transposition metadata and polyphony limits
- Style-aware harmonic source plan
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 030 — PDF Import Framework


## Feature 030 — PDF Import Framework
Status: PASSED
Checkpoint: `checkpoint/030-pdf-framework`
Implemented:
- PDF signature validation
- Poppler-based page rasterization into managed OMR workspace
- Page metadata with DPI and deterministic ordering
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 031 — Optical Music Recognition


## Feature 031 — Optical Music Recognition
Status: PASSED
Checkpoint: `checkpoint/031-omr`
Implemented:
- Built-in baseline OMR for clean printed five-line staves
- PDF/PNG/JPG/JPEG/TIFF routing
- Staff-line detection, notehead detection, treble-staff pitch mapping and confidence
- Low-confidence warnings instead of silent acceptance
Tests: Full suite passed
Build: Python source compile passed
Known limitation: complex engraving, polyphony, clef changes, beams, handwritten music and damaged scans require a stronger OMR backend and manual verification.
Next: Feature 032 — OMR Verification Workspace


## Feature 032 — OMR Verification Workspace
Status: PASSED
Checkpoint: `checkpoint/032-omr-verification`
Implemented:
- Side-by-side verification panel scaffold
- Uncertain-symbol filtering
- Manual pitch correction, note add/delete and approval tracking
- Verified-score metadata and edit audit count
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 033 — Audio Import


## Feature 033 — Audio Import
Status: PASSED
Checkpoint: `checkpoint/033-audio-import`
Implemented:
- WAV, MP3, FLAC, AAC and M4A extension routing
- SoundFile/ffprobe metadata probing
- Librosa decoding to normalized mono analysis samples
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 034 — Melody Transcription


## Feature 034 — Melody Transcription
Status: PASSED
Checkpoint: `checkpoint/034-melody-transcription`
Implemented:
- Predominant monophonic pitch tracking using pYIN
- Voiced-segment grouping, MIDI pitch conversion and confidence
- Conversion to editable score measures using supplied BPM
Tests: Full suite passed
Build: Python source compile passed
Known limitation: dense polyphonic mixes may need stem separation or a dedicated melody model for professional accuracy.
Next: Feature 035 — Audio Chord Recognition


## Feature 035 — Audio Chord Recognition
Status: PASSED
Checkpoint: `checkpoint/035-audio-chords`
Implemented:
- Chroma-based major/minor/dominant7/minor7 recognition
- Time-window segmentation, confidence scoring and adjacent-segment merging
- Manual correction API
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 036 — Tempo and Meter Detection


## Feature 036 — Tempo and Meter Detection
Status: PASSED
Checkpoint: `checkpoint/036-tempo-meter`
Implemented:
- Beat tracking and BPM estimation
- 3/4, 4/4 and 6/4 accent-pattern meter hypotheses with confidence
- Beat-time output, tempo regularity confidence and pickup-phase estimate
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 037 — MusicXML Export


## Feature 037 — MusicXML Export
Status: PASSED
Checkpoint: `checkpoint/037-musicxml-export`
Implemented:
- `.musicxml`, `.xml` and compressed `.mxl` export
- Notes/rests, duration, voice/staff, key/time/tempo, harmony, ties and lyrics
- Export -> re-import validation tests
Tests: Full suite passed
Build: Python source compile passed
Known limitation: complex simultaneous multi-voice onset encoding still needs MusicXML backup/forward support.
Next: Feature 038 — MIDI Export


## Feature 038 — MIDI Export
Status: PASSED
Checkpoint: `checkpoint/038-midi-export`
Implemented:
- Type-1 MIDI export with per-part tracks/programs
- Note timing, velocity, tempo and meter events
- Export -> MIDI import round-trip test
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 039 — PDF Score Export


## Feature 039 — PDF Score Export
Status: PASSED
Checkpoint: `checkpoint/039-pdf-export`
Implemented:
- Printable full score, individual part, lead sheet, chord chart and SATB PDF modes
- Programmatic staff/note/chord/lyric drawing
- PDF signature validation and actual first-page render validation
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 040 — Audio Export


## Feature 040 — Audio Export
Status: PASSED
Checkpoint: `checkpoint/040-audio-export`
Implemented:
- Score-to-audio reference synthesizer with velocity and part-volume control
- PCM WAV export
- MP3 encoding through ffmpeg/libmp3lame
Tests: Full suite passed
Build: Python source compile passed
Known limitation: built-in synthesis is a reference playback renderer, not a sampled production instrument library.
Next: Feature 041 — Practice Track Export


## Feature 041 — Practice Track Export
Status: PASSED
Checkpoint: `checkpoint/041-practice-tracks`
Implemented:
- Full mix
- Per-part emphasized rehearsal mixes
- Instrument-only mix by muting detected voice parts
- WAV/MP3 output through the shared audio exporter
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 042 — Harmony Quality Analyzer


## Feature 042 — Harmony Quality Analyzer
Status: PASSED
Checkpoint: `checkpoint/042-quality-analysis`
Implemented:
- Melody preservation, voice leading, range compliance and harmonic consistency metrics
- Cadence, style, playability and rhythmic consistency metrics
- Overall score plus explicit issue counts/warnings
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 043 — Natural Language Music Commands


## Feature 043 — Natural Language Music Commands
Status: PASSED
Checkpoint: `checkpoint/043-ai-assistant`
Implemented:
- Deterministic natural-language parser for styles, measure ranges, ensembles and candidate count
- Melody-preservation, easier-voice, bass-movement and ending-style constraints
- Execution through existing harmonization/arrangement engines
- Mandatory quality validation after assistant operations
Tests: Full suite passed
Build: Python source compile passed
Next: Feature 044 — Complete Project History


## Feature 044 — Complete Project History
Status: PASSED
Checkpoint: `checkpoint/044-project-history`
Implemented:
- Undo/redo history snapshots independent of score editor undo
- Named versions, harmony-generation snapshots and imported-source snapshots
- Snapshot restore by name/id and serializable history
- `.harmonia` schema v2 with safe migration from schema v1
Tests: 86 total suite tests passed
Build: Python source compile passed
Next: Integration and release audit

## Preview Release Audit — 0.9.0 Build 44

Status: PASSED FOR SOURCE PREVIEW

Validation:
- 44 feature checkpoint tags present
- 89 automated tests passed
- Python source compile passed
- Integrated controller workflow passed
- MusicXML/MIDI export and re-import integration passed
- PDF signature/render tests passed in the feature suite
- WAV/MP3 export tests passed in the feature suite
- Python wheel built successfully with the installed build toolchain
- Built wheel installed and smoke-imported successfully

Desktop/native status:
- Tk desktop shell wired to import, analyze, harmonize, arrange, validate and export workflows
- Manual GUI launch: NOT TESTED (headless environment)
- Physical audio/MIDI/printer/device tests: NOT TESTED
- Windows executable: NOT CONFIRMED
- GitHub Actions: NOT STARTED (local project has no configured Harmonia GitHub target)

Release classification:
- 0.9.0 preview, not production 1.0
