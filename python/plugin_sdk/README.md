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

## 🚀 Creating a Plugin

Implement the `BaseAudioSourcePlugin` interface and expose the standard `get_plugin()` factory function:

```python
from musicare_plugin_sdk import (
    BaseAudioSourcePlugin,
    Track,
    AudioQuality,
    AudioStreamResponse,
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

    def get_stream(
        self,
        track: Track,
        quality: AudioQuality,
    ) -> list[AudioStreamResponse]:
        # 1. Search provider API
        # 2. Score and rank candidates using TrackMatcher.rank_candidates()
        # 3. Return resolved AudioStreamResponse items
        return [
            AudioStreamResponse(
                url="https://example.com/audio.m4a",
                quality=quality,
                codec="m4a",
                bitrate=128000,
            )
        ]


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