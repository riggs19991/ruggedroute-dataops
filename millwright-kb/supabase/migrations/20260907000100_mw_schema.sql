-- Millwright Knowledge Base — schema
-- All objects are prefixed mw_ so they coexist with other apps in the same Supabase project.

create extension if not exists pg_trgm;

-- ---------------------------------------------------------------------------
-- Profiles (one row per auth user)
-- ---------------------------------------------------------------------------
create table if not exists public.mw_profiles (
  id            uuid primary key references auth.users(id) on delete cascade,
  display_name  text not null default '',
  role          text not null default 'student' check (role in ('student','teacher')),
  school        text not null default '',
  created_at    timestamptz not null default now()
);

-- Auto-create a profile when a user signs up. Metadata comes from signUp({ options: { data } }).
create or replace function public.mw_handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.mw_profiles (id, display_name, school)
  values (
    new.id,
    coalesce(new.raw_user_meta_data->>'display_name', split_part(coalesce(new.email,''), '@', 1)),
    coalesce(new.raw_user_meta_data->>'school', '')
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists mw_on_auth_user_created on auth.users;
create trigger mw_on_auth_user_created
  after insert on auth.users
  for each row execute function public.mw_handle_new_user();

-- Role can only change through mw_become_teacher() (which sets a local flag).
create or replace function public.mw_guard_role_change()
returns trigger language plpgsql as $$
begin
  if new.role is distinct from old.role
     and coalesce(current_setting('mw.allow_role_change', true), '') <> 'on' then
    raise exception 'role can only be changed with a teacher access code';
  end if;
  return new;
end $$;

drop trigger if exists mw_profiles_guard_role on public.mw_profiles;
create trigger mw_profiles_guard_role
  before update on public.mw_profiles
  for each row execute function public.mw_guard_role_change();

-- ---------------------------------------------------------------------------
-- App settings (teacher access code etc.) — readable by nobody via API.
-- ---------------------------------------------------------------------------
create table if not exists public.mw_settings (
  key   text primary key,
  value text not null
);
insert into public.mw_settings (key, value)
values ('teacher_access_code', 'MILLWRIGHT-TEACHER')
on conflict (key) do nothing;

-- ---------------------------------------------------------------------------
-- Categories
-- ---------------------------------------------------------------------------
create table if not exists public.mw_categories (
  id          uuid primary key default gen_random_uuid(),
  slug        text not null unique,
  name        text not null,
  description text not null default '',
  icon        text not null default '',
  sort_order  int  not null default 100
);

-- ---------------------------------------------------------------------------
-- Groups (a teacher's class) — created before articles because articles can be group-scoped
-- ---------------------------------------------------------------------------
create table if not exists public.mw_groups (
  id          uuid primary key default gen_random_uuid(),
  name        text not null,
  school      text not null default '',
  teacher_id  uuid not null references public.mw_profiles(id) on delete cascade,
  join_code   text not null unique,
  term_start  date,
  created_at  timestamptz not null default now()
);

create table if not exists public.mw_group_members (
  group_id   uuid not null references public.mw_groups(id) on delete cascade,
  user_id    uuid not null references public.mw_profiles(id) on delete cascade,
  joined_at  timestamptz not null default now(),
  primary key (group_id, user_id)
);

-- ---------------------------------------------------------------------------
-- Helper predicates (security definer so RLS policies can call them cheaply)
-- ---------------------------------------------------------------------------
create or replace function public.mw_is_teacher()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.mw_profiles where id = auth.uid() and role = 'teacher');
$$;

create or replace function public.mw_is_group_member(gid uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.mw_group_members where group_id = gid and user_id = auth.uid())
      or exists (select 1 from public.mw_groups where id = gid and teacher_id = auth.uid());
$$;

create or replace function public.mw_is_group_teacher(gid uuid)
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.mw_groups where id = gid and teacher_id = auth.uid());
$$;

-- ---------------------------------------------------------------------------
-- Articles — the knowledge base itself
-- ---------------------------------------------------------------------------
-- array_to_string() is only STABLE; generated columns need IMMUTABLE.
create or replace function public.mw_arr_text(a text[])
returns text language sql immutable parallel safe as $$ select array_to_string(a, ' ') $$;

