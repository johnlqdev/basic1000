"""Basic 1000 voice lab: a small HTTP server for trying large open text-to-speech models on a GPU pod.

The RunPod pod downloads this file from GitHub and runs it. It answers on port 8880 straight away
(so its progress can be watched), then installs the models in the background:

  * Breeze TTS 2   (BreezeBlue, weights for research / non-commercial use)
  * Qwen3-TTS 1.7B (Alibaba Qwen, Apache-2.0): preset speakers, voice design and voice cloning

Endpoints
  GET  /status   -> {"phase", "ready", "errors", "log": [...last lines], "gpu"}
  POST /tts      JSON {"engine", "text", ...} -> audio/mpeg (mono, silence trimmed, peak-normalised)
       engine "qwen_custom": {"speaker": "Ryan"}                 preset Qwen3 speaker
       engine "qwen_design": {"key", "instruct", "seed"}          voice made from a description
       engine "breeze":      {"key", "instruct", "seed"}          voice made from a description

A voice "made from a description" is designed once: the model reads REF_TEXT in that voice, and the
result is kept as a reference recording. Every later sentence is cloned from that recording, so the
same voice is used throughout (designing again for every sentence would give a slightly different
person each time).
"""

import io
import json
import os
import subprocess
import sys
import tarfile
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
BREEZE_SRC = os.path.join(HOME, "breeze-tts-main")
REF_TEXT = "Hello! I am going to read some simple English words and sentences for you, slowly and clearly."

STATE = {"phase": "starting", "ready": [], "errors": {}, "started": time.time()}
GPU_LOCK = threading.Lock()
ENGINES = {}


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

        STATE["phase"] = "downloading Breeze code"
        if not os.path.isdir(BREEZE_SRC):
            url = "https://codeload.github.com/breezeblue-ai/breeze-tts/tar.gz/refs/heads/main"
            data = urllib.request.urlopen(url, timeout=120).read()
            tarfile.open(fileobj=io.BytesIO(data)).extractall(HOME)
        log("breeze code at", BREEZE_SRC, os.listdir(BREEZE_SRC))

        STATE["phase"] = "downloading models"
        from huggingface_hub import snapshot_download
        for repo in ["Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
                     "Qwen/Qwen3-TTS-12Hz-1.7B-Base", "BreezeBlue/Breeze-TTS-2"]:
            path = snapshot_download(repo, local_dir=os.path.join(MODELS, repo.split("/")[1]))
            log("downloaded", repo, "->", path)

        STATE["phase"] = "loading models"
        for name in ["qwen_custom", "qwen_design", "qwen_base", "breeze"]:
            try:
                engine(name)
            except Exception as e:  # keep going: one broken model should not stop the others
                STATE["errors"][name] = repr(e)[:500]
                log("FAILED to load", name, traceback.format_exc())
        STATE["phase"] = "ready"
        log("ready:", STATE["ready"], "errors:", list(STATE["errors"]))
    except Exception as e:
        STATE["phase"] = "failed"
        STATE["errors"]["setup"] = repr(e)[:500]
        log("SETUP FAILED", traceback.format_exc())


# ---------------------------------------------------------------- engines

