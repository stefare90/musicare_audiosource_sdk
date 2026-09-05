# 🎵 MusicAre Audio Source SDK & Tooling Monorepo

Official multi-language SDK and verification testbed for the **MusicAre** audio source plugin ecosystem.

This monorepo provides the domain models, interfaces, packaging CLI tools, embedded SeriousPython runtime host, Dart client driver, and automated E2E compliance test harness.

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
│                                      Implements dynamic plugin loading and stream RPC endpoints.
│
└── dart/
    └── host_sdk/                   # 📦 musicare_dart_host_sdk
        │                              Flutter/Dart package providing AudioSourceClient,
        │                              domain models, and SeriousPython lifecycle management.
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
* **Documentation**: See [`dart/host_sdk/README.md`](dart/host_sdk/README.md) for usage of `AudioSourceClient`.

---

### 🧪 For QA & Compliance Testing (E2E Harness)
* **Goal**: Certify that a compiled `plugin.zip` runs in the real SeriousPython runtime without mobile OS security violations.
* **App to run**: `dart/host_sdk/harness`
* **Execution**:
  ```bash
  cd dart/host_sdk/harness
  ./test_plugin.sh /path/to/plugin.zip [linux | <android_device_id>]
  ```
* **Documentation**: See [`dart/host_sdk/harness/README.md`](dart/host_sdk/harness/README.md).

---

## 📜 Compatibility & Rules

* **100% Pure-Python Rule**: All plugins executed at runtime must be pure-Python packages. Compiled native C/C++ binary extensions (`.so`, `.pyd`, `.dylib`, `.dll`) are strictly prohibited due to mobile platform (Android/iOS) dynamic loading restrictions.
* **SemVer Protocol**: Plugin manifests define `pluginSdkVersion` to guarantee forward and backward compatibility with the host runtime.