create table if not exists public.mw_articles (
  id             uuid primary key default gen_random_uuid(),
  slug           text not null unique,
  title          text not null,
  summary        text not null default '',
  body           text not null default '',           -- markdown
  kind           text not null default 'procedure'
                 check (kind in ('procedure','reference','chart','manual','tip','safety')),
  category_id    uuid references public.mw_categories(id) on delete set null,
  tags           text[] not null default '{}',
  manufacturer   text not null default '',
  model_numbers  text[] not null default '{}',
  source         text not null default '',           -- where the info came from
  author_id      uuid references public.mw_profiles(id) on delete set null,
  status         text not null default 'pending'
                 check (status in ('draft','pending','published','rejected')),
  review_note    text not null default '',
  reviewed_by    uuid references public.mw_profiles(id) on delete set null,
  group_id       uuid references public.mw_groups(id) on delete cascade, -- null = whole community
  view_count     int  not null default 0,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now(),
  search         tsvector generated always as (
                   setweight(to_tsvector('english', coalesce(title,'')), 'A') ||
                   setweight(to_tsvector('english', public.mw_arr_text(tags)), 'A') ||
                   setweight(to_tsvector('english', coalesce(manufacturer,'') || ' ' || public.mw_arr_text(model_numbers)), 'B') ||
                   setweight(to_tsvector('english', coalesce(summary,'')), 'B') ||
                   setweight(to_tsvector('english', coalesce(body,'')), 'C')
                 ) stored
);

create index if not exists mw_articles_search_idx on public.mw_articles using gin (search);
create index if not exists mw_articles_title_trgm_idx on public.mw_articles using gin (title gin_trgm_ops);
create index if not exists mw_articles_tags_idx on public.mw_articles using gin (tags);
create index if not exists mw_articles_category_idx on public.mw_articles (category_id);
create index if not exists mw_articles_status_idx on public.mw_articles (status);
create index if not exists mw_articles_author_idx on public.mw_articles (author_id);

create or replace function public.mw_touch_updated_at()
returns trigger language plpgsql as $$
begin new.updated_at = now(); return new; end $$;

drop trigger if exists mw_articles_touch on public.mw_articles;
create trigger mw_articles_touch before update on public.mw_articles
  for each row execute function public.mw_touch_updated_at();

-- ---------------------------------------------------------------------------
-- Files (manuals, PDFs, photos) attached to articles or group posts
-- ---------------------------------------------------------------------------
create table if not exists public.mw_group_posts (
  id           uuid primary key default gen_random_uuid(),
  group_id     uuid not null references public.mw_groups(id) on delete cascade,
  week_number  int  not null check (week_number between 1 and 60),
  title        text not null,
  body         text not null default '',   -- markdown
  article_id   uuid references public.mw_articles(id) on delete set null,
  posted_by    uuid references public.mw_profiles(id) on delete set null,
  pinned       boolean not null default false,
  created_at   timestamptz not null default now()
);
create index if not exists mw_group_posts_group_week_idx on public.mw_group_posts (group_id, week_number);

create table if not exists public.mw_files (
  id             uuid primary key default gen_random_uuid(),
  article_id     uuid references public.mw_articles(id) on delete cascade,
  group_post_id  uuid references public.mw_group_posts(id) on delete cascade,
  uploader_id    uuid references public.mw_profiles(id) on delete set null,
  bucket         text not null default 'mw-files',
  path           text not null,
  filename       text not null,
  mime_type      text not null default 'application/octet-stream',
  size_bytes     bigint not null default 0,
  created_at     timestamptz not null default now(),
  check (article_id is not null or group_post_id is not null)
);
create index if not exists mw_files_article_idx on public.mw_files (article_id);
create index if not exists mw_files_post_idx on public.mw_files (group_post_id);

-- ---------------------------------------------------------------------------
-- Bookmarks
-- ---------------------------------------------------------------------------
create table if not exists public.mw_bookmarks (
  user_id     uuid not null references public.mw_profiles(id) on delete cascade,
  article_id  uuid not null references public.mw_articles(id) on delete cascade,
  created_at  timestamptz not null default now(),
  primary key (user_id, article_id)
);

