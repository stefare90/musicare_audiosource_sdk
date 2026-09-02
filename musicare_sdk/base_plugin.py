from abc import ABC, abstractmethod
from typing import List
from .types import Track, AudioQuality, AudioStreamResponse


class BaseAudioSourcePlugin(ABC):
    """
    Mandatory abstract base interface for all MusicAre Audio Source plugins.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique plugin reverse-DNS identifier (e.g. 'org.musicare.audiosource.youtube')."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name for the plugin (e.g. 'MusicAre YouTube Audio Source')."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """SemVer version string of the plugin (e.g. '1.0.0')."""
        pass

    @abstractmethod
    def get_stream(self, track: Track, quality: AudioQuality) -> List[AudioStreamResponse]:
        """
        Resolves track metadata into an ordered list of playable audio stream sources,
        sorted descending by adherence score.
        """
        pass