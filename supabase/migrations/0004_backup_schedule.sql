-- Scheduled backups to Dropbox (supabase/functions/backup), run by the database itself.
--   weekly  Sunday 03:17 Singapore time (Saturday 19:17 UTC): a snapshot (progress + code zip, newest 5
--           kept), one batch of audio, and the manifest
--   daily   03:37 Singapore time (19:37 UTC): copy any new or changed audio (up to 700 files; nothing
--           to do costs one database query and no Dropbox call)
-- The admin token is read from the vault when each job runs, so it is not stored in the job.
create extension if not exists pg_cron;
create extension if not exists pg_net with schema extensions;

select cron.unschedule(jobname) from cron.job where jobname in ('basic1000-backup-weekly', 'basic1000-backup-audio-daily');

select cron.schedule('basic1000-backup-weekly', '17 19 * * 6', $job$
  select net.http_post(
    url := 'https://duptugctgzemfczbtvgj.supabase.co/functions/v1/backup',
    body := '{"action":"all","limit":700}'::jsonb,
    headers := jsonb_build_object('content-type', 'application/json',
      'x-admin-token', (select decrypted_secret from vault.decrypted_secrets where name = 'tts_admin_token')),
    timeout_milliseconds := 150000);
$job$);

select cron.schedule('basic1000-backup-audio-daily', '37 19 * * *', $job$
  select net.http_post(
    url := 'https://duptugctgzemfczbtvgj.supabase.co/functions/v1/backup',
    body := '{"action":"audio","limit":700}'::jsonb,
    headers := jsonb_build_object('content-type', 'application/json',
      'x-admin-token', (select decrypted_secret from vault.decrypted_secrets where name = 'tts_admin_token')),
    timeout_milliseconds := 150000);
$job$);
