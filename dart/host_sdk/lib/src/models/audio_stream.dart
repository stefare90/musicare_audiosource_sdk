/// Target audio stream bitrate/resolution quality.
enum AudioQuality {
  low,
  medium,
  high;

  String toJson() => name;

  static AudioQuality fromJson(String value) {
    switch (value.toLowerCase()) {
      case 'low':
        return AudioQuality.low;
      case 'medium':
        return AudioQuality.medium;
      case 'high':
      default:
        return AudioQuality.high;
    }
  }
}

/// Resolved playable audio stream entity returned by audio source plugins.
class AudioStreamResponse {
  final String url;
  final AudioQuality quality;
  final String? codec;
  final int? bitrate;
  final int? expiresAt;
  final Map<String, String> headers;

  const AudioStreamResponse({
    required this.url,
    required this.quality,
    this.codec,
    this.bitrate,
    this.expiresAt,
    this.headers = const {},
  });

  factory AudioStreamResponse.fromJson(Map<String, dynamic> json) {
    return AudioStreamResponse(
      url: json['url'] as String? ?? '',
      quality: AudioQuality.fromJson(json['quality'] as String? ?? 'high'),
      codec: json['codec'] as String?,
      bitrate: json['bitrate'] as int?,
      expiresAt: json['expiresAt'] as int?,
      headers: (json['headers'] as Map?)?.cast<String, String>() ?? const {},
    );
  }

  Map<String, dynamic> toJson() => {
    'url': url,
    'quality': quality.toJson(),
    'codec': codec,
    'bitrate': bitrate,
    'expiresAt': expiresAt,
    'headers': headers,
  };

  @override
  String toString() =>
      'AudioStreamResponse(url: $url, quality: $quality, codec: $codec, bitrate: $bitrate, expiresAt: $expiresAt)';
}
