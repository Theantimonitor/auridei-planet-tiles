"""
Prepare Cesium quantized-mesh terrain for plain static hosting:
cesium-terrain-builder writes every .terrain tile gzip-compressed, which only
works if the server adds a 'Content-Encoding: gzip' header. Unzipping them here
means any static host (Cloudflare R2, Firebase) serves them correctly as-is.

Usage: python3 finish_terrain.py TERRAIN_DIR
"""
import gzip, os, sys

root = sys.argv[1]
n = 0
for dirpath, _, files in os.walk(root):
    for f in files:
        if not f.endswith('.terrain'):
            continue
        path = os.path.join(dirpath, f)
        with open(path, 'rb') as fh:
            data = fh.read()
        if data[:2] == b'\x1f\x8b':
            with open(path, 'wb') as fh:
                fh.write(gzip.decompress(data))
            n += 1
print(f'Unzipped {n:,} terrain tiles in {root}')
