// backup: copies everything that is not code into one Dropbox folder, and a snapshot of the code too.
//
// Admin only (header x-admin-token). POST JSON { action }:
//   check     can we reach Dropbox? -> { ok, folder, entries }
//   audio     copy up to `limit` (default 400) audio files that are new or changed since their last
//             copy -> { copied, failed, pending }. Call again until pending is 0. Every file keeps its
//             path: audio/v2/us_daniel/<hash>.mp3, audio/slow1/..., audio/refs/qwen_daniel.wav
//   database  a dated JSON export of the progress table -> database/progress-<date>.json
//   code      a zip of the GitHub repo at the newest commit on main -> code/basic1000-<date>-<sha>.zip
//   manifest  manifest.json: when each part was last backed up, and how much is in it
//   all       database + code + one audio batch + manifest (the scheduled run)
//   status    how much of the audio is backed up, with no Dropbox call
//
// Dropbox: an app with "App folder" access, so it can only see Apps/<app name>/ in the owner's
// Dropbox. Everything goes under /basic1000-backup inside that folder.
// Secrets (set by the owner in the Supabase dashboard): DROPBOX_APP_KEY, DROPBOX_APP_SECRET,
// DROPBOX_REFRESH_TOKEN. SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are provided by the platform.
// The backup_log table (migration 0003) remembers which storage files are copied already.

const SB = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const DBX_KEY = Deno.env.get("DROPBOX_APP_KEY") ?? "";
const DBX_SECRET = Deno.env.get("DROPBOX_APP_SECRET") ?? "";
const DBX_REFRESH = Deno.env.get("DROPBOX_REFRESH_TOKEN") ?? "";
// sha256 of the admin token (the token itself is kept in the database vault, not in code)
const ADMIN_HASH = "fd386d8929b80a4bcadc5ada75095c854d0efbb50fb431ed975786cd6ad36fc8";
const ROOT = "/basic1000-backup";
const REPO = "johnlqdev/basic1000";
const BUDGET_MS = 120_000; // stop starting new uploads after this long, so a call ends in time

const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });
async function sha256(s: string) {
  const b = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return Array.from(new Uint8Array(b)).map((x) => x.toString(16).padStart(2, "0")).join("");
}
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const today = () => new Date().toISOString().slice(0, 10);

// ---------- Supabase ----------
const sbHeaders = { apikey: SERVICE, authorization: `Bearer ${SERVICE}`, "content-type": "application/json" };
async function rpc(fn: string, args: Record<string, unknown> = {}) {
  const r = await fetch(`${SB}/rest/v1/rpc/${fn}`, { method: "POST", headers: sbHeaders, body: JSON.stringify(args) });
  if (!r.ok) throw new Error(`${fn}: ${r.status} ${await r.text()}`);
  return r.json();
}
async function logCopied(rows: { path: string; size: number; src_updated: string }[]) {
  if (!rows.length) return;
  const r = await fetch(`${SB}/rest/v1/backup_log?on_conflict=path`, {
    method: "POST",
    headers: { ...sbHeaders, prefer: "resolution=merge-duplicates,return=minimal" },
    body: JSON.stringify(rows.map((x) => ({ ...x, backed_up_at: new Date().toISOString() }))),
  });
  if (!r.ok) throw new Error(`backup_log: ${r.status} ${await r.text()}`);
}

