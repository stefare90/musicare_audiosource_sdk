class MusicAreSDKException(Exception):
    """Base exception for the MusicAre SDK."""
    pass


class StreamResolutionError(MusicAreSDKException):
    """Raised when an audio stream cannot be resolved for a requested track."""
    pass


class PluginMetadataError(MusicAreSDKException):
    """Raised when plugin metadata or manifest contracts are invalid."""
    pass