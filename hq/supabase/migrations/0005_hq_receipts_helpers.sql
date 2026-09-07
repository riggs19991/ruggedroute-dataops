-- Receipts helpers: vendor normalization/matching, duplicate detection, vendor rules,
-- and owner-managed secrets (the Anthropic API key lives in Vault, never in a table).
-- (Applied 2026-09-07; body identical to the live migration hq_receipts_helpers.)

create or replace function public.hq_normalize_vendor(p text) returns text
language sql immutable as $$
  select nullif(trim(regexp_replace(regexp_replace(regexp_replace(lower(coalesce(p,'')),
    '\b(inc|llc|ltd|corp|co|store|#\s*\d+|\d{3,})\b', ' ', 'g'),
    '[^a-z0-9 ]+', ' ', 'g'), '\s+', ' ', 'g')), '');
$$;

create or replace function public.hq_match_vendor(p_name text)
returns table (vendor_id uuid, name text, default_category_id uuid, matched_by text)
language sql stable security invoker set search_path = public as $$
  with norm as (select public.hq_normalize_vendor(p_name) n)
  select v.id, v.name, v.default_category_id, 'alias'
    from public.hq_vendor_aliases a join public.hq_vendors v on v.id = a.vendor_id, norm
   where v.owner = auth.uid() and lower(coalesce(p_name,'')) like lower(a.alias_pattern)
  union all
  select v.id, v.name, v.default_category_id, 'exact'
    from public.hq_vendors v, norm where v.owner = auth.uid() and v.normalized_name = norm.n
  union all
  select v.id, v.name, v.default_category_id, 'prefix'
    from public.hq_vendors v, norm
   where v.owner = auth.uid() and norm.n is not null and length(norm.n) >= 4
     and (v.normalized_name like norm.n || '%' or norm.n like v.normalized_name || '%')
  limit 1;
$$;
grant execute on function public.hq_match_vendor(text) to authenticated;

create or replace function public.hq_upsert_vendor(p_name text) returns uuid
language plpgsql security invoker set search_path = public as $$
declare v_id uuid; v_norm text := public.hq_normalize_vendor(p_name);
begin
  if v_norm is null then return null; end if;
  select vendor_id into v_id from public.hq_match_vendor(p_name);
  if v_id is null then
    insert into public.hq_vendors (owner, name, normalized_name) values (auth.uid(), trim(p_name), v_norm)
    on conflict (owner, normalized_name) do update set name = excluded.name
    returning id into v_id;
  end if;
  return v_id;
end $$;
grant execute on function public.hq_upsert_vendor(text) to authenticated;

create or replace function public.hq_receipt_duplicates(p_receipt_id uuid)
returns table (id uuid, date date, total numeric, vendor_name text, reason text)
language sql stable security invoker set search_path = public as $$
  with me as (
    select r.*, f.sha256 as my_sha from public.hq_receipts r
      left join public.hq_files f on f.id = r.file_id
     where r.id = p_receipt_id and r.owner = auth.uid())
  select r.id, r.date, r.total, v.name,
         case when f.sha256 is not null and f.sha256 = me.my_sha then 'identical file'
              else 'same vendor and total within 5 days' end
    from public.hq_receipts r
    left join public.hq_files f on f.id = r.file_id
    left join public.hq_vendors v on v.id = r.vendor_id, me
   where r.owner = auth.uid() and r.id <> me.id and r.deleted_at is null and r.status <> 'void'
     and ((f.sha256 is not null and f.sha256 = me.my_sha)
       or (r.vendor_id is not null and r.vendor_id = me.vendor_id and r.total = me.total
           and r.date is not null and me.date is not null and abs(r.date - me.date) <= 5))
   order by r.date desc limit 10;
$$;
grant execute on function public.hq_receipt_duplicates(uuid) to authenticated;

create or replace function public.hq_apply_vendor_rule(p_vendor_id uuid, p_category_id uuid, p_receipt_id uuid default null)
returns void language plpgsql security invoker set search_path = public as $$
begin
  update public.hq_vendors set default_category_id = p_category_id where id = p_vendor_id and owner = auth.uid();
  insert into public.hq_vendor_rules (owner, vendor_id, category_id, created_from_receipt_id)
  values (auth.uid(), p_vendor_id, p_category_id, p_receipt_id);
end $$;
grant execute on function public.hq_apply_vendor_rule(uuid, uuid, uuid) to authenticated;

create or replace function public.hq_set_secret(p_key text, p_value text) returns void
language plpgsql security definer set search_path = public, vault as $$
declare v_id uuid; v_name text;
begin
  if not public.hq_is_owner() then raise exception 'not allowed'; end if;
  v_name := 'hq_' || p_key || '_' || auth.uid()::text;
  select (value->>'vault_id')::uuid into v_id from public.hq_settings where owner = auth.uid() and key = 'secret:' || p_key;
  if v_id is not null then
    perform vault.update_secret(v_id, p_value, v_name, 'RuggedRoute HQ secret ' || p_key);
  else
    v_id := vault.create_secret(p_value, v_name, 'RuggedRoute HQ secret ' || p_key);
    insert into public.hq_settings (owner, key, value) values (auth.uid(), 'secret:' || p_key, jsonb_build_object('vault_id', v_id))
    on conflict (owner, key) do update set value = excluded.value, updated_at = now();
  end if;
end $$;
revoke all on function public.hq_set_secret(text, text) from public;
grant execute on function public.hq_set_secret(text, text) to authenticated;

create or replace function public.hq_has_secret(p_key text) returns boolean
language sql stable security invoker set search_path = public as $$
  select exists (select 1 from public.hq_settings where owner = auth.uid() and key = 'secret:' || p_key);
$$;
grant execute on function public.hq_has_secret(text) to authenticated;

create or replace function public.hq_read_secret(p_owner uuid, p_key text) returns text
language plpgsql security definer set search_path = public, vault as $$
declare v_id uuid; v_secret text;
begin
  if current_setting('request.jwt.claim.role', true) is distinct from 'service_role'
     and coalesce(auth.jwt() ->> 'role', '') <> 'service_role' then
    raise exception 'not allowed';
  end if;
  select (value->>'vault_id')::uuid into v_id from public.hq_settings where owner = p_owner and key = 'secret:' || p_key;
  if v_id is null then return null; end if;
  select decrypted_secret into v_secret from vault.decrypted_secrets where id = v_id;
  return v_secret;
end $$;
revoke all on function public.hq_read_secret(uuid, text) from public;
grant execute on function public.hq_read_secret(uuid, text) to service_role;
