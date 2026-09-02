from dataclasses import dataclass, field
from typing import List, Optional, Dict, Literal

AudioQuality = Literal['low', 'medium', 'high']


@dataclass
class Artist:
    name: str

    def to_dict(self) -> dict:
        return {'name': self.name}

    @classmethod
    def from_dict(cls, data: dict) -> 'Artist':
        return cls(name=data.get('name', ''))


@dataclass
class Track:
    name: str
    artists: List[Artist] = field(default_factory=list)
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'artists': [a.to_dict() for a in self.artists],
            'durationMs': self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Track':
        raw_artists = data.get('artists', [])
        artists = [
            Artist.from_dict(a) if isinstance(a, dict) else Artist(name=str(a))
            for a in raw_artists
        ]
        return cls(
            name=data.get('name', ''),
            artists=artists,
            duration_ms=int(data.get('durationMs', data.get('duration_ms', 0))),
        )


@dataclass
class AudioStreamResponse:
    url: str
    quality: AudioQuality
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    expires_at: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'url': self.url,
            'quality': self.quality,
            'codec': self.codec,
            'bitrate': self.bitrate,
            'expiresAt': self.expires_at,
            'headers': self.headers,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'AudioStreamResponse':
        return cls(
            url=data.get('url', ''),
            quality=data.get('quality', 'high'),
            codec=data.get('codec'),
            bitrate=data.get('bitrate'),
            expires_at=data.get('expiresAt', data.get('expires_at')),
            headers=data.get('headers', {}) or {},
        )