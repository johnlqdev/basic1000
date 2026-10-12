// tts: text to speech for Basic 1000, backed by open voice models running on RunPod pods
// that are switched on only when audio needs to be made.
//
// Public:  GET or POST  ?text=...&voice=woman|man  (optional &voiceId=af_bella, one of CHOICES)
//   -> { url } of an MP3 in the public "audio" bucket. Clips are cached forever by (voice, text),
//      so a sentence is synthesised once. If it is not cached and the voice server is off: 503.
//   Every clip has a short silence before and after it (see pad.ts), so the first word is heard.
// Admin (header x-admin-token): action = status | pods | create | start | stop | delete | batch | head
//   (start/stop/delete/status take "pod": lab | kokoro; default lab)
//
// Voices come from Qwen3-TTS 1.7B (Apache-2.0) on a RunPod GPU pod named basic1000-lab, which runs
// tools/tts-lab/lab_server.py. Some are Qwen's preset speakers; the others are designed from a
// written description once, and their reference recording is kept in storage at refs/qwen_<key>.wav
// so the same person can be brought back whenever the pod is started again.
// (The earlier Kokoro clips are still in storage; the Kokoro pod itself has been removed.)
//
// Secrets: RUNPOD_API_KEY (set by the owner in the Supabase dashboard).
// SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are provided by the platform.

import { padMp3 } from "./pad.ts";

const RP = "https://rest.runpod.io/v1";
const RUNPOD_KEY = Deno.env.get("RUNPOD_API_KEY") ?? "";
const SB = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
// sha256 of the admin token (the token itself is kept in the database vault, not in code)
const ADMIN_HASH = "fd386d8929b80a4bcadc5ada75095c854d0efbb50fb431ed975786cd6ad36fc8";
const PODS: Record<string, { name: string; port: number }> = {
  lab: { name: "basic1000-lab", port: 8880 },
  kokoro: { name: "basic1000-tts", port: 8880 },
};
const BUCKET = "audio";
// the voice used when a request names only "woman" or "man" (until the final two are chosen)
const VOICES: Record<string, string> = { woman: "us_lily", man: "qw_aiden" };
// the older Kokoro trial, kept so its stored clips still resolve
const CHOICES: Record<string, string[]> = {
  woman: ["af_heart", "af_bella", "bf_emma"],
  man: ["am_michael", "am_fenrir", "bm_george"],
};
// Qwen3 voices on trial, all American English. "us_*" voices are designed from these descriptions.
const CLEAR = "speaking clearly at a calm, unhurried pace, with standard American pronunciation";
const design = (key: string, seed: number, who: string) =>
  ({ pod: "lab", req: { engine: "qwen_design", key, seed, instruct: `${who}, ${CLEAR}.` } });
const VOICE_SPECS: Record<string, { pod: string; req?: Record<string, unknown> }> = {
  af_heart: { pod: "kokoro" }, af_bella: { pod: "kokoro" }, bf_emma: { pod: "kokoro" },
  am_michael: { pod: "kokoro" }, am_fenrir: { pod: "kokoro" }, bm_george: { pod: "kokoro" },
  // women
  us_lily: design("lily", 11, "A friendly American woman in her thirties with a clear, warm voice, like a patient English teacher"),
  us_emma: design("emma", 31, "A young American woman in her twenties with a bright, cheerful, lively voice"),
  us_grace: design("grace", 32, "A calm American woman in her fifties with a soft, low, soothing voice"),
  us_olivia: design("olivia", 33, "A confident American woman in her forties with a crisp, polished newsreader voice"),
  us_mia: design("mia", 34, "A gentle young American woman with a light, sweet, soft voice"),
  us_sarah: design("sarah", 35, "A warm American mother in her thirties with a kind, smiling voice, like reading to her children"),
  us_chloe: design("chloe", 36, "An American college student with a natural, relaxed, friendly conversational voice"),
  us_ruth: design("ruth", 37, "A kind American grandmother in her sixties with a warm, slightly husky voice"),
  // men
  qw_ryan: { pod: "lab", req: { engine: "qwen_custom", speaker: "Ryan" } },
  qw_aiden: { pod: "lab", req: { engine: "qwen_custom", speaker: "Aiden" } },
  us_daniel: design("daniel", 41, "A friendly American man in his thirties with a clear, warm voice, like a patient English teacher"),
  us_james: design("james", 42, "A calm American man in his fifties with a deep, rich, steady voice"),
  us_jake: design("jake", 43, "A young American man in his twenties with a bright, friendly, upbeat voice"),
  us_michael: design("michael", 44, "A confident American man in his forties with a crisp, polished newsreader voice"),
  us_ben: design("ben", 45, "A gentle American man in his thirties with a soft-spoken, calm, reassuring voice"),
  us_frank: design("frank", 46, "A kind American grandfather in his sixties with a warm, slightly gravelly voice"),
};
const ALLOWED = new Set(Object.keys(VOICE_SPECS));
const SPEED = 0.92; // a little slower than normal, for learners
const LEAD = 0.5, TAIL = 0.4; // seconds of silence before and after each clip
const VERSION = "v2"; // folder for padded clips; bump it whenever the way clips are made changes

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "content-type, x-admin-token, authorization, apikey, x-client-info",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};
const json = (o: unknown, status = 200) =>
  new Response(JSON.stringify(o), { status, headers: { ...cors, "content-type": "application/json" } });

