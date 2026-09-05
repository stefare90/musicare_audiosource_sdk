/// Base sealed exception for all errors thrown by the MusicAre Dart Host SDK.
sealed class MusicAreHostException implements Exception {
  final String message;
  const MusicAreHostException(this.message);

  @override
  String toString() => '$runtimeType: $message';
}

/// Thrown when the embedded SeriousPython daemon fails to answer /ping within the timeout.
class EngineBootTimeoutException extends MusicAreHostException {
  const EngineBootTimeoutException(super.message);
}

/// Thrown when a plugin's sdkConstraint does not satisfy the host's current SDK version.
class IncompatiblePluginException extends MusicAreHostException {
  const IncompatiblePluginException(super.message);
}

/// Thrown when an inspected plugin zip contains compiled native C/C++ binaries (.so, .pyd, .dylib, .dll).
class PurePythonViolationException extends MusicAreHostException {
  final List<String> detectedBinaries;
  const PurePythonViolationException(
    super.message, {
    this.detectedBinaries = const [],
  });

  @override
  String toString() =>
      '$runtimeType: $message\nDetected non-portable binaries:\n${detectedBinaries.map((b) => ' - $b').join('\n')}';
}

/// Thrown when dynamic plugin injection or loading fails in the host daemon.
class PluginLoadException extends MusicAreHostException {
  const PluginLoadException(super.message);
}

/// Thrown when track resolution fails or yields no playable stream sources.
class StreamResolutionException extends MusicAreHostException {
  const StreamResolutionException(super.message);
}
