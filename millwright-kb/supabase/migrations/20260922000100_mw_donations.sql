-- Supporters wall: verified donations recorded by the Cloudflare Worker after Stripe Checkout,
-- with the display choice the donor makes afterwards (anonymous, name, business or profile name).
-- Writes only go through token-gated definer functions (same pattern as mw_import_content);
-- the token lives in mw_settings, which the API cannot read. Rotate with:
--   update public.mw_settings set value = encode(gen_random_bytes(24), 'hex') where key = 'donation_token';

insert into public.mw_settings (key, value)
values ('donation_token', encode(gen_random_bytes(24), 'hex'))
on conflict (key) do nothing;

create table if not exists public.mw_donations (
  id uuid primary key default gen_random_uuid(),
  stripe_session_id text not null unique,
  amount_cents integer not null check (amount_cents > 0),
  currency text not null default 'usd',
  display_mode text not null default 'anonymous' check (display_mode in ('anonymous', 'name', 'business', 'profile')),
  display_name text not null default '',
  hidden boolean not null default false,
  created_at timestamptz not null default now(),
  display_updated_at timestamptz
);
create index if not exists mw_donations_created_idx on public.mw_donations (created_at desc);

alter table public.mw_donations enable row level security;
-- Everyone can read the wall; the Stripe session id (proof of ownership) is never granted.
create policy mw_donations_select on public.mw_donations for select using (not hidden);
grant select (id, amount_cents, currency, display_mode, display_name, created_at) on public.mw_donations to anon, authenticated;

create or replace function public.mw_record_donation(p_token text, p_session text, p_amount_cents int, p_currency text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  expected text;
  r public.mw_donations;
begin
  select value into expected from public.mw_settings where key = 'donation_token';
  if expected is null or p_token is null or p_token <> expected then
    raise exception 'invalid donation token';
  end if;
  if p_session is null or p_session = '' or p_amount_cents is null or p_amount_cents <= 0 then
    raise exception 'invalid donation';
  end if;
  insert into public.mw_donations (stripe_session_id, amount_cents, currency)
  values (p_session, p_amount_cents, lower(coalesce(p_currency, 'usd')))
  on conflict (stripe_session_id) do update set amount_cents = excluded.amount_cents, currency = excluded.currency
  returning * into r;
  return jsonb_build_object('id', r.id, 'amount_cents', r.amount_cents, 'currency', r.currency,
    'display_mode', r.display_mode, 'display_name', r.display_name, 'created_at', r.created_at);
end $$;

create or replace function public.mw_set_donation_display(p_token text, p_session text, p_mode text, p_name text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  expected text;
  r public.mw_donations;
begin
  select value into expected from public.mw_settings where key = 'donation_token';
  if expected is null or p_token is null or p_token <> expected then
    raise exception 'invalid donation token';
  end if;
  if p_mode not in ('anonymous', 'name', 'business', 'profile') then
    raise exception 'invalid display mode';
  end if;
  update public.mw_donations
     set display_mode = p_mode,
         display_name = case when p_mode = 'anonymous' then '' else left(coalesce(p_name, ''), 60) end,
         display_updated_at = now()
   where stripe_session_id = p_session and created_at > now() - interval '30 days'
  returning * into r;
  if r.id is null then
    raise exception 'unknown donation';
  end if;
  return jsonb_build_object('id', r.id, 'amount_cents', r.amount_cents, 'currency', r.currency,
    'display_mode', r.display_mode, 'display_name', r.display_name, 'created_at', r.created_at);
end $$;

-- Admin backstop beside the automatic name filter: hide an entry from the wall.
create or replace function public.mw_hide_donation(p_id uuid)
returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.mw_is_admin() then
    raise exception 'not allowed';
  end if;
  update public.mw_donations set hidden = true where id = p_id;
end $$;

revoke execute on function public.mw_record_donation(text, text, int, text) from public;
revoke execute on function public.mw_set_donation_display(text, text, text, text) from public;
revoke execute on function public.mw_hide_donation(uuid) from public, anon;
-- The Worker calls the two token-gated functions with the anon key.
grant execute on function public.mw_record_donation(text, text, int, text) to anon, authenticated;
grant execute on function public.mw_set_donation_display(text, text, text, text) to anon, authenticated;
grant execute on function public.mw_hide_donation(uuid) to authenticated;
