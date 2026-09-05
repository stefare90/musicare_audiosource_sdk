from .types import AudioQuality, Artist, Track, AudioStreamResponse
from .base_plugin import BaseAudioSourcePlugin
from .matcher import CandidateTrack, TrackMatcher
from .exceptions import MusicAreSDKException, StreamResolutionError, PluginMetadataError

__version__ = "1.0.0"

__all__ = [
    "AudioQuality",
    "Artist",
    "Track",
    "AudioStreamResponse",
    "BaseAudioSourcePlugin",
    "CandidateTrack",
    "TrackMatcher",
    "MusicAreSDKException",
    "StreamResolutionError",
    "PluginMetadataError",
]