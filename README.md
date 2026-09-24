> [!IMPORTANT]
> **Superseded / archived repository.** This monorepo was the first version of the audio
> source SDK and is now frozen read-only for historical reference. Its content has been
> absorbed by **`musicare_plugin_sdk`**: the Python author SDK is now
> **`musicare_audio_plugin_sdk`**, the runtime is the unified Python host
> (`python/audio/host_runtime/`, started by the single entry point `python/main.py`, which
> runs both the audio and metadata daemons), the Dart host SDK is
> **`musicare_audio_host_sdk`**, the shared lifecycle package is
> **`musicare_runtime_host`**, the E2E harness lives in `dart/harness/`, and the wire
> protocol is documented in **`contract/PROTOCOL.md`**.
> The official audio plugin is **`musicare_audiosource_youtube_plugin`** (release `v1.1.0`,
> already migrated to the new platform). Everything in this repository stays as it is — as
> historical reference: no retroactive renames, no files to touch.

# 🎵 MusicAre Audio Source SDK & Tooling Monorepo

Official multi-language SDK and verification testbed for the **MusicAre** audio source plugin ecosystem.

This monorepo provides domain models, interfaces, packaging CLI tools, embedded SeriousPython runtime host, Dart client driver, and automated E2E compliance test harness supporting the **Two-Tier Just-In-Time (JIT)** audio stream resolution architecture.

---

## 🏛️ Monorepo Architecture

The repository is structured into two language domains and four focused modules:

```text
musicare_audiosource_sdk/
│
├── python/
│   ├── plugin_sdk/                 # 📦 musicare-plugin-sdk
│   │                                  Pure-Python SDK for plugin developers.
│   │                                  Contains models, BaseAudioSourcePlugin, TrackMatcher,
│   │                                  and the 'musicare-build' / 'musicare-play' CLIs.
│   │
│   └── host_runtime/               # 📌 musicare_python_host_runtime
│                                      Fixed CPython Flask daemon packaged by SeriousPython.
│                                      Implements dynamic plugin loading and Two-Tier JIT
│                                      stream RPC endpoints (/resolve_track, /resolve_stream).
│
└── dart/
    └── host_sdk/                   # 📦 musicare_dart_host_sdk
        │                              Flutter/Dart package providing AudioSourceClient,
        │                              domain models (CandidateTrack, ResolvedTrackPlayback),
        │                              and SeriousPython lifecycle management.
        │
        └── harness/                # 🧪 musicare_dart_harness
                                       Flutter integration test suite to verify third-party
                                       plugin.zip archives on Linux Desktop and Android.
```

---

## 🚀 Quick Navigation by Role

### 🎧 For Plugin Developers
* **Goal**: Build an audio streaming plugin (e.g. YouTube, SoundCloud, Spotify, Jellyfin).
* **Package to use**: `python/plugin_sdk`
* **Installation**:
  ```text
  pip install git+https://github.com/stefare90/musicare_audiosource_sdk.git#subdirectory=python/plugin_sdk
  ```
* **Documentation**: See [`python/plugin_sdk/README.md`](python/plugin_sdk/README.md) for quickstart and CLI guides (`musicare-build`, `musicare-play`).

---

### 📱 For Host Application Developers (Flutter)
* **Goal**: Integrate the audio source engine into the `music_are` Flutter app.
* **Package to use**: `dart/host_sdk`
* **Installation**:
  ```yaml
  dependencies:
    musicare_dart_host_sdk:
      git:
        url: https://github.com/stefare90/musicare_audiosource_sdk.git
        path: dart/host_sdk
  ```
* **Documentation**: See [`dart/host_sdk/README.md`](dart/host_sdk/README.md) for usage of `AudioSourceClient` (`resolveTrack`, `resolveStream`).

---

### 🧪 For QA & Compliance Testing (E2E Harness)
* **Goal**: Certify that a compiled `plugin.zip` runs in the real SeriousPython runtime without mobile OS security violations.
* **App to run**: `dart/harness`
* **Execution**:
  ```bash
  cd dart/harness
  ./test_plugin.sh /path/to/plugin.zip [linux | <android_device_id>]
  ```
* **Documentation**: See [`dart/harness/README.md`](dart/harness/README.md).

---

## 📜 Compatibility & Rules

* **100% Pure-Python Rule**: All plugins executed at runtime must be pure-Python packages. Compiled native C/C++ binary extensions (`.so`, `.pyd`, `.dylib`, `.dll`) are strictly prohibited due to mobile platform (Android/iOS) dynamic loading restrictions.
* **SemVer Protocol**: Plugin manifests define `pluginSdkVersion` to guarantee forward and backward compatibility with the host runtime.