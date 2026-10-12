"""Basic 1000 voice lab: a small HTTP server that runs Qwen3-TTS 1.7B (Alibaba Qwen, Apache-2.0) on a GPU pod.

The RunPod pod downloads this file from GitHub and runs it. It answers on port 8880 straight away
(so its progress can be watched), then installs Qwen3-TTS and loads three models in the background:
CustomVoice (preset speakers), VoiceDesign (a voice from a description) and Base (voice cloning).

Endpoints
  GET  /status       -> {"phase", "ready", "errors", "log": [...last lines], "gpu"}
  GET  /ref/<key>    -> the reference recording (WAV) of a designed voice
  POST /tts          JSON {"engine", "text", ...}   -> audio/mpeg
  POST /tts_batch    JSON {"engine", "texts": [...], ...} -> {"clips": [base64 MP3 or null], "errors": [...]}
       engine "qwen_custom": {"speaker": "Ryan"}                              preset speaker
       engine "qwen_design": {"key", "instruct", "seed", "ref_url"?}          voice made from a description

A voice made from a description is designed once: the VoiceDesign model reads REF_TEXT in that voice
and the recording is kept. Every clip is then cloned from that recording by the Base model, so the
speaker stays the same. The site keeps the recording in its storage and passes it back as "ref_url",
so the same person comes back after the pod restarts (the pod's own disk is wiped when it stops).

Every clip is trimmed of silence and peak-normalised; the site adds its own silence before and after.
"""

import base64
import io
import json
import os
import subprocess
import sys
import threading
import time
import traceback
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8880
HOME = "/workspace" if os.path.isdir("/workspace") else "/tmp"
LOG = os.path.join(HOME, "lab.log")
MODELS = os.path.join(HOME, "models")
REFS = os.path.join(HOME, "refs")
REF_TEXT = "Hello! I am going to read some simple English words and sentences for you, slowly and clearly."
REPOS = {"qwen_custom": "Qwen3-TTS-12Hz-1.7B-CustomVoice", "qwen_design": "Qwen3-TTS-12Hz-1.7B-VoiceDesign",
         "qwen_base": "Qwen3-TTS-12Hz-1.7B-Base"}

STATE = {"phase": "starting", "ready": [], "errors": {}, "started": time.time()}
GPU_LOCK = threading.Lock()
ENGINES = {}
PROMPTS = {}


