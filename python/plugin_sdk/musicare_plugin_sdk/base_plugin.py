from abc import ABC, abstractmethod
from typing import List
from .models import AudioQuality, AudioStreamResponse, CandidateTrack, Track


class BaseAudioSourcePlugin(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique reverse-domain plugin identifier."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable display name of the plugin."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version string of the plugin."""
        pass

    @abstractmethod
    def search_candidates(self, track: Track) -> List[CandidateTrack]:
        """Search platform and return lightweight metadata candidates (fast: < 0.4s)."""
        pass

    @abstractmethod
    def resolve_stream(
        self, candidate_id: str, quality: AudioQuality = AudioQuality.HIGH
    ) -> AudioStreamResponse:
        """Extract direct audio stream URL for a specific candidate_id (~0.7s)."""
        pass
