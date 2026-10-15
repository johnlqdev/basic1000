"""Record the grammar films as MP4 files (not part of the website).

    python3 tools/video/render.py --out /work/out                 # all films, desktop and phone
    python3 tools/video/render.py --out /tmp/t --only sentence --layouts desktop --fake-audio --offline

Each film is drawn frame by frame by the site's own player (tools/video/frame.html loads films.js,
figures.js, grammar-data.js and the styles of index.html), at exact times computed from the real
recordings, so picture and sound are always in step and no frame is dropped. The sound track is
the same clips the site plays (Supabase storage, Daniel or Sarah), placed at those times.

    desktop  1920 x 1080 (16:9)      phone  1080 x 1920 (9:16)      30 frames a second, H.264 + AAC

Needs: playwright (Chromium), ffmpeg. --fake-audio uses silent clips of an estimated length
(for testing without network); --offline serves d3 from a local file and skips web fonts.
"""
import argparse
import hashlib
import http.server
import json
import multiprocessing as mp
import os
import re
import shutil
import socketserver
import subprocess
import threading
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AUDIO = 'https://duptugctgzemfczbtvgj.supabase.co/storage/v1/object/public/audio/v2/'
VOICES = {'man': 'us_daniel', 'woman': 'us_sarah'}
RATE = 48000
LAYOUTS = {'desktop': (1280, 720), 'phone': (720, 1280)}  # CSS px, recorded at 1.5x
SCALE = 1.5
LOCAL_D3 = '/opt/npm-tools/node_modules/d3/dist/d3.min.js'


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


def clip_url(text, voice):
    v = VOICES[voice]
    return AUDIO + v + '/' + hashlib.sha256((v + '|' + norm(text)).encode()).hexdigest()[:32] + '.mp3?r=2'


def serve(port):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=ROOT, **k)

        def log_message(self, *a):
            pass
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.ThreadingTCPServer(('127.0.0.1', port), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def open_page(pw, layout, offline):
    b = pw.chromium.launch(args=['--font-render-hinting=none'])
    w, h = LAYOUTS[layout]
    pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=SCALE)
    if offline:
        pg.route('https://cdnjs.cloudflare.com/**', lambda r: r.fulfill(path=LOCAL_D3, content_type='application/javascript'))
        pg.route('https://fonts.googleapis.com/**', lambda r: r.abort())
    return b, pg


def pcm(path):
    """decode an audio file to 48 kHz mono 16-bit samples (bytes)"""
    return subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(RATE), '-'],
                          check=True, capture_output=True).stdout


def fetch_clips(films, cache, fake):
    """download every clip once; returns {(text, voice): pcm bytes}"""
    os.makedirs(cache, exist_ok=True)
    out = {}
    for f in films:
        for l in f['lines']:
            key = (norm(l['t']), l['v'])
            if key in out:
                continue
            if fake:  # silence of a plausible length: 0.9 s of padding + 0.4 s a word
                out[key] = b'\0\0' * int(RATE * (0.9 + 0.4 * len(l['t'].split())))
                continue
            path = os.path.join(cache, hashlib.md5(repr(key).encode()).hexdigest() + '.mp3')
            if not os.path.exists(path):
                for attempt in range(5):
                    try:
                        with urllib.request.urlopen(clip_url(*key), timeout=60) as r, open(path + '.part', 'wb') as w:
                            shutil.copyfileobj(r, w)
                        os.replace(path + '.part', path)
                        break
                    except Exception as e:
                        if attempt == 4:
                            raise RuntimeError(f'clip missing for {key}: {e}')
                        time.sleep(2 * (attempt + 1))
            out[key] = pcm(path)
    return out


