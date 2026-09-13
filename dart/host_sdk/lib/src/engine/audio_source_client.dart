import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:archive/archive.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:serious_python/serious_python.dart';

import '../exceptions.dart';
import '../models/audio_stream.dart';

/// Low-level driver managing SeriousPython host lifecycle, plugin archive unpacking,
/// dynamic runtime injection, and HTTP RPC communication.
class AudioSourceClient {
  int? _port;
  http.Client? _httpClient;
  bool _isStarted = false;
  String? _loadedPluginName;

  bool get isStarted => _isStarted;
  int? get port => _port;
  String? get loadedPluginName => _loadedPluginName;

  /// Starts the embedded SeriousPython host daemon on an ephemeral dynamic port.
  Future<void> start({Duration timeout = const Duration(seconds: 15)}) async {
    if (_isStarted) return;

    _httpClient = http.Client();

    // 1. Allocate an ephemeral free port
    final socket = await ServerSocket.bind(InternetAddress.loopbackIPv4, 0);
    _port = socket.port;
    await socket.close();

    // 2. Launch SeriousPython with the assigned port
    SeriousPython.run(
      environmentVariables: {'PORT': _port.toString()},
      sync: false,
    );

    // 3. Poll /ping until the Flask daemon is healthy
    final stopwatch = Stopwatch()..start();
    while (stopwatch.elapsed < timeout) {
      if (await ping()) {
        _isStarted = true;
        return;
      }
      await Future.delayed(const Duration(milliseconds: 300));
    }

    throw EngineBootTimeoutException(
      'SeriousPython host daemon failed to respond on 127.0.0.1:$_port within ${timeout.inSeconds} seconds.',
    );
  }

  /// Sends a health check request to the daemon.
  Future<bool> ping() async {
    if (_port == null) return false;
    try {
      final client = _httpClient ?? http.Client();
      final response = await client.get(
        Uri.parse('http://127.0.0.1:$_port/ping'),
      );
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Dynamically loads an already unzipped plugin directory into the Python runtime.
  Future<Map<String, dynamic>> loadPlugin(
    String pluginDir, {
    String moduleName = 'main',
  }) async {
    if (!_isStarted) {
      throw const PluginLoadException(
        'Host engine has not been started. Call start() before loading a plugin.',
      );
    }

    final client = _httpClient ?? http.Client();
    final response = await client.post(
      Uri.parse('http://127.0.0.1:$_port/load_plugin'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'plugin_dir': pluginDir, 'module_name': moduleName}),
    );

    if (response.statusCode != 200) {
      throw PluginLoadException('Failed to load plugin: ${response.body}');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    _loadedPluginName = data['loaded'] as String?;
    return data;
  }

  /// Unpacks a plugin archive (.zip) into the designated directory and dynamically loads it.
  /// If [targetDir] is omitted, unpacks into '<appSupportDir>/plugins/audio_source/<zipName>'.
  Future<Map<String, dynamic>> loadPluginFromZip(
    File zipFile, {
    Directory? targetDir,
    String moduleName = 'main',
  }) async {
    if (!zipFile.existsSync()) {
      throw PluginLoadException('Plugin archive not found at: ${zipFile.path}');
    }

    // Determine target extraction directory
    final Directory destination;
    if (targetDir != null) {
      destination = targetDir;
    } else {
      final appSupport = await getApplicationSupportDirectory();
      final zipName = p.basenameWithoutExtension(zipFile.path);
      destination = Directory(
        p.join(appSupport.path, 'plugins', 'audio_source', zipName),
      );
    }

    // Clean destination directory if already present
    if (destination.existsSync()) {
      destination.deleteSync(recursive: true);
    }
    destination.createSync(recursive: true);

    // Unpack archive safely
    final bytes = zipFile.readAsBytesSync();
    final archive = ZipDecoder().decodeBytes(bytes);

    for (final file in archive) {
      final filename = p.join(destination.path, file.name);
      if (file.isFile) {
        File(filename)
          ..createSync(recursive: true)
          ..writeAsBytesSync(file.content as List<int>);
      } else {
        Directory(filename).createSync(recursive: true);
      }
    }

    // Dynamically inject unzipped plugin directory into Python runtime
    return loadPlugin(destination.path, moduleName: moduleName);
  }

  /// Resolves track metadata via fast search and immediate primary stream resolution (~1.1s).
  Future<ResolvedTrackPlayback> resolveTrack({
    required String title,
    List<String> artists = const [],
    int durationMs = 0,
    AudioQuality quality = AudioQuality.high,
  }) async {
    if (!_isStarted) {
      throw const StreamResolutionException(
        'Host engine is not running. Call start() and loadPlugin() first.',
      );
    }

    final client = _httpClient ?? http.Client();
    final response = await client.post(
      Uri.parse('http://127.0.0.1:$_port/resolve_track'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'track': {'name': title, 'artists': artists, 'duration_ms': durationMs},
        'quality': quality.toJson(),
      }),
    );

    if (response.statusCode != 200) {
      throw StreamResolutionException(
        'Failed to resolve track playback: ${response.body}',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return ResolvedTrackPlayback.fromJson(data);
  }

  /// Resolves a playable direct audio stream on-demand for a chosen candidate ID (~0.7s).
  Future<AudioStreamResponse> resolveStream({
    required String candidateId,
    AudioQuality quality = AudioQuality.high,
  }) async {
    if (!_isStarted) {
      throw const StreamResolutionException(
        'Host engine is not running. Call start() and loadPlugin() first.',
      );
    }

    final client = _httpClient ?? http.Client();
    final response = await client.post(
      Uri.parse('http://127.0.0.1:$_port/resolve_stream'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'candidate_id': candidateId,
        'quality': quality.toJson(),
      }),
    );

    if (response.statusCode != 200) {
      throw StreamResolutionException(
        'Failed to resolve audio stream: ${response.body}',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    return AudioStreamResponse.fromJson(data);
  }

  /// Terminates SeriousPython runtime and disposes the HTTP client.
  void stop() {
    try {
      SeriousPython.terminate();
    } catch (_) {}
    _httpClient?.close();
    _httpClient = null;
    _isStarted = false;
    _loadedPluginName = null;
    _port = null;
  }
}