async function sha256(s: string) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(b)].map((x) => x.toString(16).padStart(2, "0")).join("");
}

async function rp(path: string, init: RequestInit = {}) {
  const r = await fetch(RP + path, {
    ...init,
    headers: { Authorization: `Bearer ${RUNPOD_KEY}`, "content-type": "application/json", ...(init.headers ?? {}) },
  });
  const text = await r.text();
  let body: unknown = text;
  try { body = JSON.parse(text); } catch { /* not json */ }
  return { status: r.status, body };
}

// deno-lint-ignore no-explicit-any
async function findPod(key = "lab"): Promise<any | null> {
  const r = await rp("/pods");
  if (r.status !== 200) throw new Error(`runpod list ${r.status}: ${JSON.stringify(r.body).slice(0, 300)}`);
  // deno-lint-ignore no-explicit-any
  const list: any[] = Array.isArray(r.body) ? r.body : ((r.body as any)?.pods ?? []);
  return list.find((p) => p.name === PODS[key].name) ?? null;
}
const podUrl = (id: string, key = "lab") => `https://${id}-${PODS[key].port}.proxy.runpod.net`;
const norm = (t: string) => t.replace(/\s+/g, " ").trim();
const publicUrl = (path: string) => `${SB}/storage/v1/object/public/${BUCKET}/${path}`;

async function clipPath(voiceId: string, text: string) {
  return `${VERSION}/${voiceId}/${(await sha256(voiceId + "|" + text)).slice(0, 32)}.mp3`;
}
async function cached(path: string) {
  const r = await fetch(publicUrl(path), { method: "HEAD" });
  return r.ok;
}
// the stored reference recording of a designed voice
const refPath = (spec: { req?: Record<string, unknown> }) => `refs/qwen_${spec.req?.key}.wav`;
const labBody = (spec: { req?: Record<string, unknown> }) =>
  spec.req?.engine === "qwen_design" ? { ...spec.req, ref_url: publicUrl(refPath(spec)) } : { ...spec.req };
// after a designed voice is used for the first time, keep its reference recording in storage
async function saveRef(podId: string, spec: { req?: Record<string, unknown> }) {
  if (spec.req?.engine !== "qwen_design" || await cached(refPath(spec))) return;
  const r = await fetch(podUrl(podId, "lab") + "/ref/" + spec.req.key, { signal: AbortSignal.timeout(30000) });
  if (r.ok) await upload(refPath(spec), new Uint8Array(await r.arrayBuffer()), "audio/wav");
}
const fromB64 = (s: string) => Uint8Array.from(atob(s), (c) => c.charCodeAt(0));

