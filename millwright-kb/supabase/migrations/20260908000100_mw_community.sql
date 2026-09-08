-- Community model: no teacher access code. Anyone signed in can create a group (and is its
-- instructor), publish to the public library directly, and upvote articles. A quiet admin flag
-- (set only by SQL) keeps a moderator able to edit or remove anything.

-- ---------------------------------------------------------------------------
-- 1. Admin flag replaces the teacher role. The role column stays (unused) so old rows are valid.
-- ---------------------------------------------------------------------------
alter table public.mw_profiles add column if not exists is_admin boolean not null default false;

create or replace function public.mw_guard_role_change()
returns trigger language plpgsql set search_path = public as $$
begin
  if (new.is_admin is distinct from old.is_admin or new.role is distinct from old.role)
     and coalesce(current_setting('mw.allow_role_change', true), '') <> 'on' then
    raise exception 'admin flag can only be changed by the database owner';
  end if;
  return new;
end $$;

drop function if exists public.mw_become_teacher(text);
delete from public.mw_settings where key = 'teacher_access_code';

create or replace function public.mw_is_admin()
returns boolean language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.mw_profiles where id = auth.uid() and is_admin);
$$;
grant execute on function public.mw_is_admin() to anon, authenticated;

-- ---------------------------------------------------------------------------
-- 2. Upvotes
-- ---------------------------------------------------------------------------
alter table public.mw_articles add column if not exists upvotes int not null default 0;

create table if not exists public.mw_votes (
  article_id uuid not null references public.mw_articles(id) on delete cascade,
  user_id    uuid not null references public.mw_profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (article_id, user_id)
);
create index if not exists mw_votes_user_idx on public.mw_votes(user_id);
create index if not exists mw_articles_upvotes_idx on public.mw_articles(upvotes desc);

create or replace function public.mw_count_votes()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' then
    update public.mw_articles set upvotes = upvotes + 1 where id = new.article_id;
    return new;
  else
    update public.mw_articles set upvotes = greatest(upvotes - 1, 0) where id = old.article_id;
    return old;
  end if;
end $$;
revoke execute on function public.mw_count_votes() from anon, authenticated, public;

drop trigger if exists mw_votes_count on public.mw_votes;
create trigger mw_votes_count
  after insert or delete on public.mw_votes
  for each row execute function public.mw_count_votes();

alter table public.mw_votes enable row level security;
create policy mw_votes_select on public.mw_votes for select using (true);
create policy mw_votes_insert on public.mw_votes for insert with check (user_id = auth.uid());
create policy mw_votes_delete on public.mw_votes for delete using (user_id = auth.uid());
grant select on public.mw_votes to anon;
grant select, insert, delete on public.mw_votes to authenticated;

-- ---------------------------------------------------------------------------
-- 3. Policies: open publishing, groups for everyone, admin moderation
-- ---------------------------------------------------------------------------
drop policy if exists mw_categories_write on public.mw_categories;
create policy mw_categories_write on public.mw_categories for all
  using (public.mw_is_admin()) with check (public.mw_is_admin());

drop policy if exists mw_groups_insert on public.mw_groups;
create policy mw_groups_insert on public.mw_groups for insert
  with check (teacher_id = auth.uid());

drop policy if exists mw_articles_select on public.mw_articles;
create policy mw_articles_select on public.mw_articles for select using (
  (status = 'published' and group_id is null)
  or author_id = auth.uid()
  or (group_id is not null and public.mw_is_group_member(group_id))
  or public.mw_is_admin()
);
drop policy if exists mw_articles_insert on public.mw_articles;
create policy mw_articles_insert on public.mw_articles for insert with check (
  author_id = auth.uid()
  and status in ('draft','published')
  and (group_id is null or public.mw_is_group_member(group_id))
);
drop policy if exists mw_articles_update on public.mw_articles;
create policy mw_articles_update on public.mw_articles for update
  using (author_id = auth.uid() or public.mw_is_admin())
  with check ((author_id = auth.uid() or public.mw_is_admin()) and status in ('draft','published'));
drop policy if exists mw_articles_delete on public.mw_articles;
create policy mw_articles_delete on public.mw_articles for delete
  using (author_id = auth.uid() or public.mw_is_admin());

drop policy if exists mw_files_delete on public.mw_files;
create policy mw_files_delete on public.mw_files for delete
  using (uploader_id = auth.uid() or public.mw_is_admin());

drop policy if exists mw_storage_delete on storage.objects;
create policy mw_storage_delete on storage.objects for delete to authenticated
  using (bucket_id = 'mw-files' and ((storage.foldername(name))[1] = auth.uid()::text or public.mw_is_admin()));

-- Anything that was waiting for review is simply published now.
update public.mw_articles set status = 'published' where status = 'pending';

drop function if exists public.mw_is_teacher();

-- ---------------------------------------------------------------------------
-- 4. Search returns the vote count
-- ---------------------------------------------------------------------------
drop function if exists public.mw_search(text, text, int);
create or replace function public.mw_search(q text, cat text default null, lim int default 40)
returns table (
  id uuid, slug text, title text, summary text, kind text, tags text[],
  manufacturer text, category_slug text, category_name text, rank real, headline text, upvotes int
) language sql stable set search_path = public as $$
  with query as (select websearch_to_tsquery('english', coalesce(q,'')) as tsq)
  select a.id, a.slug, a.title, a.summary, a.kind, a.tags, a.manufacturer,
         c.slug, c.name,
         (ts_rank_cd(a.search, query.tsq) + similarity(a.title, q) * 0.5)::real as rank,
         ts_headline('english', a.summary || ' ' || left(a.body, 4000), query.tsq,
                     'MaxWords=30, MinWords=12, StartSel=<mark>, StopSel=</mark>'),
         a.upvotes
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
  order by rank desc, a.upvotes desc, a.view_count desc
  limit lim;
$$;
grant execute on function public.mw_search(text, text, int) to anon, authenticated;

-- To make an account a moderator (run as the database owner in the SQL editor):
--   select set_config('mw.allow_role_change', 'on', true);
--   update public.mw_profiles set is_admin = true
--   where id = (select id from auth.users where email = 'owner@example.com');
