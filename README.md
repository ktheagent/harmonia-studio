# Harmonia Studio

Harmonia Studio is an AI-assisted music harmonization, arrangement, transcription, notation and export workstation developed feature-by-feature with recoverable Git checkpoints.

**Preview version:** 0.9.0 (build 54)  
**Roadmap checkpoints:** 44 / 44 implemented and automated-test validated at MVP level.

## What the preview can do

Import structured notation (MusicXML/MXL/MIDI), recognize clean printed score images/PDFs through a baseline OMR pipeline, transcribe predominant melody/tempo/meter from audio, analyze tonality/chords/functions/phrases, generate multiple harmonization candidates across the implemented styles, create SATB/ensemble arrangements, validate quality, preserve project history, and export MusicXML/MXL/MIDI/PDF/WAV/MP3 plus practice tracks.

The desktop shell exposes Import, Analyze, Harmonize, Arrange, Validate and Export workflows. The current Windows desktop includes native notation preview/editing, playback transport, Windows WAV speaker output, audio diagnostics, persistent playback preferences, and crash/startup diagnostics.

## Run from source

```bash
python harmonia_studio_launcher.py
```

A headless diagnostic/controller path is exercised by automated tests.

## Test

```bash
python -m unittest discover -s tests -v
python -m compileall harmonia_studio
```

## Windows CI

The `Validate Harmonia Studio Windows Build` workflow runs the automated tests, compiles the source, builds `Harmonia-Studio.exe` with PyInstaller, launches the packaged GUI in startup-smoke mode, creates a versioned portable ZIP plus SHA-256 checksum file, and uploads the Windows artifact.

The current CI-validated Windows run is #74 for commit `c24d1dbfc1bbbeb5f6ca7018c88c1633c912bbf3`. It passed the packaged-GUI startup smoke gate and produced artifact `Harmonia-Studio-0.9.0-Windows` (159 MB, digest `sha256:cba7d8e8a55fea70388f2b23c1fa22916aedbea0a258936e74adf71ed35dfed6`).

CI-validated packaged GUI startup is not a substitute for manual interactive Windows or physical-device testing.

## Project structure

- `harmonia_studio/` application and music engines
- `tests/` automated unit, regression and integration tests
- `docs/` architecture, formats, roadmap and checkpoint records
- `.github/workflows/` Windows validation/package workflow

## Preview limitations

This is not yet declared a production 1.0 release. The built-in OMR targets clean printed notation, audio transcription targets a predominant melody rather than arbitrary dense polyphony, and the internal synthesizer is reference-quality.

The Windows executable is automatically launched during CI, but the full GUI has not been manually exercised on a physical Windows desktop in this audit. Physical speakers/audio devices, MIDI hardware, microphone, printer, and other hardware integrations remain manually unverified.

See `docs/FEATURES.md`, `docs/FILE_FORMAT_SUPPORT.md`, `docs/RELEASE_AUDIT.md` and `RELEASE_NOTES.md` for details.
