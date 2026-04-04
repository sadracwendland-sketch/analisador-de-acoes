from __future__ import annotations

import os
import struct
import zlib
from pathlib import Path

OUT_DIR = Path('/home/user/stock-analyzer/web/static')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xFFFFFFFF)


def make_png(path: Path, size: int) -> None:
    width = height = size
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            cx = x - width / 2
            cy = y - height / 2
            dist = (cx * cx + cy * cy) ** 0.5
            if dist < width * 0.32:
                r, g, b = 34, 197, 94
            elif dist < width * 0.36:
                r, g, b = 56, 189, 248
            else:
                r, g, b = 2, 6, 23
            if abs(x - y) < max(2, size // 48):
                r, g, b = 168, 85, 247
            raw.extend([r, g, b, 255])
    ihdr = struct.pack('!IIBBBBB', width, height, 8, 6, 0, 0, 0)
    data = b'\x89PNG\r\n\x1a\n' + png_chunk(b'IHDR', ihdr) + png_chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + png_chunk(b'IEND', b'')
    path.write_bytes(data)


make_png(OUT_DIR / 'icon-192.png', 192)
make_png(OUT_DIR / 'icon-512.png', 512)
print('icons generated')
