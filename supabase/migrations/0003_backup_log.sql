-- Backups to Dropbox (supabase/functions/backup): a log of every storage file already copied, so
-- each run only sends files that are new or changed since the last copy.
create table if not exists public.backup_log (
  path text primary key,            -- the path inside the backup folder, e.g. audio/v2/us_daniel/ab12.mp3
  size bigint,
  src_updated timestamptz,          -- when the storage file was last changed, at the time it was copied
  backed_up_at timestamptz not null default now()
);
alter table public.backup_log enable row level security;  -- no policies: only the service role can read or write it

-- storage files in the audio bucket that are not backed up yet, or changed since
create or replace function public.backup_pending(n int)
returns table (name text, size bigint, updated_at timestamptz)
language sql stable security definer set search_path = ''
as $$
  select o.name, (o.metadata->>'size')::bigint, o.updated_at
  from storage.objects o
  left join public.backup_log b on b.path = 'audio/' || o.name
  where o.bucket_id = 'audio' and (b.path is null or b.src_updated < o.updated_at)
  order by o.name
  limit n
$$;

-- how much of the audio bucket is backed up
create or replace function public.backup_counts()
returns table (files bigint, bytes bigint, pending bigint)
language sql stable security definer set search_path = ''
as $$
  select count(*), coalesce(sum((o.metadata->>'size')::bigint), 0),
         count(*) filter (where b.path is null or b.src_updated < o.updated_at)
  from storage.objects o
  left join public.backup_log b on b.path = 'audio/' || o.name
  where o.bucket_id = 'audio'
$$;

revoke all on function public.backup_pending(int) from public, anon, authenticated;
revoke all on function public.backup_counts() from public, anon, authenticated;
grant execute on function public.backup_pending(int) to service_role;
grant execute on function public.backup_counts() to service_role;
