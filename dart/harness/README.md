# 🧪 MusicAre Audio Source Test Harness

Official end-to-end (E2E) compliance and runtime verification test harness for **MusicAre** audio source plugins, powered by Flutter and **SeriousPython**.

---

## 🎯 Purpose

This harness acts as the official certification testbed for third-party audio source plugins. It validates that a compiled `plugin.zip` archive correctly executes inside the sandboxed CPython runtime on real target platforms (**Linux Desktop** and **Android**) before release.

### What the Harness Tests:
1. **Archive Unpacking**: Extracts `plugin.zip` into a clean, sandboxed application directory.
2. **Host Daemon Boot**: Stages `python/host_runtime` and launches SeriousPython on an ephemeral port.
3. **Dynamic Injection**: Calls `POST /load_plugin` to verify dynamic import and `get_plugin()` contract adherence.
4. **Stream Resolution**: Resolves canonical track metadata via `POST /get_stream`.
5. **CDN Playback Handshake**: Performs an HTTP Range request (`Range: bytes=0-1024`) against upstream CDN servers (e.g. `googlevideo.com`) to confirm real audio bytes are playable.

---

## ⚙️ Prerequisites

Before running the harness, ensure your development machine has:

* **Flutter SDK**: `v3.12.0` or higher
* **Python**: `3.10` or higher (with `pip`)
* **Android Target** *(optional, for mobile testing)*:
  * Physical Android device connected via USB with **USB Debugging** enabled.
  * Or an active Android Emulator.

---

## 🚀 One-Time Setup

From this directory (`dart/harness`), fetch Flutter dependencies and grant execution permissions to the test runner script:

```bash
cd dart/harness
flutter pub get
chmod +x test_plugin.sh
```

---

## 🧪 Running the Verification Test

Make sure your plugin archive (`plugin.zip`) has already been built (e.g. via `musicare-build` in your plugin repository).

### 1. Test on Linux Desktop (Fastest)
Runs natively inside the local desktop runtime:

```bash
./test_plugin.sh /absolute/or/relative/path/to/plugin.zip linux
```

### 2. Test on Connected Android Device (Moto G84, Pixel, etc.)
Find your device identifier with `flutter devices`:

```bash
flutter devices
```

Then run the harness targeting your device ID:

```bash
# Example with device ID 'ZT322KHSD2':
./test_plugin.sh /path/to/plugin.zip ZT322KHSD2
```

---

## 📋 Interpreting Results

* **✅ Test Passes (`✓`)**: The plugin is 100% compliant with SeriousPython, respects mobile runtime constraints, and resolves playable CDN audio streams.
* **❌ Test Fails**: The harness fails fast with descriptive assertion reasons:
  * *`EngineBootTimeoutException`*: The host daemon failed to bind sockets or start Flask.
  * *`PluginLoadException`*: Python could not import the entry point or `get_plugin()` failed.
  * *`StreamResolutionException`*: `yt-dlp` or the provider failed to extract audio URLs or hit rate limits.
  * *`CDN handshake failed`*: Upstream CDN rejected the HTTP Range request (e.g. expired token, blocked IP, or invalid headers).