-- ---------------------------------------------------------------------------
-- RPCs
-- ---------------------------------------------------------------------------

-- Full-text search with typo tolerance. Runs as the caller, so RLS decides visibility.
create or replace function public.mw_search(q text, cat text default null, lim int default 40)
returns table (
  id uuid, slug text, title text, summary text, kind text, tags text[],
  manufacturer text, category_slug text, category_name text, rank real, headline text
) language sql stable as $$
  with query as (select websearch_to_tsquery('english', coalesce(q,'')) as tsq)
  select a.id, a.slug, a.title, a.summary, a.kind, a.tags, a.manufacturer,
         c.slug, c.name,
         (ts_rank_cd(a.search, query.tsq) + similarity(a.title, q) * 0.5)::real as rank,
         ts_headline('english', a.summary || ' ' || left(a.body, 4000), query.tsq,
                     'MaxWords=30, MinWords=12, StartSel=<mark>, StopSel=</mark>')
  from public.mw_articles a
  cross join query
  left join public.mw_categories c on c.id = a.category_id
  where (cat is null or c.slug = cat)
    and (
      a.search @@ query.tsq
      or a.title % q
      or exists (select 1 from unnest(a.tags) t where t % q)
      or exists (select 1 from unnest(a.model_numbers) m where lower(m) = lower(q))
    )
  order by rank desc, a.view_count desc
  limit lim;
$$;

-- Increment a view counter without granting UPDATE on articles.
create or replace function public.mw_bump_view(article_slug text)
returns void language sql security definer set search_path = public as $$
  update public.mw_articles set view_count = view_count + 1 where slug = article_slug;
$$;

-- Join a group by code. Returns the group row on success.
create or replace function public.mw_join_group(code text)
returns public.mw_groups language plpgsql security definer set search_path = public as $$
declare g public.mw_groups;
begin
  if auth.uid() is null then raise exception 'sign in first'; end if;
  select * into g from public.mw_groups where upper(join_code) = upper(trim(code));
  if g.id is null then raise exception 'no group with that code'; end if;
  insert into public.mw_group_members (group_id, user_id) values (g.id, auth.uid())
  on conflict do nothing;
  return g;
end $$;

-- Upgrade the current user to teacher with the access code.
create or replace function public.mw_become_teacher(code text)
returns void language plpgsql security definer set search_path = public as $$
declare expected text;
begin
  if auth.uid() is null then raise exception 'sign in first'; end if;
  select value into expected from public.mw_settings where key = 'teacher_access_code';
  if expected is null or upper(trim(code)) <> upper(expected) then
    raise exception 'invalid teacher access code';
  end if;
  perform set_config('mw.allow_role_change', 'on', true);
  update public.mw_profiles set role = 'teacher' where id = auth.uid();
end $$;

-- Random, readable join code for a new group.
create or replace function public.mw_new_join_code()
returns text language sql volatile as $$
  select string_agg(substr('ABCDEFGHJKLMNPQRSTUVWXYZ23456789', (floor(random()*32)+1)::int, 1), '')
  from generate_series(1, 6);
$$;

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
alter table public.mw_profiles      enable row level security;
alter table public.mw_settings      enable row level security;   -- no policies: API cannot read it
alter table public.mw_categories    enable row level security;
alter table public.mw_groups        enable row level security;
alter table public.mw_group_members enable row level security;
alter table public.mw_articles      enable row level security;
alter table public.mw_group_posts   enable row level security;
alter table public.mw_files         enable row level security;
alter table public.mw_bookmarks     enable row level security;

-- profiles: names are public (shown as authors); only you edit yours.
create policy mw_profiles_select on public.mw_profiles for select using (true);
create policy mw_profiles_insert on public.mw_profiles for insert with check (id = auth.uid());
create policy mw_profiles_update on public.mw_profiles for update using (id = auth.uid()) with check (id = auth.uid());

-- categories: everyone reads, teachers manage.
create policy mw_categories_select on public.mw_categories for select using (true);
create policy mw_categories_write  on public.mw_categories for all
  using (public.mw_is_teacher()) with check (public.mw_is_teacher());

-- groups
create policy mw_groups_select on public.mw_groups for select
  using (teacher_id = auth.uid() or public.mw_is_group_member(id));
