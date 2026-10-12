"""Basic 1000 voice lab: a small HTTP server that runs Qwen3-TTS 1.7B (Alibaba Qwen, Apache-2.0) on a GPU pod.

The RunPod pod downloads this file from GitHub and runs it. It answers on port 8880 straight away
(so its progress can be watched), then installs Qwen3-TTS and loads three models in the background:
CustomVoice (preset speakers), VoiceDesign (a voice from a description) and Base (voice cloning).

Endpoints
  GET  /status       -> {"phase", "ready", "errors", "log": [...last lines], "gpu"}
  GET  /ref/<key>    -> the reference recording (WAV) of a designed voice
  POST /tts          JSON {"engine", "text", ...}   -> audio/mpeg
  POST /tts_batch    JSON {"engine", "texts": [...], ...} -> {"clips": [base64 MP3 or null], "errors": [...]}
  POST /slow_batch   JSON {"items": [{"url", "text", "kind": "word"|"sentence", "tempo", "ipa"?}]}
                     -> {"results": [{"mp3": base64, "timing": {...}} or {"error"}]}
       Makes the slow version of a stored clip (time-stretched with Rubber Band, pitch kept) and finds
       when each letter (word clips) or each word (sentences) is spoken, with a wav2vec2 CTC model
       (facebook/wav2vec2-large-960h-lv60-self) and forced alignment. "heard" is what a phoneme model
       (facebook/wav2vec2-lv-60-espeak-cv-ft) hears, for checking the IPA shown on the site; given
       "ipa", "match" (0..1) says how well the two agree.
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
ALIGN_REPO = "facebook/wav2vec2-large-960h-lv60-self"  # English letters, CTC
PHONE_REPO = "facebook/wav2vec2-lv-60-espeak-cv-ft"    # IPA phonemes, CTC
LEAD, TAIL = 0.5, 0.4  # seconds of silence before and after a slow clip (same as the site's normal clips)
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
            "numpy>=2.0", "soundfile>=0.13", "lameenc", "huggingface_hub", "audiotsm", "scipy"])
        setup_slow()
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


def setup_slow():
    """ffmpeg with Rubber Band (time stretch) and the two wav2vec2 models; failures here do not stop the voices."""
    STATE["phase"] = "installing ffmpeg"
    try:
        sh(["bash", "-c", "apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ffmpeg > /dev/null"])
    except Exception as e:
        STATE["errors"]["ffmpeg"] = repr(e)[:300]
    STATE["phase"] = "loading aligner"
    try:
        for name, repo in (("align", ALIGN_REPO), ("phone", PHONE_REPO)):
            ctc_model(name, repo)
        STATE["ready"].append("slow")
        log("slow clips ready")
    except Exception as e:
        STATE["errors"]["slow"] = repr(e)[:500]
        log("FAILED to load aligner", traceback.format_exc())


CTC = {}


def ctc_model(name, repo):
    import torch
    from huggingface_hub import hf_hub_download
    from transformers import Wav2Vec2ForCTC
    vocab = json.load(open(hf_hub_download(repo, "vocab.json")))
    if vocab and isinstance(next(iter(vocab.values())), dict):  # some vocab files are keyed by language
        vocab = next(iter(vocab.values()))
    model = Wav2Vec2ForCTC.from_pretrained(repo).to("cuda:0").eval()
    blank = vocab.get("<pad>", 0)
    CTC[name] = (model, vocab, {v: k for k, v in vocab.items()}, blank)
    log("loaded", repo, len(vocab), "tokens")


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


def trim(a, sr):
    """Cut silence at both ends, keeping 40 ms of margin."""
    import numpy as np
    loud = np.flatnonzero(np.abs(a) > 0.02)
    if loud.size:
        m = int(0.04 * sr)
        a = a[max(0, loud[0] - m): loud[-1] + m]
    return a


def to_mp3(audio, sr, trimmed=False):
    import numpy as np
    a = np.asarray(audio, dtype=np.float32).reshape(-1)
    if not trimmed:
        a = trim(a, sr)  # the site adds its own fixed silence
    peak = float(np.max(np.abs(a))) if a.size else 0.0
    if peak > 0:
        a = a * (0.89 / peak)  # about -1 dBFS, so all voices are equally loud
    return encode_mp3(a, sr)


def encode_mp3(a, sr):
    import numpy as np
    try:
        import lameenc
    except ImportError:
        lameenc = None
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


# ---------------------------------------------------------------- slow clips

def read_audio(data):
    """Decode audio bytes (MP3/WAV) to mono float32."""
    import numpy as np
    import soundfile as sf
    try:
        a, sr = sf.read(io.BytesIO(data), dtype="float32")
    except Exception:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src, dst = os.path.join(d, "in.mp3"), os.path.join(d, "out.wav")
            with open(src, "wb") as f:
                f.write(data)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, dst], capture_output=True, check=True)
            a, sr = sf.read(dst, dtype="float32")
    if a.ndim > 1:
        a = a.mean(axis=1)
    return np.ascontiguousarray(a), int(sr)


def stretch(a, sr, tempo):
    """Slow speech down to `tempo` (0.6 = 60 % speed) without changing its pitch."""
    import soundfile as sf
    if abs(tempo - 1) < 1e-3:
        return a
    try:  # Rubber Band, through ffmpeg; soft transient detection suits speech
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            src, dst = os.path.join(d, "in.wav"), os.path.join(d, "out.wav")
            sf.write(src, a, sr, subtype="FLOAT")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                            f"rubberband=tempo={tempo}:transients=mixed:detector=soft:phase=laminar:window=standard:channels=together",
                            "-c:a", "pcm_f32le", dst], capture_output=True, check=True)
            out, _ = sf.read(dst, dtype="float32")
        return out.reshape(-1) if out.ndim == 1 else out.mean(axis=1)
    except Exception as e:
        log("rubberband failed, using WSOLA:", repr(e)[:200])
        import numpy as np
        from audiotsm import wsola
        from audiotsm.io.array import ArrayReader, ArrayWriter
        reader, writer = ArrayReader(a.reshape(1, -1)), ArrayWriter(channels=1)
        wsola(1, speed=tempo).run(reader, writer)
        return np.asarray(writer.data, dtype=np.float32).reshape(-1)


def to16k(a, sr):
    import numpy as np
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(16000, sr)
    return resample_poly(a, 16000 // g, sr // g).astype(np.float32)


def emissions(name, wav16):
    """Log-probabilities per 20 ms frame, shape (frames, tokens)."""
    import torch
    model = CTC[name][0]
    x = torch.from_numpy((wav16 - wav16.mean()) / (wav16.std() + 1e-7)).float()[None].to("cuda:0")
    with torch.inference_mode():
        logits = model(x).logits[0].float()
    return torch.log_softmax(logits, dim=-1).cpu().numpy()


def ctc_align(em, tokens, blank):
    """Viterbi forced alignment of a token sequence to CTC emissions. Returns (first, last+1) frames per token."""
    import numpy as np
    T, L = em.shape[0], len(tokens)
    S = 2 * L + 1
    ext = [blank] * S
    for j, t in enumerate(tokens):
        ext[2 * j + 1] = t
    ext = np.array(ext)
    neg = -1e30
    dp = np.full((T, S), neg, dtype=np.float64)
    bp = np.zeros((T, S), dtype=np.int8)  # 0: stay, 1: from s-1, 2: from s-2
    dp[0, 0] = em[0, ext[0]]
    if S > 1:
        dp[0, 1] = em[0, ext[1]]
    skip = np.zeros(S, dtype=bool)  # s-2 -> s allowed for a letter that differs from the letter before it
    for s_ in range(3, S, 2):
        skip[s_] = ext[s_] != ext[s_ - 2]
    for t in range(1, T):
        prev = dp[t - 1]
        c0 = prev
        c1 = np.concatenate(([neg], prev[:-1]))
        c2 = np.where(skip, np.concatenate(([neg, neg], prev[:-2])), neg)
        stack = np.stack([c0, c1, c2])
        bp[t] = np.argmax(stack, axis=0)
        dp[t] = stack[bp[t], np.arange(S)] + em[t, ext]
    s_ = S - 1 if S == 1 or dp[T - 1, S - 1] >= dp[T - 1, S - 2] else S - 2
    path = [0] * T
    for t in range(T - 1, -1, -1):
        path[t] = s_
        s_ -= int(bp[t, s_])
    spans = [[None, None] for _ in tokens]
    for t, s_ in enumerate(path):
        if s_ % 2 == 1:
            j = s_ // 2
            if spans[j][0] is None:
                spans[j][0] = t
            spans[j][1] = t + 1
    return spans


def heard(wav16):
    """What the phoneme model hears, as IPA (greedy CTC decoding)."""
    em = emissions("phone", wav16)
    _, _, id2tok, blank = CTC["phone"]
    out, last = [], None
    for i in em.argmax(axis=1):
        if i != last and i != blank:
            out.append(id2tok.get(int(i), "?"))
        last = i
    return " ".join(out)


WORD_RE = __import__("re").compile(r"[A-Za-z']+")  # the site splits sentences into words the same way


def ipa_match(heard_ipa, ipa):
    """0..1: how close what the phoneme model heard is to the IPA shown on the site.
    Sounds that the model often mixes up are put together first, so only real differences count
    (for example "live" said /laɪv/ where the site shows /lɪv/)."""
    import re
    def norm(s):
        s = s.replace(" ", "").replace("ˈ", "").replace("ˌ", "").replace("ː", "")
        for a, b in (("eɪ", "A"), ("aɪ", "Y"), ("aʊ", "W"), ("ɔɪ", "O"), ("oʊ", "o"), ("tʃ", "C"), ("dʒ", "J")):
            s = s.replace(a, b)
        table = {"ɪ": "i", "ɛ": "E", "æ": "E", "e": "A", "ɑ": "a", "ɔ": "a", "ə": "@", "ʌ": "@", "ɐ": "@", "ʊ": "u",
                 "ɝ": "R", "ɚ": "R", "ɜ": "R", "ɹ": "r", "ɾ": "t", "ɡ": "g", "ʔ": "", "ɫ": "l", "ᵻ": "i"}
        return "".join(table.get(c, c) for c in s if not c.isdigit() and c not in ".")
    a, b = norm(heard_ipa), norm(ipa)
    if not a or not b:
        return 0.0
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return round(1 - d[len(b)] / max(len(a), len(b)), 2)


def make_slow(it):
    import numpy as np
    text, kind, tempo = str(it["text"]), it.get("kind", "sentence"), float(it.get("tempo", 0.7))
    a, sr = read_audio(urllib.request.urlopen(it["url"], timeout=60).read())
    a = stretch(trim(a, sr), sr, tempo)
    peak = float(np.max(np.abs(a))) if a.size else 0.0
    if peak > 0:
        a = a * (0.89 / peak)
    a = np.concatenate([np.zeros(int(LEAD * sr), np.float32), a.astype(np.float32), np.zeros(int(TAIL * sr), np.float32)])
    mp3 = encode_mp3(a, sr)
    dec, dsr = read_audio(mp3)  # align what the listener will actually hear
    wav16 = to16k(dec, dsr)
    _, vocab, _, blank = CTC["align"]
    em = emissions("align", wav16)
    sec = lambda f: None if f is None else round(f * 0.02, 3)
    if kind == "word":
        letters = [c for c in text if c.isalpha() or c == "'"]
        toks = [vocab.get(c.upper()) for c in letters]
        keep = [j for j, t in enumerate(toks) if t is not None]
        spans = ctc_align(em, [toks[j] for j in keep], blank)
        out = [[None, None] for _ in letters]
        for j, sp in zip(keep, spans):
            out[j] = [sec(sp[0]), sec(sp[1])]
        timing = {"kind": "word", "letters": out}
    else:
        words = WORD_RE.findall(text)
        seq, owner = [], []
        for w_i, w in enumerate(words):
            if w_i and "|" in vocab:
                seq.append(vocab["|"]); owner.append(None)
            for c in w:
                t = vocab.get(c.upper())
                if t is not None:
                    seq.append(t); owner.append(w_i)
        spans = ctc_align(em, seq, blank)
        out = [[None, None] for _ in words]
        for o, sp in zip(owner, spans):
            if o is None or sp[0] is None:
                continue
            if out[o][0] is None:
                out[o][0] = sp[0]
            out[o][1] = sp[1]
        timing = {"kind": "sentence", "words": [[sec(x[0]), sec(x[1])] for x in out]}
    loud = np.flatnonzero(np.abs(dec) > 0.03)  # where the voice starts and stops
    speech = [round(loud[0] / dsr, 3), round(loud[-1] / dsr, 3)] if loud.size else None
    timing.update({"text": text, "tempo": tempo, "dur": round(len(dec) / dsr, 3), "speech": speech, "heard": heard(wav16)})
    if it.get("ipa"):
        timing["match"] = ipa_match(timing["heard"], it["ipa"])
    return {"mp3": base64.b64encode(mp3).decode(), "timing": timing}


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
            if self.path.startswith("/slow_batch"):
                if "slow" not in STATE["ready"]:
                    return self._send(503, {"error": "aligner not ready", "phase": STATE["phase"]})
                t0, results = time.time(), []
                with GPU_LOCK:
                    for it in req.get("items", []):
                        try:
                            results.append(make_slow(it))
                        except Exception as e:
                            log("slow failed", repr(it.get("text")), traceback.format_exc()[-400:])
                            results.append({"error": repr(e)[:300]})
                log("slow batch", len(results), f"{time.time() - t0:.1f}s")
                return self._send(200, {"results": results})
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
