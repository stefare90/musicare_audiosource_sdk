import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:integration_test/integration_test.dart';
import 'package:musicare_dart_host_sdk/musicare_dart_host_sdk.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

const String kPluginUrlParam = String.fromEnvironment('PLUGIN_URL');

Future<File> downloadPluginZip(String url) async {
  final appSupportDir = await getApplicationSupportDirectory();
  final targetFile = File(p.join(appSupportDir.path, 'downloaded_plugin.zip'));

  if (targetFile.existsSync()) {
    targetFile.deleteSync();
  }

  final response = await http.get(Uri.parse(url));
  expect(
    response.statusCode,
    200,
    reason:
        'Failed to download plugin archive from: $url (HTTP ${response.statusCode})',
  );

  targetFile.writeAsBytesSync(response.bodyBytes);
  return targetFile;
}

Future<void> assertPlayableCdnStream(AudioStreamResponse stream) async {
  expect(
    stream.url,
    startsWith('https://'),
    reason: 'Stream URL must use secure HTTPS protocol',
  );
  expect(
    stream.bitrate,
    greaterThan(0),
    reason: 'Stream bitrate must be greater than 0 bps',
  );

  final requestHeaders = {...stream.headers, 'Range': 'bytes=0-1024'};

  final client = http.Client();
  try {
    final response = await client.get(
      Uri.parse(stream.url),
      headers: requestHeaders,
    );

    expect(
      [200, 206],
      contains(response.statusCode),
      reason:
          'CDN handshake failed. Expected HTTP 200 or 206, received ${response.statusCode}',
    );
    expect(
      response.bodyBytes.length,
      greaterThan(0),
      reason: 'CDN returned empty response body',
    );
  } finally {
    client.close();
  }
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  HttpOverrides.global = null;

  group('Audio Source Plugin Compliance Suite', () {
    final client = AudioSourceClient();

    setUpAll(() async {
      expect(
        kPluginUrlParam,
        isNotEmpty,
        reason:
            'Target plugin URL missing. Provide --dart-define=PLUGIN_URL=http://...',
      );

      // 1. Simulates real OTA download from local HTTP server
      final zipFile = await downloadPluginZip(kPluginUrlParam);

      // 2. Boot SeriousPython host daemon
      await client.start();
      expect(
        client.isStarted,
        isTrue,
        reason: 'Failed to boot SeriousPython host daemon',
      );

      // 3. Unpack and dynamically inject the downloaded plugin archive
      final loadResult = await client.loadPluginFromZip(zipFile);
      expect(
        loadResult['success'],
        isTrue,
        reason: 'Plugin dynamic injection failed',
      );
      expect(
        loadResult['loaded'],
        isNotNull,
        reason: 'Plugin display name is null or undefined',
      );
    });

    tearDownAll(() {
      client.stop();
    });

    testWidgets(
      'resolves stream and validates CDN playback for canonical track',
      (tester) async {
        final streams = await client.getStream(
          title: 'Come Together',
          artists: ['The Beatles'],
          durationMs: 259000,
          quality: AudioQuality.high,
        );

        expect(
          streams,
          isNotEmpty,
          reason: 'Plugin returned zero audio stream candidates',
        );

        final primaryStream = streams.first;
        await assertPlayableCdnStream(primaryStream);
      },
    );
  });
}
