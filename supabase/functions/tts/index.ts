// tts: text to speech for Basic 1000, backed by Kokoro-82M (open source, Apache-2.0)
// running on a RunPod pod that is switched on only when audio needs to be made.
//
// Public:  GET or POST  ?text=...&voice=woman|man  (optional &voiceId=af_bella, one of CHOICES)
//   -> { url } of an MP3 in the public "audio" bucket. Clips are cached forever by (voice, text),
//      so a sentence is synthesised once. If it is not cached and the voice server is off: 503.
//   Every clip has a short silence before and after it (see pad.ts), so the first word is heard.
// Admin (header x-admin-token): action = status | pods | create | start | stop | delete | batch
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
const POD_NAME = "basic1000-tts";
const PORT = 8880;
const BUCKET = "audio";
// the course's two voices; change a Kokoro voice here and new clips use it (old ones stay cached under the old id)
const VOICES: Record<string, string> = { woman: "af_heart", man: "am_michael" };
// voices on trial: the site shows one button per voice so the owner can pick the nicest
const CHOICES: Record<string, string[]> = {
  woman: ["af_heart", "af_bella", "bf_emma"],
  man: ["am_michael", "am_fenrir", "bm_george"],
};
const ALLOWED = new Set(Object.values(CHOICES).flat());
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
async function findPod(): Promise<any | null> {
  const r = await rp("/pods");
  if (r.status !== 200) throw new Error(`runpod list ${r.status}: ${JSON.stringify(r.body).slice(0, 300)}`);
  // deno-lint-ignore no-explicit-any
  const list: any[] = Array.isArray(r.body) ? r.body : ((r.body as any)?.pods ?? []);
  return list.find((p) => p.name === POD_NAME) ?? null;
}
const podUrl = (id: string) => `https://${id}-${PORT}.proxy.runpod.net`;
const norm = (t: string) => t.replace(/\s+/g, " ").trim();
const publicUrl = (path: string) => `${SB}/storage/v1/object/public/${BUCKET}/${path}`;

async function clipPath(voiceId: string, text: string) {
  return `${VERSION}/${voiceId}/${(await sha256(voiceId + "|" + text)).slice(0, 32)}.mp3`;
}
async function cached(path: string) {
  const r = await fetch(publicUrl(path), { method: "HEAD" });
  return r.ok;
}
async function synth(podId: string, voiceId: string, text: string, speed: number) {
  const r = await fetch(podUrl(podId) + "/v1/audio/speech", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ model: "kokoro", voice: voiceId, input: text, response_format: "mp3", speed }),
  });
  if (!r.ok) throw new Error(`kokoro ${r.status}: ${(await r.text()).slice(0, 200)}`);
  return padMp3(new Uint8Array(await r.arrayBuffer()), LEAD, TAIL);
}
async function upload(path: string, bytes: Uint8Array) {
  const r = await fetch(`${SB}/storage/v1/object/${BUCKET}/${path}`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${SERVICE}`, apikey: SERVICE, "content-type": "audio/mpeg",
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
      const pod = await findPod().catch(() => null);
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
    if (action === "start" || action === "stop" || action === "delete") {
      const pod = await findPod();
      if (!pod) return json({ error: "no pod named " + POD_NAME }, 404);
      return json(action === "delete"
        ? await rp(`/pods/${pod.id}`, { method: "DELETE" })
        : await rp(`/pods/${pod.id}/${action}`, { method: "POST" }));
    }
    if (action === "status") {
      const pod = await findPod();
      if (!pod) return json({ pod: null });
      let server: unknown = null;
      try {
        const r = await fetch(podUrl(pod.id) + "/v1/audio/voices", { signal: AbortSignal.timeout(8000) });
        server = r.ok ? { ok: true, voices: ((await r.json())?.voices ?? []).length } : { ok: false, status: r.status };
      } catch (e) { server = { ok: false, error: String(e) }; }
      return json({ pod: { id: pod.id, desiredStatus: pod.desiredStatus, costPerHr: pod.costPerHr, image: pod.imageName }, server });
    }
    if (action === "batch") {
      // items: [{ text, voice: 'woman'|'man' } or { text, voiceId: 'af_bella' }], optional speed, force;
      // body.all = true makes each item in every CHOICES voice of its gender
      const pod = await findPod();
      const podId = pod && pod.desiredStatus === "RUNNING" ? pod.id : null;
      const out = [];
      for (const it of body.items ?? []) {
        const text = norm(String(it.text ?? ""));
        const ids: string[] = it.voiceId ? [it.voiceId] : body.all ? CHOICES[it.voice ?? "woman"] : [VOICES[it.voice ?? "woman"]];
        for (const voiceId of ids) {
          try { out.push({ text, voiceId, ...(await speak(text, voiceId, podId, it.speed ?? SPEED, !!it.force)) }); }
          catch (e) { out.push({ text, voiceId, error: String(e) }); }
        }
      }
      return json({ results: out });
    }
    return json({ error: "unknown action" }, 400);
  } catch (e) {
    return json({ error: String(e) }, 500);
  }
});
