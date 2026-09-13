# 🎵 MusicAre Python Plugin SDK

Official pure-Python SDK providing core contracts, domain models, heuristic candidate ranking, and packaging CLI tools for building **MusicAre** audio source plugins.

---

## 📦 Installation

Add this SDK to your plugin's `requirements.txt`:

```text
git+https://github.com/your-org/musicare_audiosource_sdk.git#subdirectory=python/plugin_sdk
```

Or install it directly via `pip`:

```bash
pip install git+https://github.com/your-org/musicare_audiosource_sdk.git#subdirectory=python/plugin_sdk
```

---

## ⚡ Two-Tier Just-In-Time (JIT) Resolution Lifecycle

Plugins built with this SDK implement a decoupled, two-phase resolution architecture:
1. **Phase 1: Candidate Search (`search_candidates`)**: Fast text-based search returning lightweight metadata (`CandidateTrack`: id, title, artist, duration) in **< 0.4s** without downloading media formats or running heavy deciphers.
2. **Phase 2: JIT Stream Resolution (`resolve_stream`)**: Direct on-demand extraction of the playable CDN stream URL (`AudioStreamResponse`) in **~0.7s** executed exclusively for the single chosen `candidate_id`.

---

## 🚀 Creating a Plugin

Implement the `BaseAudioSourcePlugin` interface and expose the standard `get_plugin()` factory function:

```python
from musicare_plugin_sdk import (
    AudioQuality,
    AudioStreamResponse,
    BaseAudioSourcePlugin,
    CandidateTrack,
    Track,
    TrackMatcher,
)


class ExampleAudioSourcePlugin(BaseAudioSourcePlugin):
    @property
    def id(self) -> str:
        return "org.musicare.audiosource.example"

    @property
    def name(self) -> str:
        return "Example Audio Source"

    @property
    def version(self) -> str:
        return "1.0.0"

    def search_candidates(self, track: Track) -> list[CandidateTrack]:
        # 1. Fast search on upstream provider (< 0.4s)
        # 2. Return lightweight candidate metadata (id, title, artist, duration_ms)
        return [
            CandidateTrack(
                id="track_12345",
                title="Come Together",
                artist="The Beatles",
                duration_ms=259000,
            )
        ]

    def resolve_stream(
        self, candidate_id: str, quality: AudioQuality = AudioQuality.HIGH
    ) -> AudioStreamResponse:
        # Direct on-demand stream URL extraction for the given candidate ID (~0.7s)
        return AudioStreamResponse(
            url="https://example.com/audio.m4a",
            quality=quality,
            codec="m4a",
            bitrate=160000,
            expires_at=None,
            headers={"User-Agent": "MusicAre/1.0.0"},
        )


def get_plugin() -> BaseAudioSourcePlugin:
    """Standard entry-point factory called dynamically by the host engine."""
    return ExampleAudioSourcePlugin()
```

---

## 🛠️ Included CLI Tools

When installed, this package exposes two command-line utilities:

### 1. `musicare-build`
Validates `plugin.json`, installs dependencies, performs a strict **Pure-Python mobile compliance audit** (rejects any compiled `.so`, `.pyd`, or `.dylib` native binaries), and packages your plugin into a portable `plugin.zip`:

```bash
musicare-build
```

### 2. `musicare-play`
Resolves and streams audio directly through a local media player (`mpv`, `ffplay`, or `vlc`) without requiring the host application:

```bash
musicare-play "The Beatles" "Come Together"
```