def build_job(job):
    """record one film in one layout: frames from the page + the sound track -> MP4"""
    from playwright.sync_api import sync_playwright
    a = job['args']
    with sync_playwright() as pw:
        b, pg = open_page(pw, job['layout'], a['offline'])
        pg.goto(f"http://127.0.0.1:{a['port']}/tools/video/frame.html")
        pg.wait_for_function('window.BASIC_FILMS && window.listFilms')
        info = pg.evaluate('([id, layout, n, count, durs]) => setupFilm(id, layout, n, count, durs)',
                           [job['id'], job['layout'], job['number'], job['count'], job['durs']])
        total = info['total']
        # sound: each clip at the moment its line begins
        track = bytearray(b'\0\0' * (int(round(total * RATE)) + RATE // 10))
        for s, starts in enumerate(info['starts']):
            for k, t0 in enumerate(starts):
                data = job['pcm'][s][k]
                i = int(round(t0 * RATE)) * 2
                track[i:i + len(data)] = data
        wav = job['out'] + '.s16'
        with open(wav, 'wb') as w:
            w.write(track)
        fps = a['fps']
        n_frames = int(total * fps) + 1
        w, h = (int(x * SCALE) for x in LAYOUTS[job['layout']])
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y',
                                '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'mjpeg', '-i', '-',
                                '-f', 's16le', '-ar', str(RATE), '-ac', '1', '-i', wav,
                                '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', a['preset'], '-crf', str(a['crf']),
                                '-pix_fmt', 'yuv420p', '-vf', f'scale={w}:{h}:flags=lanczos', '-r', str(fps),
                                '-c:a', 'aac', '-b:a', '128k', '-ar', str(RATE), '-ac', '2', '-shortest',
                                '-movflags', '+faststart', job['out'] + '.part.mp4'], stdin=subprocess.PIPE)
        png = None
        for n in range(n_frames):
            changed = pg.evaluate('t => drawFrame(t)', n / fps)
            if changed or png is None:
                png = pg.screenshot(type='jpeg', quality=95, clip={'x': 0, 'y': 0, 'width': LAYOUTS[job['layout']][0], 'height': LAYOUTS[job['layout']][1]})
            enc.stdin.write(png)
        enc.stdin.close()
        if enc.wait() != 0:
            raise RuntimeError('ffmpeg failed for ' + job['out'])
        b.close()
    os.remove(wav)
    os.replace(job['out'] + '.part.mp4', job['out'])
    return job['out'], round(total, 2), n_frames


def slug(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--layouts', default='desktop,phone')
    ap.add_argument('--only', default='', help='comma-separated lesson ids')
    ap.add_argument('--fps', type=int, default=30)
    ap.add_argument('--crf', type=int, default=20)
    ap.add_argument('--preset', default='medium')
    ap.add_argument('--workers', type=int, default=max(1, (os.cpu_count() or 2) // 2))
    ap.add_argument('--port', type=int, default=8791)
    ap.add_argument('--cache', default='/tmp/b1000-clips')
    ap.add_argument('--fake-audio', action='store_true')
    ap.add_argument('--offline', action='store_true')
    a = ap.parse_args()
    serve(a.port)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b, pg = open_page(pw, 'desktop', a.offline)
        pg.goto(f'http://127.0.0.1:{a.port}/tools/video/frame.html')
        pg.wait_for_function('window.BASIC_FILMS && window.listFilms')
        films = pg.evaluate('listFilms()')
        shots = pg.evaluate('ids => ids.map(id => BASIC_GRAMMAR_DATA.lessons[id].film.map(s => (s.lines || []).length))', [f['id'] for f in films])
        b.close()
    print(f'{len(films)} films, {sum(len(f["lines"]) for f in films)} lines', flush=True)
    clips = fetch_clips(films, a.cache, a.fake_audio)
    print(f'{len(clips)} clips ready', flush=True)
    only = set(x for x in a.only.split(',') if x)
    jobs = []
    for n, (f, counts) in enumerate(zip(films, shots), 1):
        if only and f['id'] not in only:
            continue
        flat = [clips[(norm(l['t']), l['v'])] for l in f['lines']]
        durs, data, i = [], [], 0
        for c in counts:
            durs.append([len(x) / 2 / RATE for x in flat[i:i + c]]); data.append(flat[i:i + c]); i += c
        for layout in a.layouts.split(','):
            os.makedirs(os.path.join(a.out, layout), exist_ok=True)
            jobs.append({'id': f['id'], 'layout': layout, 'number': n, 'count': len(films), 'durs': durs, 'pcm': data,
                         'out': os.path.join(a.out, layout, f'{n:02d}_{slug(f["title"])}.mp4'),
                         'args': {'port': a.port, 'fps': a.fps, 'crf': a.crf, 'preset': a.preset, 'offline': a.offline}})
    t0 = time.time()
    done = 0
    with mp.get_context('spawn').Pool(a.workers) as pool:
        for out, secs, frames in pool.imap_unordered(build_job, jobs):
            done += 1
            print(f'[{done}/{len(jobs)}] {os.path.relpath(out, a.out)}  {secs}s  {frames} frames  ({time.time() - t0:.0f}s)', flush=True)


if __name__ == '__main__':
    main()