def engine(name):
    if name in ENGINES:
        return ENGINES[name]
    import torch
    log("loading", name)
    t0 = time.time()
    if name.startswith("qwen_"):
        from qwen_tts import Qwen3TTSModel
        repo = {"qwen_custom": "CustomVoice", "qwen_design": "VoiceDesign", "qwen_base": "Base"}[name]
        m = Qwen3TTSModel.from_pretrained(os.path.join(MODELS, "Qwen3-TTS-12Hz-1.7B-" + repo),
                                          device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa")
        ENGINES[name] = m
    elif name == "breeze":
        sys.path.insert(0, BREEZE_SRC)
        from pathlib import Path
        from breeze_infer.runtime import load_runtime, update_generation_config_for_breeze
        from models.fast_streaming import FastBreezeStreamingRuntime, FastStreamingConfig
        tok, model, audio_tok = load_runtime(Path(MODELS, "Breeze-TTS-2"), device="cuda:0", attn_implementation="eager")
        update_generation_config_for_breeze(model)
        cfg = FastStreamingConfig(max_new_tokens=1500, max_seq_len=2048, fast_all=False, fast_text_encoder=False,
                                  fast_backbone_prefill=False, fast_backbone_decode=False, fast_depth_decoder=False,
                                  fast_codec=False, repetition_penalty=1.1)
        rt = FastBreezeStreamingRuntime(model, audio_tok, cfg, tokenizer=tok)
        ENGINES[name] = (tok, model, audio_tok, rt)
    else:
        raise ValueError("unknown engine " + name)
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


def breeze_say(text, seed, instruct=None, ref=None, cfg_scale=1.0):
    import numpy as np
    from breeze_infer.templates import get_template, prepare_inputs, select_template_name
    tok, model, audio_tok, rt = engine("breeze")
    req = {"id": "r", "text": text, "speaker": "S0"}
    if instruct:
        req["instruction"] = instruct
    if ref:
        req["ref_audio_path"], req["ref_text"] = ref
    seed_all(seed)
    inputs = prepare_inputs(tok, audio_tok, model, [req], get_template(select_template_name(req)),
                            guidance_scale=cfg_scale, guidance_scale_ref=None, guidance_scale_ins=None)
    chunks = [np.asarray(c.audio, dtype=np.float32).reshape(-1) for c in rt.iter_audio_chunks(inputs, request_id="r", seed=seed)]
    return np.concatenate(chunks), rt.sample_rate


def qwen_design_ref(key, instruct, seed):
    import soundfile as sf
    path = os.path.join(REFS, f"qwen_{key}.wav")
    if not os.path.exists(path):
        seed_all(seed)
        wavs, sr = engine("qwen_design").generate_voice_design(text=REF_TEXT, instruct=instruct, language="English")
        sf.write(path, wavs[0], sr)
        log("designed qwen voice", key)
    return path


_qwen_prompts = {}


def synth(req):
    """Return (float32 numpy audio, sample rate) for one request."""
    import soundfile as sf
    eng, text = req["engine"], req["text"]
    seed = int(req.get("seed", 7))
    if eng == "qwen_custom":
        seed_all(seed)
        wavs, sr = engine("qwen_custom").generate_custom_voice(text=text, speaker=req["speaker"], language="English",
                                                               instruct=req.get("instruct") or None)
        return wavs[0], sr
    if eng == "qwen_design":
        key = req["key"]
        if key not in _qwen_prompts:
            ref = qwen_design_ref(key, req["instruct"], seed)
            _qwen_prompts[key] = engine("qwen_base").create_voice_clone_prompt(ref_audio=ref, ref_text=REF_TEXT)
        seed_all(seed)
        wavs, sr = engine("qwen_base").generate_voice_clone(text=text, language="English", voice_clone_prompt=_qwen_prompts[key])
        return wavs[0], sr
    if eng == "breeze":
        path = os.path.join(REFS, f"breeze_{req['key']}.wav")
        if not os.path.exists(path):
            audio, sr = breeze_say(REF_TEXT, seed, instruct=req["instruct"], cfg_scale=4.0)
            sf.write(path, audio, sr)
            log("designed breeze voice", req["key"])
        return breeze_say(text, seed, ref=(path, REF_TEXT))
    raise ValueError("unknown engine " + eng)


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
    pcm = (np.clip(a, -1, 1) * 32767).astype("<i2").tobytes()
    if lameenc is None:  # libsndfile in soundfile >= 0.13 can write MP3 too
        import soundfile as sf
        buf = io.BytesIO()
        sf.write(buf, a, int(sr), format="MP3")
        return buf.getvalue()
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
                    tail = f.read().splitlines()[-int(os.environ.get("LOG_LINES", "60")):]
            except FileNotFoundError:
                tail = []
            return self._send(200, {**STATE, "uptime": int(time.time() - STATE["started"]), "log": tail, "gpu": gpu()})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/tts"):
            return self._send(404, {"error": "not found"})
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("content-length", "0"))) or b"{}")
            if STATE["phase"] != "ready":
                return self._send(503, {"error": "not ready", "phase": STATE["phase"]})
            t0 = time.time()
            with GPU_LOCK:
                audio, sr = synth(req)
            mp3 = to_mp3(audio, sr)
            log("tts", req.get("engine"), req.get("key") or req.get("speaker"), repr(req.get("text"))[:60], f"{time.time() - t0:.1f}s")
            self._send(200, mp3, "audio/mpeg")
        except Exception as e:
            log("tts error", traceback.format_exc())
            self._send(500, {"error": repr(e)[:800]})


if __name__ == "__main__":
    log("voice lab starting; python", sys.version.split()[0])
    threading.Thread(target=setup, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
