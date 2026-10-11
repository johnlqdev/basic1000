-- Public bucket for the course audio clips (made by the "tts" edge function), and the http
-- extension used to call that function from SQL when making clips in bulk.
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('audio', 'audio', true, 2097152, array['audio/mpeg'])
on conflict (id) do nothing;
create extension if not exists http with schema extensions;