async function synth(podId: string, voiceId: string, text: string, speed: number) {
  const spec = VOICE_SPECS[voiceId];
  if (!spec) throw new Error("unknown voice " + voiceId);
  const post = (path: string, body: unknown) => fetch(podUrl(podId, spec.pod) + path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(140000),
  });
  const r = spec.pod === "kokoro"
    ? await post("/v1/audio/speech", { model: "kokoro", voice: voiceId, input: text, response_format: "mp3", speed })
    : await post("/tts", { ...labBody(spec), text });
  if (!r.ok) throw new Error(`${spec.pod} ${r.status}: ${(await r.text()).slice(0, 200)}`);
  return padMp3(new Uint8Array(await r.arrayBuffer()), LEAD, TAIL);
}
async function upload(path: string, bytes: Uint8Array, ctype = "audio/mpeg") {
  const r = await fetch(`${SB}/storage/v1/object/${BUCKET}/${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${SERVICE}`, apikey: SERVICE, "content-type": ctype,
      "x-upsert": "true", "cache-control": "31536000",
    },
    body: bytes,
  });
  if (!r.ok) throw new Error(`upload ${r.status}: ${await r.text()}`);
}

async function speak(text: string, voiceId: string, podId: string | null, speed = SPEED, force = false) {
  const path = await clipPath(voiceId, text);
  if (!force && await cached(path)) return { url: publicUrl(path), cached: true };
  if (!podId) return { error: "voice server is off", status: 503 };
  const bytes = await synth(podId, voiceId, text, speed);
  await upload(path, bytes);
  if (VOICE_SPECS[voiceId]?.pod === "lab") await saveRef(podId, VOICE_SPECS[voiceId]).catch(() => {});
  return { url: publicUrl(path), cached: false, bytes: bytes.length };
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  const url = new URL(req.url);
  // deno-lint-ignore no-explicit-any
  let body: any = {};
  if (req.method === "POST") { try { body = await req.json(); } catch { body = {}; } }
  const q = (k: string) => body[k] ?? url.searchParams.get(k);
  const action = String(q("action") ?? "speak");

  try {
    if (action === "speak") {
      const text = norm(String(q("text") ?? ""));
      const voice = String(q("voice") ?? "woman");
      if (!text || text.length > 300) return json({ error: "text must be 1 to 300 characters" }, 400);
      if (!VOICES[voice]) return json({ error: "voice must be woman or man" }, 400);
      const asked = q("voiceId") ? String(q("voiceId")) : "";
      if (asked && !ALLOWED.has(asked)) return json({ error: "voiceId must be one of " + [...ALLOWED].join(", ") }, 400);
      const voiceId = asked || VOICES[voice];
      const path = await clipPath(voiceId, text);
      if (await cached(path)) return json({ url: publicUrl(path), cached: true });
      const pod = await findPod(VOICE_SPECS[voiceId].pod).catch(() => null);
      if (!pod || pod.desiredStatus !== "RUNNING") return json({ status: "unavailable", message: "voice server is off" }, 503);
      return json(await speak(text, voiceId, pod.id));
    }

    if ((await sha256(req.headers.get("x-admin-token") ?? "")) !== ADMIN_HASH) return json({ error: "forbidden" }, 403);
    if (!RUNPOD_KEY) return json({ error: "RUNPOD_API_KEY secret is not set" }, 500);

    if (action === "pods") return json(await rp("/pods"));
    if (action === "head") {
      // first bytes of a stored clip, as hex, for checking its format
      const r = await fetch(body.url ? String(body.url) : publicUrl(String(body.path)));
      const b = new Uint8Array(await r.arrayBuffer());
      const hex = (a: Uint8Array) => [...a].map((x) => x.toString(16).padStart(2, "0")).join("");
      return json({ status: r.status, size: b.length, head: hex(b.slice(0, Number(body.n ?? 700))) });
    }
    if (action === "create") return json(await rp("/pods", { method: "POST", body: JSON.stringify(body.spec) }));
    const podKey = PODS[String(body.pod ?? "lab")] ? String(body.pod ?? "lab") : "lab";
    if (action === "start" || action === "stop" || action === "delete") {
      const pod = await findPod(podKey);
      if (!pod) return json({ error: "no pod named " + PODS[podKey].name }, 404);
      return json(action === "delete"
        ? await rp(`/pods/${pod.id}`, { method: "DELETE" })
        : await rp(`/pods/${pod.id}/${action}`, { method: "POST" }));
    }
    if (action === "status") {
      const pod = await findPod(podKey);
      if (!pod) return json({ pod: null });
      let server: unknown = null;
      try {
        const r = await fetch(podUrl(pod.id, podKey) + (podKey === "lab" ? "/status" : "/v1/audio/voices"),
          { signal: AbortSignal.timeout(8000) });
        server = r.ok ? { ok: true, body: await r.json() } : { ok: false, status: r.status, text: (await r.text()).slice(0, 300) };
      } catch (e) { server = { ok: false, error: String(e) }; }
      return json({ pod: { id: pod.id, desiredStatus: pod.desiredStatus, costPerHr: pod.costPerHr, image: pod.imageName }, server });
    }
    if (action === "batch") {
      // items: [{ text, voice: 'woman'|'man' } or { text, voiceId }], optional speed, force;
      // body.all = true makes each item in every CHOICES voice of its gender (old Kokoro trial).
      // Qwen voices are made in GPU batches of body.chunk texts (default 12) per voice.
      const podIds: Record<string, string | null> = {};
      const podFor = async (voiceId: string) => {
        const key = VOICE_SPECS[voiceId]?.pod ?? "lab";
        if (!(key in podIds)) {
          const pod = await findPod(key);
          podIds[key] = pod && pod.desiredStatus === "RUNNING" ? pod.id : null;
        }
        return podIds[key];
      };
      const out: Record<string, unknown>[] = [];
      const groups = new Map<string, { text: string; path: string }[]>();
      for (const it of body.items ?? []) {
        const text = norm(String(it.text ?? ""));
        const ids: string[] = it.voiceId ? [it.voiceId] : body.all ? CHOICES[it.voice ?? "woman"] : [VOICES[it.voice ?? "woman"]];
        for (const voiceId of ids) {
          if (!VOICE_SPECS[voiceId]) { out.push({ text, voiceId, error: "unknown voice" }); continue; }
          if (VOICE_SPECS[voiceId].pod !== "lab") {
            try { out.push({ text, voiceId, ...(await speak(text, voiceId, await podFor(voiceId), it.speed ?? SPEED, !!it.force)) }); }
            catch (e) { out.push({ text, voiceId, error: String(e) }); }
            continue;
          }
          const path = await clipPath(voiceId, text);
          if (!it.force && await cached(path)) { out.push({ text, voiceId, url: publicUrl(path), cached: true }); continue; }
          if (!groups.has(voiceId)) groups.set(voiceId, []);
          groups.get(voiceId)!.push({ text, path });
        }
      }
      const size = Math.max(1, Math.min(32, Number(body.chunk ?? 12)));
      for (const [voiceId, list] of groups) {
        const spec = VOICE_SPECS[voiceId], podId = await podFor(voiceId);
        if (!podId) { list.forEach((c) => out.push({ text: c.text, voiceId, error: "voice server is off" })); continue; }
        for (let k = 0; k < list.length; k += size) {
          const chunk = list.slice(k, k + size);
          try {
            const r = await fetch(podUrl(podId, "lab") + "/tts_batch", {
              method: "POST", headers: { "content-type": "application/json" },
              body: JSON.stringify({ ...labBody(spec), texts: chunk.map((c) => c.text) }),
              signal: AbortSignal.timeout(140000),
            });
            if (!r.ok) throw new Error(`lab ${r.status}: ${(await r.text()).slice(0, 200)}`);
            const res = await r.json();
            await Promise.all(chunk.map(async (c, i) => {
              const b64 = res.clips?.[i];
              if (!b64) { out.push({ text: c.text, voiceId, error: "not made" }); return; }
              await upload(c.path, padMp3(fromB64(b64), LEAD, TAIL));
              out.push({ text: c.text, voiceId, url: publicUrl(c.path), cached: false });
            }));
          } catch (e) {
            chunk.forEach((c) => out.push({ text: c.text, voiceId, error: String(e) }));
          }
        }
        await saveRef(podId, spec).catch((e) => out.push({ voiceId, error: "reference not saved: " + String(e) }));
      }
      return json({ results: out });
    }
    return json({ error: "unknown action" }, 400);
  } catch (e) {
    return json({ error: String(e) }, 500);
  }
});
