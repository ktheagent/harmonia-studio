# Harmonia Studio 0.9.0 Preview — Build 54

This preview consolidates all 44 roadmap checkpoints and the subsequent Windows desktop hardening work through Build 54.

## Release-gate status

- Unified project/score model and versioned `.harmonia` projects: implemented.
- MusicXML/MXL and MIDI structured import/export: implemented and regression-tested.
- PDF/image OMR: baseline implemented with confidence and verification support.
- Audio import/transcription: predominant melody, chords, tempo/meter baseline implemented.
- Harmonization: diatonic, SATB, hymn, classical, gospel, jazz, pop, R&B/neo-soul, highlife, Afrobeat and blues profiles implemented.
- Arrangement, quality analysis, natural-language music commands and project history: implemented.
- PDF and audio/practice-track exports: implemented and automated-test validated where optional external tools are available.
- Desktop workflow: native notation preview/editing, richer note/harmony/measure editing, playback transport, Windows WAV speaker output, diagnostics, persistent playback preferences and crash reporting are integrated.
- Windows executable: built with PyInstaller and validated by the `Validate Harmonia Studio Windows Build` workflow.
- Packaged Windows GUI startup: CI-validated. Run #74 for commit `c24d1dbfc1bbbeb5f6ca7018c88c1633c912bbf3` passed the packaged-executable startup smoke gate.
- Windows artifact: run #74 produced `Harmonia-Studio-0.9.0-Windows` (159 MB), digest `sha256:cba7d8e8a55fea70388f2b23c1fa22916aedbea0a258936e74adf71ed35dfed6`.
- Manual interactive Windows GUI and physical-device testing: not yet performed in this audit.

## Build 45–54 hardening highlights

- Improved polyphonic MusicXML timing import/export and regression coverage.
- Added native desktop notation preview and richer score editing controls.
- Hardened playback timing, looping, seeking, mute/solo and volume behavior.
- Added native Windows WAV speaker playback plus audio diagnostics and a speaker self-test path.
- Added persistent speaker-output, master-volume and loop preferences.
- Added GUI crash reporting, startup smoke mode and project lifecycle smoke coverage.
- Added a CI gate that launches the packaged `Harmonia-Studio.exe` and fails on startup crash/hang.
- Corrected Windows-specific Tk menu tear-off/separator handling and inherited toolbar packing.
- Corrected the Windows CRLF-sensitive smoke success check.

## Why this remains 0.9.0 preview, not 1.0.0

Passing automated software tests and packaged-GUI startup does not prove full interactive desktop behavior or physical hardware integration. The following remain outside the current validation claim:

- full manual Windows GUI workflow testing on a physical desktop;
- physical speaker/audio-device verification;
- MIDI hardware, microphone, printer and other hardware testing;
- professional OMR accuracy benchmarking;
- dense polyphonic audio-transcription benchmarking;
- production engraving-quality validation;
- professional sampled-instrument playback quality.

See `docs/RELEASE_AUDIT.md` for the current validation record.
