from .base_plugin import BaseAudioSourcePlugin
from .models import (
    AudioQuality,
    AudioStreamResponse,
    CandidateTrack,
    LoadPluginRequest,
    ResolveStreamRequest,
    ResolveTrackRequest,
    ResolvedTrackPlayback,
    Track,
)

__all__ = [
    "AudioQuality",
    "AudioStreamResponse",
    "CandidateTrack",
    "LoadPluginRequest",
    "ResolveStreamRequest",
    "ResolveTrackRequest",
    "ResolvedTrackPlayback",
    "Track",
    "BaseAudioSourcePlugin",
]

try:
    from .matcher import TrackMatcher

    __all__.append("TrackMatcher")
except ImportError:
    pass
