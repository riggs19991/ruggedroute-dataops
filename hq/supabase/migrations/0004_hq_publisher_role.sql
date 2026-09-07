-- A publisher login may upload builds and record releases, nothing else.
-- The publisher auth user itself is created out-of-band (auth.users), never via migration.
create table if not exists public.hq_publisher_emails (
  email text primary key,
  added_at timestamptz not null default now()
);
alter table public.hq_publisher_emails enable row level security;
insert into public.hq_publisher_emails (email) values ('publisher@ruggedroutehq.com') on conflict do nothing;

create or replace function public.hq_is_publisher() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(
    (select true from public.hq_publisher_emails p
      where lower(p.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
      limit 1),
    false);
$$;
revoke all on function public.hq_is_publisher() from public;
grant execute on function public.hq_is_publisher() to authenticated;

drop policy if exists hq_releases_owner_write on storage.objects;
create policy hq_releases_owner_write on storage.objects for insert to authenticated
  with check (bucket_id = 'hq-releases' and (public.hq_is_owner() or public.hq_is_publisher()) and name like 'builds/%');
drop policy if exists hq_releases_owner_update on storage.objects;
create policy hq_releases_owner_update on storage.objects for update to authenticated
  using (bucket_id = 'hq-releases' and (public.hq_is_owner() or public.hq_is_publisher()) and name like 'builds/%')
  with check (bucket_id = 'hq-releases' and (public.hq_is_owner() or public.hq_is_publisher()) and name like 'builds/%');
drop policy if exists hq_releases_owner_read on storage.objects;
create policy hq_releases_owner_read on storage.objects for select to authenticated
  using (bucket_id = 'hq-releases' and (public.hq_is_owner() or public.hq_is_publisher()) and name like 'builds/%');
drop policy if exists hq_releases_owner_insert_row on public.hq_app_releases;
create policy hq_releases_owner_insert_row on public.hq_app_releases for insert to authenticated
  with check (public.hq_is_owner() or public.hq_is_publisher());
drop policy if exists hq_releases_read on public.hq_app_releases;
create policy hq_releases_read on public.hq_app_releases for select to authenticated
  using (public.hq_is_owner() or public.hq_is_publisher());
