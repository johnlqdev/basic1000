// backup: copies everything that is not code into one Dropbox folder, and a snapshot of the code too.
//
// Layout in Dropbox (under /basic1000-backup in the app's folder):
//   audio/                one mirror of the 'audio' storage bucket, path for path. Files are added or
//                         updated, never duplicated, so it costs the bucket's size once.
//   snapshots/<date>/     progress.json (the progress table) and basic1000-<commit>.zip (the GitHub repo).
//                         Only the newest KEEP (5) snapshots are kept; older ones are deleted.
//   manifest.json         what is there, when it was written, and how to restore.
//
// Admin only (header x-admin-token). POST JSON { action }:
//   check     can we reach Dropbox? -> { ok, folder, entries }
//   audio     copy up to `limit` (default 400, at most 1000) audio files that are new or changed since
//             their last copy -> { copied, failed, pending }. Call again until pending is 0.
//   snapshot  today's snapshot folder, then delete all but the newest KEEP snapshots
//   manifest  rewrite manifest.json
//   all       snapshot + one audio batch + manifest (the weekly scheduled run)
//   status    how much of the audio is backed up, with no Dropbox call
// Scheduled in the database with pg_cron (migration 0004): weekly "all", daily "audio".
//
// Dropbox: the app's folder is the only place the function can see. Secrets (set by the owner in the
// Supabase dashboard): DROPBOX_APP_KEY, DROPBOX_APP_SECRET, DROPBOX_REFRESH_TOKEN. SUPABASE_URL and
// SUPABASE_SERVICE_ROLE_KEY are provided by the platform. The backup_log table (migration 0003)
// remembers which storage files are copied already.

