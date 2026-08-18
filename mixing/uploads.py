from __future__ import annotations

import os
import struct
import wave
from pathlib import Path


ALLOWED_EXTENSIONS = {"wav", "mp3"}


class UploadError(ValueError):
    pass


def safe_display_name(filename: str) -> str:
    name = Path(filename or "audio").name.strip().replace("\x00", "")
    return name[:140] or "audio"


def _inspect_wav(path: Path) -> dict:
    try:
        with wave.open(str(path), "rb") as audio:
            rate = audio.getframerate()
            frames = audio.getnframes()
            channels = audio.getnchannels()
            duration = round(frames / rate, 3) if rate else None
            return {"format": "wav", "sample_rate": rate, "channels": channels, "duration_seconds": duration}
    except (wave.Error, EOFError) as exc:
        raise UploadError("无法读取 WAV 音频信息，文件可能已损坏") from exc


def _inspect_mp3(path: Path) -> dict:
    # Lightweight MPEG frame scan. It intentionally validates only enough metadata
    # for upload eligibility; audio conversion is not part of the mixing engine.
    data = path.read_bytes()[:256 * 1024]
    offset = 10 + int.from_bytes(data[6:10], "big") if data.startswith(b"ID3") and len(data) >= 10 else 0
    for index in range(offset, max(offset, len(data) - 4)):
        header = int.from_bytes(data[index:index + 4], "big")
        if header >> 21 != 0x7FF:
            continue
        version_id = (header >> 19) & 0b11
        layer = (header >> 17) & 0b11
        bitrate_index = (header >> 12) & 0b1111
        sample_index = (header >> 10) & 0b11
        if version_id == 1 or layer != 1 or bitrate_index in {0, 15} or sample_index == 3:
            continue
        version = "mpeg1" if version_id == 3 else "mpeg2"
        bitrates = {
            "mpeg1": [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
            "mpeg2": [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
        }
        sample_rates = {3: [44100, 48000, 32000], 2: [22050, 24000, 16000], 0: [11025, 12000, 8000]}
        rate = sample_rates.get(version_id, [0, 0, 0])[sample_index]
        bitrate = bitrates[version][bitrate_index] * 1000
        if not rate or not bitrate:
            continue
        return {
            "format": "mp3",
            "sample_rate": rate,
            "channels": 1 if ((header >> 6) & 0b11) == 3 else 2,
            "duration_seconds": round(path.stat().st_size * 8 / bitrate, 3),
        }
    raise UploadError("无法读取 MP3 音频信息，文件可能已损坏")


def inspect_audio(path: Path) -> dict:
    header = path.read_bytes()[:16]
    if header.startswith(b"RIFF") and header[8:12] == b"WAVE":
        return _inspect_wav(path)
    if header.startswith(b"ID3") or (len(header) >= 2 and header[0] == 0xFF and header[1] & 0xE0 == 0xE0):
        return _inspect_mp3(path)
    raise UploadError("格式不支持，仅允许有效的 WAV 或 MP3 文件")


def parse_multipart(content_type: str, body: bytes) -> dict[str, list[dict]]:
    """Minimal multipart parser for the small, controlled demo API surface."""
    marker = "boundary="
    if marker not in content_type:
        raise UploadError("上传请求格式错误")
    boundary = content_type.split(marker, 1)[1].strip().strip('"').encode("utf-8")
    if not boundary:
        raise UploadError("上传请求缺少 boundary")
    parts: dict[str, list[dict]] = {}
    for raw_part in body.split(b"--" + boundary):
        if not raw_part or raw_part in {b"--\r\n", b"--"}:
            continue
        raw_part = raw_part.lstrip(b"\r\n")
        if b"\r\n\r\n" not in raw_part:
            continue
        raw_headers, value = raw_part.split(b"\r\n\r\n", 1)
        value = value.rstrip(b"\r\n")
        headers = raw_headers.decode("utf-8", errors="replace")
        disposition = next((line for line in headers.split("\r\n") if line.lower().startswith("content-disposition:")), "")
        if "name=\"" not in disposition:
            continue
        name = disposition.split('name="', 1)[1].split('"', 1)[0]
        filename = ""
        if 'filename="' in disposition:
            filename = disposition.split('filename="', 1)[1].split('"', 1)[0]
        parts.setdefault(name, []).append({"filename": filename, "content": value})
    return parts
