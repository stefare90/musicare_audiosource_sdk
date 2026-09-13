# 🎯 MusicAre Dart Host SDK

Official Flutter/Dart Host SDK providing runtime lifecycle management for **SeriousPython** and HTTP RPC communication with audio source plugins in the **MusicAre** ecosystem.

---

## 📦 What this package provides

* **`AudioSourceClient`**: Low-level driver that allocates dynamic ports, boots the embedded SeriousPython host daemon, injects unzipped plugins at runtime, and proxies Two-Tier JIT stream resolution requests.
* **`ResolvedTrackPlayback`**: Composite domain payload returned by initial track resolution containing the active playable stream, candidate list, and active candidate ID.
* **`CandidateTrack`**: Lightweight metadata candidate representation (ID, title, artist, duration) used for stream switching and failovers.
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

  // 3. Fast initial track playback resolution (~1.1s total)
  final playback = await client.resolveTrack(
    title: 'Come Together',
    artists: ['The Beatles'],
    durationMs: 259000,
    quality: AudioQuality.high,
  );

  print('Primary Stream URL: ${playback.stream.url}');
  print('Active Candidate ID: ${playback.activeCandidateId}');
  print('Available Candidates: ${playback.candidates.length}');

  // 4. On-demand stream resolution for an alternative candidate (~0.7s)
  if (playback.candidates.length > 1) {
    final alternativeCandidate = playback.candidates[1];
    final alternativeStream = await client.resolveStream(
      candidateId: alternativeCandidate.id,
      quality: AudioQuality.high,
    );
    print('Alternative Stream URL: ${alternativeStream.url}');
  }

  // 5. Terminate runtime when disposing
  client.stop();
}
```