def log(*parts):
    line = time.strftime("%H:%M:%S ") + " ".join(str(p) for p in parts)
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def sh(cmd):
    log("$", " ".join(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        line = line.rstrip()
        if line and not line.startswith("  Downloading") and "━" not in line:
            log("  ", line[:300])
    if p.wait() != 0:
        raise RuntimeError(f"command failed ({p.returncode}): {' '.join(cmd)}")


# ---------------------------------------------------------------- setup

def setup():
    try:
        os.makedirs(MODELS, exist_ok=True)
        os.makedirs(REFS, exist_ok=True)
        STATE["phase"] = "installing packages"
        # torch is pinned so qwen-tts's unpinned torchaudio cannot pull a different torch
        sh([sys.executable, "-m", "pip", "install", "-q", "--no-cache-dir",
            "torch==2.9.1", "torchaudio==2.9.1", "qwen-tts==0.1.1", "transformers==4.57.3",
            "numpy>=2.0", "soundfile>=0.13", "lameenc", "huggingface_hub"])
        STATE["phase"] = "downloading models"
        from huggingface_hub import snapshot_download
        for repo in REPOS.values():
            snapshot_download("Qwen/" + repo, local_dir=os.path.join(MODELS, repo))
            log("downloaded", repo)
        STATE["phase"] = "loading models"
        for name in REPOS:
            try:
                engine(name)
            except Exception as e:
                STATE["errors"][name] = repr(e)[:500]
                log("FAILED to load", name, traceback.format_exc())
        STATE["phase"] = "ready"
        log("ready:", STATE["ready"], "errors:", list(STATE["errors"]))
    except Exception as e:
        STATE["phase"] = "failed"
        STATE["errors"]["setup"] = repr(e)[:500]
        log("SETUP FAILED", traceback.format_exc())


def engine(name):
    if name in ENGINES:
        return ENGINES[name]
    import torch
    from qwen_tts import Qwen3TTSModel
    t0 = time.time()
    ENGINES[name] = Qwen3TTSModel.from_pretrained(os.path.join(MODELS, REPOS[name]), device_map="cuda:0",
                                                  dtype=torch.bfloat16, attn_implementation="sdpa")
    STATE["ready"].append(name)
    log("loaded", name, f"in {time.time() - t0:.0f}s")
    return ENGINES[name]


def seed_all(seed):
    import random
    import numpy as np
    import torch
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


# ---------------------------------------------------------------- voices

def ref_path(key):
    return os.path.join(REFS, f"qwen_{key}.wav")


def design_ref(req):
    """The reference recording of a designed voice: kept copy, else the site's stored copy, else design it now."""
    import soundfile as sf
    key, path = req["key"], ref_path(req["key"])
    if os.path.exists(path):
        return path
    url = req.get("ref_url")
    if url:
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
            with open(path, "wb") as f:
                f.write(data)
            log("loaded stored reference for", key)
            return path
        except Exception as e:
            log("no stored reference for", key, repr(e)[:120])
    seed_all(int(req.get("seed", 7)))
    wavs, sr = engine("qwen_design").generate_voice_design(text=REF_TEXT, instruct=req["instruct"], language="English")
    sf.write(path, wavs[0], sr)
    log("designed voice", key)
    return path


def synth_many(req, texts):
    """Return ([float32 audio, ...], sample rate) for several texts in one voice, in one GPU batch."""
    seed_all(int(req.get("seed", 7)))
    n = len(texts)
    if req["engine"] == "qwen_custom":
        return engine("qwen_custom").generate_custom_voice(text=texts, speaker=[req["speaker"]] * n,
                                                           language=["English"] * n,
                                                           instruct=[req["instruct"]] * n if req.get("instruct") else None)
    if req["engine"] == "qwen_design":
        key = req["key"]
        if key not in PROMPTS:
            PROMPTS[key] = engine("qwen_base").create_voice_clone_prompt(ref_audio=design_ref(req), ref_text=REF_TEXT)
        return engine("qwen_base").generate_voice_clone(text=texts, language=["English"] * n, voice_clone_prompt=PROMPTS[key])
    raise ValueError("unknown engine " + str(req.get("engine")))


def to_mp3(audio, sr):
    import numpy as np
    try:
        import lameenc
    except ImportError:
        lameenc = None
    a = np.asarray(audio, dtype=np.float32).reshape(-1)
    # trim silence at both ends (the site adds its own fixed silence), keeping 40 ms of margin
    loud = np.flatnonzero(np.abs(a) > 0.02)
    if loud.size:
        m = int(0.04 * sr)
        a = a[max(0, loud[0] - m): loud[-1] + m]
    peak = float(np.max(np.abs(a))) if a.size else 0.0
    if peak > 0:
        a = a * (0.89 / peak)  # about -1 dBFS, so all voices are equally loud
    if lameenc is None:  # libsndfile in soundfile >= 0.13 can write MP3 too
        import soundfile as sf
        buf = io.BytesIO()
        sf.write(buf, a, int(sr), format="MP3")
        return buf.getvalue()
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2").tobytes()
    enc = lameenc.Encoder()
    enc.set_bit_rate(128)
    enc.set_in_sample_rate(int(sr))
    enc.set_channels(1)
    enc.set_quality(2)
    return enc.encode(pcm) + enc.flush()


# ---------------------------------------------------------------- http

def gpu():
    try:
        return subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader"],
                              capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception as e:
        return repr(e)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if not isinstance(body, (bytes, bytearray)):
            body = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("content-type", ctype)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/status") or self.path == "/":
            try:
                with open(LOG) as f:
                    tail = f.read().splitlines()[-60:]
            except FileNotFoundError:
                tail = []
            return self._send(200, {**STATE, "uptime": int(time.time() - STATE["started"]), "log": tail, "gpu": gpu()})
        if self.path.startswith("/ref/"):
            path = ref_path(os.path.basename(self.path[5:]))
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return self._send(200, f.read(), "audio/wav")
        self._send(404, {"error": "not found"})

    def do_POST(self):
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("content-length", "0"))) or b"{}")
            if STATE["phase"] != "ready":
                return self._send(503, {"error": "not ready", "phase": STATE["phase"]})
            who = req.get("key") or req.get("speaker")
            t0 = time.time()
            if self.path.startswith("/tts_batch"):
                texts = [str(t) for t in req.get("texts", [])]
                clips, errors = [None] * len(texts), []
                with GPU_LOCK:
                    try:
                        wavs, sr = synth_many(req, texts)
                        for i, w in enumerate(wavs):
                            clips[i] = base64.b64encode(to_mp3(w, sr)).decode()
                    except Exception as e:  # a failed batch (e.g. out of memory) is retried one clip at a time
                        log("batch failed, retrying one by one:", repr(e)[:200])
                        for i, t in enumerate(texts):
                            try:
                                wavs, sr = synth_many(req, [t])
                                clips[i] = base64.b64encode(to_mp3(wavs[0], sr)).decode()
                            except Exception as e2:
                                errors.append({"text": t, "error": repr(e2)[:300]})
                log("batch", req.get("engine"), who, f"{len(texts)} clips", f"{time.time() - t0:.1f}s")
                return self._send(200, {"clips": clips, "errors": errors})
            if self.path.startswith("/tts"):
                with GPU_LOCK:
                    wavs, sr = synth_many(req, [str(req["text"])])
                log("tts", req.get("engine"), who, repr(req.get("text"))[:60], f"{time.time() - t0:.1f}s")
                return self._send(200, to_mp3(wavs[0], sr), "audio/mpeg")
            self._send(404, {"error": "not found"})
        except Exception as e:
            log("error", traceback.format_exc())
            self._send(500, {"error": repr(e)[:800]})


if __name__ == "__main__":
    log("voice lab starting; python", sys.version.split()[0])
    threading.Thread(target=setup, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