// ---------- Dropbox ----------
let token = "";
async function dropboxToken() {
  if (token) return token;
  if (!DBX_KEY || !DBX_SECRET || !DBX_REFRESH) throw new Error("Dropbox secrets are not set (DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN)");
  const r = await fetch("https://api.dropboxapi.com/oauth2/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ grant_type: "refresh_token", refresh_token: DBX_REFRESH, client_id: DBX_KEY, client_secret: DBX_SECRET }),
  });
  if (!r.ok) throw new Error(`Dropbox token: ${r.status} ${await r.text()}`);
  token = (await r.json()).access_token;
  return token;
}
// Dropbox wants the JSON argument header in plain ASCII
const asciiJson = (o: unknown) => JSON.stringify(o).replace(/[\u007f-￿]/g, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
async function upload(path: string, body: Uint8Array) {
  for (let attempt = 0; ; attempt++) {
    const r = await fetch("https://content.dropboxapi.com/2/files/upload", {
      method: "POST",
      headers: {
        authorization: `Bearer ${await dropboxToken()}`,
        "content-type": "application/octet-stream",
        "dropbox-api-arg": asciiJson({ path: ROOT + "/" + path, mode: "overwrite", autorename: false, mute: true }),
      },
      body,
    });
    if (r.ok) { await r.body?.cancel(); return; }
    const text = await r.text();
    // too many writes at once, or a short outage: wait and try again
    if ((r.status === 429 || r.status >= 500) && attempt < 6) {
      const wait = Number(r.headers.get("retry-after") ?? "0") * 1000 || 500 * 2 ** attempt;
      await sleep(Math.min(wait, 15000));
      continue;
    }
    throw new Error(`upload ${path}: ${r.status} ${text.slice(0, 200)}`);
  }
}
async function dropboxList() {
  const r = await fetch("https://api.dropboxapi.com/2/files/list_folder", {
    method: "POST",
    headers: { authorization: `Bearer ${await dropboxToken()}`, "content-type": "application/json" },
    body: JSON.stringify({ path: "", recursive: false }),
  });
  if (!r.ok) throw new Error(`list: ${r.status} ${await r.text()}`);
  return (await r.json()).entries as { name: string }[];
}

// ---------- the parts ----------
async function backupAudio(limit: number, started: number) {
  const todo: { name: string; size: number; updated_at: string }[] = await rpc("backup_pending", { n: limit });
  const done: { path: string; size: number; src_updated: string }[] = [];
  const failed: string[] = [];
  let next = 0;
  const worker = async () => {
    while (next < todo.length && Date.now() - started < BUDGET_MS) {
      const f = todo[next++];
      try {
        const r = await fetch(`${SB}/storage/v1/object/audio/${f.name.split("/").map(encodeURIComponent).join("/")}`, { headers: sbHeaders });
        if (!r.ok) throw new Error(`download ${r.status}`);
        await upload("audio/" + f.name, new Uint8Array(await r.arrayBuffer()));
        done.push({ path: "audio/" + f.name, size: f.size, src_updated: f.updated_at });
        if (done.length % 50 === 0) await logCopied(done.splice(0, done.length).map((x) => x)).catch(() => {});
      } catch (e) {
        failed.push(`${f.name}: ${(e as Error).message}`);
      }
    }
  };
  // a few at a time: Dropbox slows down writes that come too fast into one folder
  await Promise.all([1, 2, 3, 4].map(worker));
  await logCopied(done);
  const [c] = await rpc("backup_counts");
  return { tried: todo.length, failed: failed.slice(0, 10), failures: failed.length, ...c };
}

async function backupDatabase() {
  const r = await fetch(`${SB}/rest/v1/progress?select=*`, { headers: sbHeaders });
  if (!r.ok) throw new Error(`progress: ${r.status} ${await r.text()}`);
  const rows = await r.json();
  const body = new TextEncoder().encode(JSON.stringify({ table: "progress", exported_at: new Date().toISOString(), rows }, null, 1));
  const path = `database/progress-${today()}.json`;
  await upload(path, body);
  return { path, rows: rows.length };
}

async function backupCode() {
  const c = await fetch(`https://api.github.com/repos/${REPO}/commits/main`, { headers: { "user-agent": "basic1000-backup", accept: "application/vnd.github+json" } });
  if (!c.ok) throw new Error(`GitHub commit: ${c.status}`);
  const sha: string = (await c.json()).sha;
  const z = await fetch(`https://codeload.github.com/${REPO}/zip/${sha}`, { headers: { "user-agent": "basic1000-backup" } });
  if (!z.ok) throw new Error(`GitHub zip: ${z.status}`);
  const body = new Uint8Array(await z.arrayBuffer());
  const path = `code/basic1000-${today()}-${sha.slice(0, 7)}.zip`;
  await upload(path, body);
  return { path, sha, bytes: body.length };
}

async function writeManifest(parts: Record<string, unknown>) {
  const [c] = await rpc("backup_counts");
  const manifest = {
    project: "Basic 1000",
    written_at: new Date().toISOString(),
    folder: ROOT,
    audio: { ...c, note: "audio/ mirrors the public 'audio' bucket in Supabase storage, path for path" },
    last_run: parts,
    restore: "Audio: upload audio/* back into the 'audio' bucket at the same paths. Database: insert database/progress-*.json rows into public.progress. Code: the zip is the GitHub repo; secrets are not backed up and live in the Supabase dashboard.",
  };
  await upload("manifest.json", new TextEncoder().encode(JSON.stringify(manifest, null, 1)));
  return manifest;
}

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ error: "POST only" }, 405);
  if ((await sha256(req.headers.get("x-admin-token") ?? "")) !== ADMIN_HASH) return json({ error: "forbidden" }, 403);
  const started = Date.now();
  let body: Record<string, unknown> = {};
  try { body = await req.json(); } catch { /* empty body */ }
  const action = String(body.action ?? "status");
  const limit = Math.max(1, Math.min(2000, Number(body.limit ?? 400)));
  try {
    if (action === "status") return json((await rpc("backup_counts"))[0]);
    if (action === "check") {
      const entries = await dropboxList();
      return json({ ok: true, folder: ROOT, entries: entries.map((e) => e.name) });
    }
    if (action === "audio") return json(await backupAudio(limit, started));
    if (action === "database") return json(await backupDatabase());
    if (action === "code") return json(await backupCode());
    if (action === "manifest") return json(await writeManifest({}));
    if (action === "all") {
      const out: Record<string, unknown> = {};
      for (const [name, fn] of [["database", backupDatabase], ["code", backupCode]] as const) {
        try { out[name] = await fn(); } catch (e) { out[name] = { error: (e as Error).message }; }
      }
      try { out.audio = await backupAudio(limit, started); } catch (e) { out.audio = { error: (e as Error).message }; }
      out.manifest = (await writeManifest(out)).written_at;
      return json(out);
    }
    return json({ error: "unknown action " + action }, 400);
  } catch (e) {
    return json({ error: (e as Error).message }, 500);
  }
});