const SB = Deno.env.get("SUPABASE_URL") ?? "";
const SERVICE = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const DBX_KEY = Deno.env.get("DROPBOX_APP_KEY") ?? "";
const DBX_SECRET = Deno.env.get("DROPBOX_APP_SECRET") ?? "";
const DBX_REFRESH = Deno.env.get("DROPBOX_REFRESH_TOKEN") ?? "";
// sha256 of the admin token (the token itself is kept in the database vault, not in code)
const ADMIN_HASH = "fd386d8929b80a4bcadc5ada75095c854d0efbb50fb431ed975786cd6ad36fc8";
const ROOT = "/basic1000-backup";
const REPO = "johnlqdev/basic1000";
const KEEP = 5; // snapshots to keep
const BUDGET_MS = 90_000; // stop starting new uploads after this long, so a call ends in time

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
const asciiJson = (o: unknown) => JSON.stringify(o).replace(/[\u007f-\uffff]/g, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"));
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
async function dropboxApi(endpoint: string, args: unknown) {
  const r = await fetch("https://api.dropboxapi.com/2/files/" + endpoint, {
    method: "POST",
    headers: { authorization: `Bearer ${await dropboxToken()}`, "content-type": "application/json" },
    body: JSON.stringify(args),
  });
  const text = await r.text();
  return { ok: r.ok, status: r.status, body: text ? JSON.parse(text) : null, text };
}
// the names in one folder ("" is the app folder itself); a folder that is not there yet is empty
async function dropboxList(path = "") {
  const r = await dropboxApi("list_folder", { path, recursive: false });
  if (r.status === 409 && r.text.includes("not_found")) return [];
  if (!r.ok) throw new Error(`list ${path}: ${r.status} ${r.text.slice(0, 200)}`);
  return r.body.entries as { name: string; ".tag": string }[];
}
async function dropboxDelete(path: string) {
  const r = await dropboxApi("delete_v2", { path });
  if (r.ok || (r.status === 409 && r.text.includes("not_found"))) return r.ok;
  throw new Error(`delete ${path}: ${r.status} ${r.text.slice(0, 200)}`);
}

// ---------- the parts ----------
// Many small files: each is sent as its own upload session (no folder lock, so many at once), then
// they are all committed together with finish_batch_v2, which takes the folder lock only once.
async function startSession(body: Uint8Array) {
  for (let attempt = 0; ; attempt++) {
    const r = await fetch("https://content.dropboxapi.com/2/files/upload_session/start", {
      method: "POST",
      headers: { authorization: `Bearer ${await dropboxToken()}`, "content-type": "application/octet-stream", "dropbox-api-arg": asciiJson({ close: true }) },
      body,
    });
    if (r.ok) return (await r.json()).session_id as string;
    const text = await r.text();
    if ((r.status === 429 || r.status >= 500) && attempt < 5) { await sleep(Number(r.headers.get("retry-after") ?? "0") * 1000 || 400 * 2 ** attempt); continue; }
    throw new Error(`session ${r.status} ${text.slice(0, 150)}`);
  }
}
async function finishBatch(entries: { session: string; size: number; path: string }[]) {
  for (let attempt = 0; ; attempt++) {
    const r = await fetch("https://api.dropboxapi.com/2/files/upload_session/finish_batch_v2", {
      method: "POST",
      headers: { authorization: `Bearer ${await dropboxToken()}`, "content-type": "application/json" },
      body: JSON.stringify({ entries: entries.map((e) => ({
        cursor: { session_id: e.session, offset: e.size },
        commit: { path: ROOT + "/" + e.path, mode: "overwrite", autorename: false, mute: true },
      })) }),
    });
    if (r.ok) return ((await r.json()).entries as { ".tag": string }[]).map((x) => x[".tag"] === "success");
    const text = await r.text();
    if ((r.status === 429 || r.status >= 500) && attempt < 5) { await sleep(Number(r.headers.get("retry-after") ?? "0") * 1000 || 1000 * 2 ** attempt); continue; }
    throw new Error(`finish_batch ${r.status} ${text.slice(0, 200)}`);
  }
}
async function backupAudio(limit: number, started: number) {
  const todo: { name: string; size: number; updated_at: string }[] = await rpc("backup_pending", { n: Math.min(limit, 1000) });
  const sent: { session: string; size: number; path: string; src_updated: string }[] = [];
  const failed: string[] = [];
  let next = 0;
  const worker = async () => {
    while (next < todo.length && Date.now() - started < BUDGET_MS) {
      const f = todo[next++];
      try {
        const r = await fetch(`${SB}/storage/v1/object/audio/${f.name.split("/").map(encodeURIComponent).join("/")}`, { headers: sbHeaders });
        if (!r.ok) throw new Error(`download ${r.status}`);
        const body = new Uint8Array(await r.arrayBuffer());
        sent.push({ session: await startSession(body), size: body.length, path: "audio/" + f.name, src_updated: f.updated_at });
      } catch (e) {
        failed.push(`${f.name}: ${(e as Error).message}`);
      }
    }
  };
  await Promise.all(Array.from({ length: 10 }, worker));
  let copied = 0;
  if (sent.length) {
    const ok = await finishBatch(sent);
    const rows = sent.filter((_, i) => ok[i]).map((x) => ({ path: x.path, size: x.size, src_updated: x.src_updated }));
    sent.forEach((x, i) => { if (!ok[i]) failed.push(`${x.path}: commit failed`); });
    for (let i = 0; i < rows.length; i += 500) await logCopied(rows.slice(i, i + 500));
    copied = rows.length;
  }
  const [c] = await rpc("backup_counts");
  return { copied, failed: failed.slice(0, 10), failures: failed.length, ...c };
}

async function snapshot() {
  const date = today(), dir = `snapshots/${date}`;
  // the progress table
  const r = await fetch(`${SB}/rest/v1/progress?select=*`, { headers: sbHeaders });
  if (!r.ok) throw new Error(`progress: ${r.status} ${await r.text()}`);
  const rows = await r.json();
  await upload(`${dir}/progress.json`, new TextEncoder().encode(JSON.stringify({ table: "progress", exported_at: new Date().toISOString(), rows }, null, 1)));
  // the code, at the newest commit on main
  const c = await fetch(`https://api.github.com/repos/${REPO}/commits/main`, { headers: { "user-agent": "basic1000-backup", accept: "application/vnd.github+json" } });
  if (!c.ok) throw new Error(`GitHub commit: ${c.status}`);
  const sha: string = (await c.json()).sha;
  const z = await fetch(`https://codeload.github.com/${REPO}/zip/${sha}`, { headers: { "user-agent": "basic1000-backup" } });
  if (!z.ok) throw new Error(`GitHub zip: ${z.status}`);
  const zip = new Uint8Array(await z.arrayBuffer());
  await upload(`${dir}/basic1000-${sha.slice(0, 7)}.zip`, zip);
  // keep the newest KEEP snapshots (folder names are dates, so they sort in time order)
  const all = (await dropboxList(ROOT + "/snapshots")).filter((e) => e[".tag"] === "folder").map((e) => e.name).sort().reverse();
  const removed: string[] = [];
  for (const old of all.slice(KEEP)) { await dropboxDelete(`${ROOT}/snapshots/${old}`); removed.push(old); }
  // the first version wrote database/ and code/ at the top; those now live in snapshots/
  for (const legacy of ["database", "code"]) if (await dropboxDelete(`${ROOT}/${legacy}`)) removed.push(legacy);
  return { folder: dir, rows: rows.length, commit: sha, zip_bytes: zip.length, kept: all.slice(0, KEEP), removed };
}

async function writeManifest(parts: Record<string, unknown>) {
  const [c] = await rpc("backup_counts");
  const manifest = {
    project: "Basic 1000",
    written_at: new Date().toISOString(),
    folder: ROOT,
    audio: { ...c, note: "audio/ mirrors the public 'audio' bucket in Supabase storage, path for path (one copy, kept up to date)" },
    snapshots: { keep: KEEP, folders: (await dropboxList(ROOT + "/snapshots")).map((e) => e.name).sort().reverse() },
    last_run: parts,
    restore: "Audio: upload audio/* back into the 'audio' bucket at the same paths. Progress: insert snapshots/<date>/progress.json rows into public.progress. Code: snapshots/<date>/basic1000-<commit>.zip is the GitHub repo at that commit. Secrets are not backed up; they live in the Supabase dashboard.",
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
      const entries = await dropboxList(ROOT);
      return json({ ok: true, folder: ROOT, entries: entries.map((e) => e.name) });
    }
    if (action === "audio") return json(await backupAudio(limit, started));
    if (action === "snapshot") return json(await snapshot());
    if (action === "manifest") return json(await writeManifest({}));
    if (action === "all") {
      const out: Record<string, unknown> = {};
      try { out.snapshot = await snapshot(); } catch (e) { out.snapshot = { error: (e as Error).message }; }
      try { out.audio = await backupAudio(limit, started); } catch (e) { out.audio = { error: (e as Error).message }; }
      out.manifest = (await writeManifest(out)).written_at;
      return json(out);
    }
    return json({ error: "unknown action " + action }, 400);
  } catch (e) {
    return json({ error: (e as Error).message }, 500);
  }
});
