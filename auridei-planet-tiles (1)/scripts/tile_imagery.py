"""
Cut a global Simple Cylindrical (equirectangular) mosaic into Cesium imagery
tiles: GeographicTilingScheme, 256x256 px, XYZ numbering (y = 0 at the north),
folders  <out>/<z>/<x>/<y>.jpg   — the same layout Venus uses.

Works directly in pixel space, so the source file needs no coordinate system:
the mosaic just has to cover the whole planet (-180..180 lon, 90..-90 lat).

Usage (inside the GDAL Docker container):
  python3 tile_imagery.py SOURCE.tif OUT_DIR --max-zoom 8 [--workers 8] [--quality 85]

Re-running skips tiles that already exist, so it can be stopped and resumed.
"""
import argparse, os, sys, time
from multiprocessing import Pool
from osgeo import gdal

gdal.UseExceptions()
gdal.SetCacheMax(512 * 1024 * 1024)

SRC = None
ARGS = None


def init(src_path, args):
    global SRC, ARGS
    SRC = gdal.Open(src_path)
    ARGS = args


def tile_job(job):
    z, x = job
    W, H = SRC.RasterXSize, SRC.RasterYSize
    tiles_y = 2 ** z
    deg = 180.0 / tiles_y                      # tile size in degrees
    made = 0
    for y in range(tiles_y):
        out = os.path.join(ARGS.out, str(z), str(x), f"{y}.{ARGS.ext}")
        if os.path.exists(out):
            continue
        west = -180.0 + x * deg
        north = 90.0 - y * deg
        # degrees -> source pixels (float), then clamp to the raster
        px0 = (west + 180.0) / 360.0 * W
        py0 = (90.0 - north) / 180.0 * H
        pw = deg / 360.0 * W
        ph = deg / 180.0 * H
        os.makedirs(os.path.dirname(out), exist_ok=True)
        opts = gdal.TranslateOptions(
            format='JPEG' if ARGS.ext == 'jpg' else 'PNG',
            srcWin=[px0, py0, pw, ph],
            width=ARGS.size, height=ARGS.size,
            resampleAlg='average' if pw > ARGS.size else 'bilinear',
            creationOptions=[f'QUALITY={ARGS.quality}'] if ARGS.ext == 'jpg' else [],
            bandList=[1, 2, 3] if SRC.RasterCount >= 3 else [1],
        )
        tmp = out + '.part'
        gdal.Translate(tmp, SRC, options=opts)
        for extra in (tmp + '.aux.xml',):
            if os.path.exists(extra):
                os.remove(extra)
        os.replace(tmp, out)
        made += 1
    return made


def main():
    p = argparse.ArgumentParser()
    p.add_argument('source')
    p.add_argument('out')
    p.add_argument('--max-zoom', type=int, default=8)
    p.add_argument('--min-zoom', type=int, default=0)
    p.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) - 1))
    p.add_argument('--quality', type=int, default=85)
    p.add_argument('--size', type=int, default=256)
    p.add_argument('--ext', choices=['jpg', 'png'], default='jpg')
    args = p.parse_args()

    ds = gdal.Open(args.source)
    print(f'Source: {ds.RasterXSize} x {ds.RasterYSize}, {ds.RasterCount} band(s)')
    if ds.GetRasterBand(1).GetOverviewCount() == 0:
        print('Note: no overviews found. Low zoom levels will be slow; run gdaladdo first (see README).')
    ds = None

    jobs = [(z, x) for z in range(args.min_zoom, args.max_zoom + 1) for x in range(2 ** (z + 1))]
    total_tiles = sum(2 ** (z + 1) * 2 ** z for z in range(args.min_zoom, args.max_zoom + 1))
    print(f'Zoom {args.min_zoom}-{args.max_zoom}: {total_tiles:,} tiles, {args.workers} workers')
    t0 = time.time(); done = 0
    with Pool(args.workers, initializer=init, initargs=(args.source, args)) as pool:
        for i, n in enumerate(pool.imap_unordered(tile_job, jobs), 1):
            done += n
            if i % 50 == 0 or i == len(jobs):
                print(f'  columns {i}/{len(jobs)}  new tiles {done:,}  {time.time()-t0:,.0f}s', flush=True)
    print('Imagery tiles done.')


if __name__ == '__main__':
    main()
