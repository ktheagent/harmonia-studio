# Harmonia Studio

Harmonia Studio is an AI-assisted music harmonization, arrangement, transcription, notation and export workstation developed feature-by-feature with recoverable Git checkpoints.

**Preview version:** 0.9.0 (build 44)
**Roadmap checkpoints:** 44 / 44 implemented and automated-test validated at MVP level.

## What the preview can do

Import structured notation (MusicXML/MXL/MIDI), recognize clean printed score images/PDFs through a baseline OMR pipeline, transcribe predominant melody/tempo/meter from audio, analyze tonality/chords/functions/phrases, generate multiple harmonization candidates across the implemented styles, create SATB/ensemble arrangements, validate quality, preserve project history, and export MusicXML/MXL/MIDI/PDF/WAV/MP3 plus practice tracks.

The desktop shell exposes Import, Analyze, Harmonize, Arrange, Validate and Export workflows. Recognition and style generation expose warnings/quality information rather than treating every musical decision as objectively correct.

## Run from source

```bash
python -m harmonia_studio.app
```

A headless diagnostic/controller path is exercised by automated tests.

## Test

```bash
python -m unittest discover -s tests -v
python -m compileall harmonia_studio
```

## Project structure

- `harmonia_studio/` application and music engines
- `tests/` automated unit, regression and integration tests
- `docs/` architecture, formats, roadmap and checkpoint records
- `.github/workflows/` Windows validation/package workflow

## Preview limitations

This is not yet declared a production 1.0 release. The built-in OMR targets clean printed notation, audio transcription targets a predominant melody rather than arbitrary dense polyphony, the internal synthesizer is reference-quality, and the GUI/native Windows build has not been manually validated in this headless local environment.

See `docs/FEATURES.md`, `docs/FILE_FORMAT_SUPPORT.md` and `RELEASE_NOTES.md` for details.
