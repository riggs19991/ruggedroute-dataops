-- Let the founder's own login publish builds (used for preview builds outside CI).
drop policy if exists hq_releases_owner_write on storage.objects;
create policy hq_releases_owner_write on storage.objects for insert to authenticated
  with check (bucket_id = 'hq-releases' and public.hq_is_owner() and name like 'builds/%');
drop policy if exists hq_releases_owner_update on storage.objects;
create policy hq_releases_owner_update on storage.objects for update to authenticated
  using (bucket_id = 'hq-releases' and public.hq_is_owner() and name like 'builds/%')
  with check (bucket_id = 'hq-releases' and public.hq_is_owner() and name like 'builds/%');
drop policy if exists hq_releases_owner_insert_row on public.hq_app_releases;
create policy hq_releases_owner_insert_row on public.hq_app_releases for insert to authenticated
  with check (public.hq_is_owner());
