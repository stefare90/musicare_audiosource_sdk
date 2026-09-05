# 🎯 MusicAre Dart Host SDK

Official Flutter/Dart Host SDK providing runtime lifecycle management for **SeriousPython** and HTTP RPC communication with audio source plugins in the **MusicAre** ecosystem.

---

## 📦 What this package provides

* **`AudioSourceClient`**: Low-level driver that allocates dynamic ports, boots the embedded SeriousPython host daemon, injects unzipped plugins at runtime, and proxies stream resolution requests.
* **`AudioStreamResponse` & `AudioQuality`**: Strongly-typed domain models representing resolved playable CDN stream URLs, codecs, bitrates, expiration timestamps, and required HTTP headers.
* **Typed Exceptions**: Specific exception types (`EngineBootTimeoutException`, `PluginLoadException`, `StreamResolutionException`, `PurePythonViolationException`).

---

## 🚀 Quickstart

Add the dependency to your host application's `pubspec.yaml`:

```yaml
dependencies:
  musicare_dart_host_sdk:
    git:
      url: https://github.com/your-org/musicare_audiosource_sdk.git
      path: dart/host_sdk
```

### Usage Example

```dart
import 'package:musicare_dart_host_sdk/musicare_dart_host_sdk.dart';

void main() async {
  final client = AudioSourceClient();

  // 1. Boot the embedded SeriousPython daemon in background
  await client.start();

  // 2. Dynamically inject an unzipped plugin directory into the Python runtime
  await client.loadPlugin('/path/to/extracted/plugin');

  // 3. Resolve stream URLs for a track
  final streams = await client.getStream(
    title: 'Come Together',
    artists: ['The Beatles'],
    durationMs: 259000,
    quality: AudioQuality.high,
  );

  final primaryStream = streams.first;
  print('Resolved URL: ${primaryStream.url}');
  print('Bitrate: ${primaryStream.bitrate} bps');
  print('Headers: ${primaryStream.headers}');

  // 4. Terminate runtime when disposing
  client.stop();
}
```