create policy mw_groups_insert on public.mw_groups for insert
  with check (teacher_id = auth.uid() and public.mw_is_teacher());
create policy mw_groups_update on public.mw_groups for update
  using (teacher_id = auth.uid()) with check (teacher_id = auth.uid());
create policy mw_groups_delete on public.mw_groups for delete using (teacher_id = auth.uid());

-- group members: joining happens through mw_join_group(); leaving/removal here.
create policy mw_members_select on public.mw_group_members for select
  using (user_id = auth.uid() or public.mw_is_group_member(group_id));
create policy mw_members_delete on public.mw_group_members for delete
  using (user_id = auth.uid() or public.mw_is_group_teacher(group_id));

-- articles
create policy mw_articles_select on public.mw_articles for select using (
  (status = 'published' and group_id is null)
  or author_id = auth.uid()
  or (group_id is not null and public.mw_is_group_member(group_id))
  or (group_id is null and public.mw_is_teacher())   -- teachers review pending community posts
);
create policy mw_articles_insert on public.mw_articles for insert with check (
  author_id = auth.uid()
  and (public.mw_is_teacher() or status in ('draft','pending'))
  and (group_id is null or public.mw_is_group_member(group_id))
);
create policy mw_articles_update on public.mw_articles for update
  using (author_id = auth.uid() or public.mw_is_teacher())
  with check (
    (author_id = auth.uid() or public.mw_is_teacher())
    and (public.mw_is_teacher() or status in ('draft','pending'))
  );
create policy mw_articles_delete on public.mw_articles for delete
  using (author_id = auth.uid() or public.mw_is_teacher());

-- group posts (the weekly share feed)
create policy mw_posts_select on public.mw_group_posts for select
  using (public.mw_is_group_member(group_id));
create policy mw_posts_write on public.mw_group_posts for all
  using (public.mw_is_group_teacher(group_id)) with check (public.mw_is_group_teacher(group_id));

-- files: visible when the parent article/post is visible (RLS applies inside the subquery).
create policy mw_files_select on public.mw_files for select using (
  (article_id is not null and exists (select 1 from public.mw_articles a where a.id = article_id))
  or (group_post_id is not null and exists (select 1 from public.mw_group_posts p where p.id = group_post_id))
);
create policy mw_files_insert on public.mw_files for insert with check (uploader_id = auth.uid());
create policy mw_files_delete on public.mw_files for delete
  using (uploader_id = auth.uid() or public.mw_is_teacher());

-- bookmarks
create policy mw_bookmarks_all on public.mw_bookmarks for all
  using (user_id = auth.uid()) with check (user_id = auth.uid());

-- ---------------------------------------------------------------------------
-- Storage bucket for uploads. Object paths are "<uid>/<random>-<filename>".
-- ---------------------------------------------------------------------------
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('mw-files', 'mw-files', false, 52428800, null)
on conflict (id) do nothing;

create policy mw_storage_read on storage.objects for select to authenticated
  using (bucket_id = 'mw-files');
create policy mw_storage_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'mw-files' and (storage.foldername(name))[1] = auth.uid()::text);
create policy mw_storage_delete on storage.objects for delete to authenticated
  using (bucket_id = 'mw-files' and ((storage.foldername(name))[1] = auth.uid()::text or public.mw_is_teacher()));

-- ---------------------------------------------------------------------------
-- Grants (Supabase default roles)
-- ---------------------------------------------------------------------------
grant usage on schema public to anon, authenticated;
grant select on public.mw_profiles, public.mw_categories, public.mw_articles to anon;
grant select on public.mw_files to anon;
grant execute on function public.mw_search(text, text, int) to anon, authenticated;
grant execute on function public.mw_bump_view(text) to anon, authenticated;
grant execute on function public.mw_join_group(text) to authenticated;
grant execute on function public.mw_become_teacher(text) to authenticated;
grant execute on function public.mw_new_join_code() to authenticated;
grant select, insert, update, delete on
  public.mw_profiles, public.mw_categories, public.mw_groups, public.mw_group_members,
  public.mw_articles, public.mw_group_posts, public.mw_files, public.mw_bookmarks
  to authenticated;
revoke all on public.mw_settings from anon, authenticated;
