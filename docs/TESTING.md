# Testing

Run the complete automated suite:

```bash
python -m unittest discover -s tests -v
```

Compile all Python source:

```bash
python -m compileall harmonia_studio
```

Validate the package without installing dependencies again:

```bash
python -m pip wheel . --no-deps --no-build-isolation -w dist
```

The suite includes unit/regression tests plus an integration path covering score analysis, three-candidate harmonization, arrangement, MusicXML/MIDI export and re-import, PDF validation, and WAV validation.

## External tools used by some features

- Poppler / `pdftoppm`: PDF page rendering for OMR.
- ffmpeg/ffprobe: MP3 export and fallback compressed-audio probing.

## Windows build

`.github/workflows/windows-build.yml` defines a Windows test/package workflow and a PyInstaller artifact. It has not been executed in this local-only build session, so a Windows executable is not considered confirmed.

## Manual/device testing not completed here

The current environment is headless. Desktop-window interaction, Windows installation/runtime behavior, physical MIDI devices, speakers/audio interfaces, microphones and production score/printer workflows were not manually tested.
