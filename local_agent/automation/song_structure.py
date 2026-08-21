"""Read-only Studio One .song structure inspection."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET


class SongStructureError(RuntimeError):
    pass


@dataclass(frozen=True)
class SongTrack:
    index: int
    name: str
    channel_type: str
    channel_id: str


def read_song_tracks(song_path: Path) -> list[SongTrack]:
    if not song_path.is_file():
        raise SongStructureError(f"Studio One song not found: {song_path}")
    try:
        with ZipFile(song_path, "r") as archive:
            raw = archive.read("Song/song.xml")
        root = ET.fromstring(raw.replace(b"x:", b"x_"))
    except (BadZipFile, KeyError, OSError, ET.ParseError) as exc:
        raise SongStructureError(f"Unable to read Studio One song structure: {exc}") from exc
    tracks = []
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "MediaTrack":
            continue
        setup = next((node for node in element.iter() if node.tag.rsplit("}", 1)[-1] == "SpeakerSetup"), None)
        channel_type = (setup.get("type", "") if setup is not None else "").strip().capitalize()
        if channel_type not in {"Stereo", "Mono"}:
            continue
        channel_id = element.get("channelID", "")
        tracks.append(SongTrack(len(tracks) + 1, element.get("name", "").strip(), channel_type, channel_id))
    if not tracks:
        raise SongStructureError("No Stereo/Mono MediaTrack found")
    return tracks


def target_track_indexes(song_path: Path) -> dict[str, int]:
    tracks = read_song_tracks(song_path)
    stereo = [track.index for track in tracks if track.channel_type == "Stereo"]
    mono = [track.index for track in tracks if track.channel_type == "Mono"]
    if len(stereo) != 1 or len(mono) != 1:
        raise SongStructureError("Template must contain exactly one Stereo and one Mono track")
    return {"accompaniment": stereo[0], "vocal": mono[0]}
