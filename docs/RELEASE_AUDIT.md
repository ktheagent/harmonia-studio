# Harmonia Studio 0.9.0 Preview Release Audit

Status: IN PROGRESS

Audit date: 2026-08-11

This file is the current release-audit record and supersedes the stale GitHub Actions / Windows build status text at the end of `docs/CHECKPOINTS.md`.

## Verified

- Repository: `ktheagent/harmonia-studio`
- Default release branch: `main`
- Project version: `0.9.0`
- All 44 roadmap features are recorded as PASSED in `docs/CHECKPOINTS.md`.
- Preview release audit records 89 automated tests passed.
- Python source compile passed in the preview audit.
- MusicXML/MIDI export and re-import integration passed in the preview audit.
- PDF and WAV/MP3 export tests passed in the feature suite.
- GitHub Actions workflow `Validate Harmonia Studio Windows Build` run #7 completed the `test-and-package` job successfully for commit `343d5cdd8b06865baede423730b6ea962c42dcd9`.
- The Windows build job uses PyInstaller; the successful #7 job confirms the CI build step completed successfully.
- The source release archive is not stored in the repository.
- `SHA256SUMS.txt` is present in the repository root.

## Release-quality corrections applied

Commit `ca7aa2c197f7ca5d67c376f20f6f7a12b7585138` updates the Windows CI pipeline to:

- Use `actions/checkout@v5`.
- Use `actions/setup-python@v6`.
- Use `actions/upload-artifact@v6`.
- Run a smoke-import check before packaging.
- Read the release version from `pyproject.toml`.
- Package the PyInstaller output as `Harmonia-Studio-<version>-Windows-Portable.zip`.
- Generate `SHA256SUMS-Windows.txt`.
- Fail the job if expected release files are missing.

## Still not verified

- The new CI packaging workflow from commit `ca7aa2c197f7ca5d67c376f20f6f7a12b7585138` has not yet been confirmed successful in this audit.
- The exact artifact record for the new versioned portable ZIP and checksum file is not yet confirmed.
- The Windows executable has not been launched and interactively tested on a Windows desktop in this audit.
- Physical audio, MIDI, printer, and other device tests have not been performed.
- OMR accuracy has not been certified against a professional multi-publisher benchmark corpus.
- Audio transcription accuracy has not been certified against a professional polyphonic benchmark corpus.

## Release classification

Harmonia Studio remains `0.9.0` preview until the current Windows packaging workflow is confirmed and the remaining manual/device-test limitations are accepted for the preview release.
