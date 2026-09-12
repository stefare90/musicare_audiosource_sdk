from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AudioQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_string(cls, value: Optional[str]) -> "AudioQuality":
        clean_val = value.lower() if value else "high"
        for item in cls:
            if item.value == clean_val:
                return item
        return cls.HIGH


@dataclass
class Track:
    name: str
    artists: List[str] = field(default_factory=list)
    duration_ms: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> "Track":
        if not isinstance(data, dict):
            raise ValueError("Track payload must be a JSON object")
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Track 'name' is required and cannot be empty")

        raw_artists = data.get("artists", [])
        artists: List[str] = []
        for a in raw_artists:
            if isinstance(a, dict):
                artist_name = a.get("name")
                if artist_name:
                    artists.append(str(artist_name).strip())
            elif isinstance(a, str) and a.strip():
                artists.append(a.strip())

        return cls(
            name=name,
            artists=artists,
            duration_ms=int(data.get("duration_ms", 0)),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "artists": self.artists,
            "duration_ms": self.duration_ms,
        }


@dataclass
class AudioStreamResponse:
    url: str
    quality: AudioQuality
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    expires_at: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "AudioStreamResponse":
        if not isinstance(data, dict):
            raise ValueError("AudioStreamResponse payload must be a JSON object")
        url = str(data.get("url", "")).strip()
        if not url:
            raise ValueError("Stream 'url' is required")

        quality_val = data.get("quality", "high")
        return cls(
            url=url,
            quality=AudioQuality.from_string(quality_val),
            codec=data.get("codec"),
            bitrate=data.get("bitrate"),
            expires_at=data.get("expires_at"),
            headers=dict(data.get("headers", {})),
        )

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "quality": self.quality.value if isinstance(self.quality, AudioQuality) else str(self.quality),
            "codec": self.codec,
            "bitrate": self.bitrate,
            "expires_at": self.expires_at,
            "headers": self.headers,
        }


@dataclass
class CandidateTrack:
    id: str
    title: str
    artist: Optional[str] = None
    duration_ms: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> "CandidateTrack":
        if not isinstance(data, dict):
            raise ValueError("CandidateTrack payload must be a JSON object")
        candidate_id = str(data.get("id", "")).strip()
        if not candidate_id:
            raise ValueError("Candidate 'id' is required")
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Candidate 'title' is required")

        return cls(
            id=candidate_id,
            title=title,
            artist=data.get("artist"),
            duration_ms=data.get("duration_ms"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "duration_ms": self.duration_ms,
        }


@dataclass
class ResolvedTrackPlayback:
    stream: AudioStreamResponse
    candidates: List[CandidateTrack]
    active_candidate_id: str

    @classmethod
    def from_dict(cls, data: dict) -> "ResolvedTrackPlayback":
        if not isinstance(data, dict):
            raise ValueError("ResolvedTrackPlayback payload must be a JSON object")

        raw_stream = data.get("stream")
        if not raw_stream:
            raise ValueError("Missing 'stream' in playback payload")
        stream = (
            AudioStreamResponse.from_dict(raw_stream)
            if isinstance(raw_stream, dict)
            else raw_stream
        )

        raw_candidates = data.get("candidates", [])
        candidates = [
            CandidateTrack.from_dict(c) if isinstance(c, dict) else c
            for c in raw_candidates
        ]
        active_id = str(data.get("active_candidate_id", "")).strip()
        if not active_id:
            raise ValueError("Missing 'active_candidate_id' in playback payload")

        return cls(
            stream=stream,
            candidates=candidates,
            active_candidate_id=active_id,
        )

    def to_dict(self) -> dict:
        return {
            "stream": self.stream.to_dict() if hasattr(self.stream, "to_dict") else self.stream,
            "candidates": [c.to_dict() if hasattr(c, "to_dict") else c for c in self.candidates],
            "active_candidate_id": self.active_candidate_id,
        }


@dataclass
class ResolveTrackRequest:
    track: Track
    quality: AudioQuality = AudioQuality.HIGH

    @classmethod
    def from_dict(cls, data: dict) -> "ResolveTrackRequest":
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        raw_track = data.get("track")
        if not raw_track:
            raise ValueError("Missing required field: 'track'")
        track = Track.from_dict(raw_track)
        quality = AudioQuality.from_string(data.get("quality", "high"))
        return cls(track=track, quality=quality)

    def to_dict(self) -> dict:
        return {
            "track": self.track.to_dict(),
            "quality": self.quality.value,
        }


@dataclass
class ResolveStreamRequest:
    candidate_id: str
    quality: AudioQuality = AudioQuality.HIGH

    @classmethod
    def from_dict(cls, data: dict) -> "ResolveStreamRequest":
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        candidate_id = str(data.get("candidate_id", "")).strip()
        if not candidate_id:
            raise ValueError("Missing required field: 'candidate_id'")
        quality = AudioQuality.from_string(data.get("quality", "high"))
        return cls(candidate_id=candidate_id, quality=quality)

    def to_dict(self) -> dict:
        return {
            "candidate_id": self.candidate_id,
            "quality": self.quality.value,
        }


@dataclass
class LoadPluginRequest:
    plugin_dir: str
    module_name: str = "main"

    @classmethod
    def from_dict(cls, data: dict) -> "LoadPluginRequest":
        if not isinstance(data, dict):
            raise ValueError("Request body must be a JSON object")
        plugin_dir = str(data.get("plugin_dir", "")).strip()
        if not plugin_dir:
            raise ValueError("Missing required field: 'plugin_dir'")
        module_name = str(data.get("module_name", "main")).strip() or "main"
        return cls(plugin_dir=plugin_dir, module_name=module_name)

    def to_dict(self) -> dict:
        return {
            "plugin_dir": self.plugin_dir,
            "module_name": self.module_name,
        }
