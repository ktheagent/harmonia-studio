# Architecture

Harmonia Studio uses modular presentation, application, domain, and infrastructure boundaries.

```text
Presentation (Tk desktop shell)
        ↓
StudioController / application workflows
        ↓
Score + analysis + harmonization + arrangement domain
        ↑
Import / export / media infrastructure adapters
```

The current preview uses Python/Tkinter because that stack could be built and tested in the available development environment. The earlier Tauri/React/Rust proposal remains a possible future shell migration; it is not claimed as implemented.

## Major modules

- `app.py`: desktop shell and user workflow wiring.
- `controller.py`: headless integration boundary for import, analysis, harmonization, arrangement and export.
- `project.py`, `history.py`: `.harmonia` persistence, migration, autosave/recovery metadata and version history.
- `score.py`: unified musical score representation.
- `importers/`: MusicXML, MIDI, PDF preparation, OMR and audio decoding.
- `analysis/`: tonality, chords, functional harmony and phrase/cadence analysis.
- `harmony/`: diatonic planning, SATB, voice leading, styles, candidates and regional reharmonization.
- `arrangement/`: ensemble templates and range-aware automatic arrangement.
- `transcription/`: melody, audio chord, tempo and meter analysis.
- `exporters/`: MusicXML, MIDI, PDF, WAV/MP3 and practice-track exports.
- `notation.py`, `editor.py`, `playback.py`: notation rendering, score editing and timed playback sequencing.
- `quality.py`: quality metrics and validation summary.
- `assistant.py`: deterministic natural-language music command parsing routed through validated engines.

## Dependencies

The preview uses the Python standard library plus NumPy, librosa, soundfile, pretty_midi/mido, OpenCV, Pillow and ReportLab. PDF rendering depends on Poppler (`pdftoppm`) where PDF OMR is used; MP3 export depends on ffmpeg.

## Extension boundaries

Importers, exporters, style profiles, OMR, transcription and audio playback are separated so stronger production engines can replace the preview implementations without changing the unified score model.

Core music logic does not depend on Tkinter.
