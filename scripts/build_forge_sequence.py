"""Turn the Higgsfield "forge" film into a scroll-scrub image sequence.

    .venv/bin/python scripts/build_forge_sequence.py assets/generated/home-forge-d90931a5.mp4

Why an image sequence and not <video> seeking: frame-accurate scrubbing in
both directions is smooth and identical in every browser (Safari's seek
latency on long-GOP H.264 makes video scrubbing stutter). Output directories
are versioned by the source request id, so the files can be cached forever.

Outputs (under business_page/static/business_page/seq/forge-<id>/):
  d/0001.webp …   desktop frames, 1600×800 (every 2nd source frame)
  m/0001.webp …   mobile frames,   800×400 (every 4th source frame)
  key-1..5.{webp,jpg}  chapter stills for reduced-motion / posters / About
  manifest.json   frame counts and sizes, read by the page
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
src = Path(sys.argv[1]).resolve()
rid = src.stem.rsplit('-', 1)[-1]
out = ROOT / 'business_page' / 'static' / 'business_page' / 'seq' / f'forge-{rid}'
FF = imageio_ffmpeg.get_ffmpeg_exe()

# Crop to 2:1 from the top: removes faint embossed lettering the model put on
# the anvil's lower face (rows ≳ 960) and gives a cinematic letterbox ratio.
CROP = 'crop=1920:960:0:0'

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([FF, '-loglevel', 'error', '-i', str(src), '-vf', CROP, '-an',
                    f'{tmp}/%04d.png'], check=True)
    frames = sorted(Path(tmp).glob('*.png'))
    print(f'{len(frames)} source frames')
    plans = {'d': (2, (1600, 800), 68), 'm': (4, (800, 400), 62)}
    counts = {}
    for key, (step, size, quality) in plans.items():
        d = out / key
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob('*.webp'):
            old.unlink()
        picked = frames[::step]
        for i, f in enumerate(picked, 1):
            Image.open(f).convert('RGB').resize(size, Image.LANCZOS).save(
                d / f'{i:04d}.webp', 'WEBP', quality=quality, method=6)
        counts[key] = len(picked)
        total = sum(p.stat().st_size for p in d.glob('*.webp'))
        print(f'{key}: {len(picked)} frames, {total/1e6:.2f} MB')
    # Chapter stills at the five narrative beats (fractions of the film).
    beats = [0.02, 0.3, 0.52, 0.74, 0.985]
    for n, frac in enumerate(beats, 1):
        f = frames[min(len(frames) - 1, int(frac * (len(frames) - 1)))]
        im = Image.open(f).convert('RGB').resize((1600, 800), Image.LANCZOS)
        im.save(out / f'key-{n}.webp', 'WEBP', quality=74, method=6)
        im.save(out / f'key-{n}.jpg', 'JPEG', quality=80, optimize=True, progressive=True)

(out / 'manifest.json').write_text(json.dumps({
    'source': str(src.relative_to(ROOT)), 'request_id_prefix': rid,
    'desktop': {'count': counts['d'], 'width': 1600, 'height': 800, 'dir': 'd'},
    'mobile': {'count': counts['m'], 'width': 800, 'height': 400, 'dir': 'm'},
    'keys': 5,
}, indent=2) + '\n')
print('→', out.relative_to(ROOT))
