# 🎵 MusicAre Audio Source SDK

Official, pure-Python SDK providing core contracts, data models, and heuristic matching engine for **MusicAre** audio source plugins and hosts.

---

## 📦 Installation

Add the SDK to your `requirements.txt`:

```text
git+https://github.com/your-org/musicare_audiosource_sdk.git
```

Or install it directly with `pip`:

```bash
pip install git+https://github.com/your-org/musicare_audiosource_sdk.git
```

---

## 🚀 Quickstart

```python
from musicare_plugin_sdk import (
    BaseAudioSourcePlugin,
    Track,
    AudioQuality,
    AudioStreamResponse,
    TrackMatcher
)

class MyCustomAudioSourcePlugin(BaseAudioSourcePlugin):
    @property
    def id(self) -> str:
        return "org.musicare.audiosource.mycustom"

    @property
    def name(self) -> str:
        return "My Custom Audio Source"

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_stream(self, track: Track, quality: AudioQuality) -> list[AudioStreamResponse]:
        # 1. Search provider API
        # 2. Rank candidates using TrackMatcher.rank_candidates()
        # 3. Return ordered AudioStreamResponse items
        return [
            AudioStreamResponse(
                url="https://example.com/audio.m4a",
                quality=quality,
                codec="m4a",
                bitrate=128000
            )
        ]
```
```