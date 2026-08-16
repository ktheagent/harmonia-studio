# Harmonia Studio 0.9.0 Preview Release Audit

Status: CI-VALIDATED PREVIEW

Audit date: 2026-08-16

This file is the current release-audit record and supersedes stale GitHub Actions / Windows build status text in older checkpoint records.

## Verified

- Repository: `ktheagent/harmonia-studio`
- Default release branch: `main`
- Project version: `0.9.0`
- Current application build: `54`
- All 44 roadmap checkpoints are recorded as PASSED at preview/MVP level.
- Automated unit, regression, integration, lifecycle, playback, import/export, and crash-reporting tests pass in the current Windows CI workflow.
- Python source compilation and smoke imports pass in Windows CI.
- MusicXML/MXL and MIDI import/export integration is covered by automated tests.
- PDF and WAV/MP3 export paths have automated coverage where their optional external tools are available.
- Workflow `Validate Harmonia Studio Windows Build` run #74 completed successfully for commit `c24d1dbfc1bbbeb5f6ca7018c88c1633c912bbf3`.
- The Windows job builds `Harmonia-Studio.exe` with PyInstaller and launches the packaged executable in CI smoke mode.
- The packaged GUI startup smoke report returned `OK` and the workflow accepted it successfully.
- Run #74 produced artifact `Harmonia-Studio-0.9.0-Windows`, size 159 MB, digest `sha256:cba7d8e8a55fea70388f2b23c1fa22916aedbea0a258936e74adf71ed35dfed6`.
- The workflow packages `Harmonia-Studio-0.9.0-Windows-Portable.zip` and generates `SHA256SUMS-Windows.txt`.
- The source release archive is not stored in the repository.

## Release-quality corrections applied

The current Windows release pipeline:

- Uses `actions/checkout@v5`.
- Uses `actions/setup-python@v6` with Python 3.12.
- Uses `actions/upload-artifact@v6`.
- Runs the automated test suite.
- Compiles the Python source tree.
- Runs smoke imports.
- Builds the Windows executable with PyInstaller.
- Launches the packaged Windows executable in startup-smoke mode.
- Captures startup/Tk callback failures into a deterministic smoke report.
- Packages the portable Windows build.
- Generates a SHA-256 checksum file.
- Fails if expected release files are missing.

Recent hardening also corrected Windows-specific Tk menu handling, workspace toolbar packing, GUI crash reporting, persistent playback preferences, and packaged-startup smoke validation.

## Still not verified

- The Windows executable has not been manually exercised through the full interactive GUI workflow on a physical Windows desktop.
- Physical speaker/audio-device playback has not been manually verified.
- Physical MIDI hardware, microphone, printer, and other device integrations have not been manually tested.
- Pause/resume audio remains measure-level rather than sample-accurate.
- The built-in audio renderer is reference-quality rather than a professional sampled-instrument library.
- OMR accuracy has not been certified against a professional multi-publisher benchmark corpus.
- Dense polyphonic audio-transcription accuracy has not been certified against a professional benchmark corpus.

## Release classification

Harmonia Studio remains `0.9.0` preview. The current Windows CI now validates tests, source compilation, PyInstaller packaging, packaged GUI startup, portable packaging, checksum generation, and artifact upload. This is not equivalent to full manual Windows UX or physical-device validation.
