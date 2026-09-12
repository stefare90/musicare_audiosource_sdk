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
      expiresAt: json['expires_at'] as int? ?? json['expiresAt'] as int?,
      headers: (json['headers'] as Map?)?.cast<String, String>() ?? const {},
    );
  }

  Map<String, dynamic> toJson() => {
    'url': url,
    'quality': quality.toJson(),
    'codec': codec,
    'bitrate': bitrate,
    'expires_at': expiresAt,
    'headers': headers,
  };

  @override
  String toString() =>
      'AudioStreamResponse(url: $url, quality: $quality, codec: $codec, bitrate: $bitrate, expiresAt: $expiresAt)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AudioStreamResponse &&
          runtimeType == other.runtimeType &&
          url == other.url &&
          quality == other.quality &&
          codec == other.codec &&
          bitrate == other.bitrate &&
          expiresAt == other.expiresAt;

  @override
  int get hashCode => Object.hash(url, quality, codec, bitrate, expiresAt);
}

/// Lightweight metadata candidate returned during the search phase.
class CandidateTrack {
  final String id;
  final String title;
  final String? artist;
  final int? durationMs;

  const CandidateTrack({
    required this.id,
    required this.title,
    this.artist,
    this.durationMs,
  });

  factory CandidateTrack.fromJson(Map<String, dynamic> json) {
    return CandidateTrack(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      artist: json['artist'] as String?,
      durationMs: json['duration_ms'] as int? ?? json['durationMs'] as int?,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    if (artist != null) 'artist': artist,
    if (durationMs != null) 'duration_ms': durationMs,
  };

  @override
  String toString() =>
      'CandidateTrack(id: $id, title: $title, artist: $artist, durationMs: $durationMs)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CandidateTrack &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          title == other.title &&
          artist == other.artist &&
          durationMs == other.durationMs;

  @override
  int get hashCode => Object.hash(id, title, artist, durationMs);
}

/// Composite payload containing the immediate playable stream and candidate list.
class ResolvedTrackPlayback {
  final AudioStreamResponse stream;
  final List<CandidateTrack> candidates;
  final String activeCandidateId;

  const ResolvedTrackPlayback({
    required this.stream,
    required this.candidates,
    required this.activeCandidateId,
  });

  factory ResolvedTrackPlayback.fromJson(Map<String, dynamic> json) {
    final rawCandidates = json['candidates'] as List<dynamic>? ?? const [];
    return ResolvedTrackPlayback(
      stream: AudioStreamResponse.fromJson(
        json['stream'] as Map<String, dynamic>? ?? const {},
      ),
      candidates: rawCandidates
          .map((c) => CandidateTrack.fromJson(c as Map<String, dynamic>))
          .toList(),
      activeCandidateId:
          json['active_candidate_id'] as String? ??
          json['activeCandidateId'] as String? ??
          '',
    );
  }

  Map<String, dynamic> toJson() => {
    'stream': stream.toJson(),
    'candidates': candidates.map((c) => c.toJson()).toList(),
    'active_candidate_id': activeCandidateId,
  };

  @override
  String toString() =>
      'ResolvedTrackPlayback(activeCandidateId: $activeCandidateId, candidatesCount: ${candidates.length}, stream: $stream)';
}
