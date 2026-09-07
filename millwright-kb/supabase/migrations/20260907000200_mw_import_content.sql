-- Token-gated content importer so the git-tracked markdown in content/ can be synced
-- to the database with `npm run seed` (no service-role key needed on the client).
-- The token lives in mw_settings (never readable through the API). Rotate with:
--   update public.mw_settings set value = encode(gen_random_bytes(24), 'hex') where key = 'seed_token';

insert into public.mw_settings (key, value)
values ('seed_token', encode(gen_random_bytes(24), 'hex'))
on conflict (key) do nothing;

create or replace function public.mw_import_content(payload jsonb, token text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  expected text;
  c jsonb;
  a jsonb;
  n_cat int := 0;
  n_art int := 0;
begin
  select value into expected from public.mw_settings where key = 'seed_token';
  if expected is null or token is null or token <> expected then
    raise exception 'invalid seed token';
  end if;

  for c in select * from jsonb_array_elements(coalesce(payload->'categories', '[]'::jsonb)) loop
    insert into public.mw_categories (slug, name, description, icon, sort_order)
    values (c->>'slug', c->>'name', coalesce(c->>'description',''), coalesce(c->>'icon',''), coalesce((c->>'sort_order')::int, 100))
    on conflict (slug) do update set
      name = excluded.name, description = excluded.description, icon = excluded.icon, sort_order = excluded.sort_order;
    n_cat := n_cat + 1;
  end loop;

  for a in select * from jsonb_array_elements(coalesce(payload->'articles', '[]'::jsonb)) loop
    insert into public.mw_articles (slug, title, summary, body, kind, category_id, tags, manufacturer, model_numbers, source, status)
    values (
      a->>'slug', a->>'title', coalesce(a->>'summary',''), coalesce(a->>'body',''), coalesce(a->>'kind','procedure'),
      (select id from public.mw_categories where slug = a->>'category'),
      coalesce(array(select jsonb_array_elements_text(a->'tags')), '{}'),
      coalesce(a->>'manufacturer',''),
      coalesce(array(select jsonb_array_elements_text(a->'model_numbers')), '{}'),
      coalesce(a->>'source',''),
      'published')
    on conflict (slug) do update set
      title = excluded.title, summary = excluded.summary, body = excluded.body, kind = excluded.kind,
      category_id = excluded.category_id, tags = excluded.tags, manufacturer = excluded.manufacturer,
      model_numbers = excluded.model_numbers, source = excluded.source, status = 'published';
    n_art := n_art + 1;
  end loop;

  return jsonb_build_object('categories', n_cat, 'articles', n_art);
end $$;

grant execute on function public.mw_import_content(jsonb, text) to anon, authenticated;
