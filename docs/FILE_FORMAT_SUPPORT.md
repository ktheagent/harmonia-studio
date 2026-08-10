# File Format Support

| Format | Import | Export | Preview status |
|---|---:|---:|---|
| MusicXML (`.musicxml`, `.xml`) | Yes | Yes | Structured import/export with round-trip tests |
| Compressed MusicXML (`.mxl`) | Yes | Yes | ZIP/container import/export |
| MIDI (`.mid`, `.midi`) | Yes | Yes | Track/note/tempo/meter/program import; multi-track export |
| PDF | Yes | Yes | PDF→image→OMR baseline; engraved/reference PDF export |
| PNG/JPG/JPEG/TIFF | Yes | No | Printed-score OMR baseline |
| WAV | Yes | Yes | Audio import; reference synthesized export |
| MP3 | Yes | Yes | Decode through audio stack; MP3 export through ffmpeg |
| FLAC | Yes | No | Audio import tested |
| AAC/M4A | Yes | No | Import route implemented; not individually round-trip tested here |

## Accuracy boundaries

MusicXML and MIDI preserve structured musical data much more directly than PDF/image/audio inputs. OMR and audio transcription are recognition processes and therefore expose confidence/verification rather than assuming every recognized note is correct.
