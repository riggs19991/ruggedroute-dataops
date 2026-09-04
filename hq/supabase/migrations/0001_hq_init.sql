-- RuggedRoute HQ — schema v1 (2026-09-04)
-- Lives in the shared Supabase project alongside the RuggedRoute app. Every HQ table is
-- prefixed hq_ and locked by row-level security to the founder's login only.

-- ---------------------------------------------------------------- allow-list + helpers
create table if not exists public.hq_allowed_emails (
  email text primary key,
  added_at timestamptz not null default now()
);
alter table public.hq_allowed_emails enable row level security;
insert into public.hq_allowed_emails (email) values ('riggs1991@gmail.com') on conflict do nothing;

create or replace function public.hq_is_owner() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce(
    (select true from public.hq_allowed_emails a
      where lower(a.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
      limit 1),
    false);
$$;
revoke all on function public.hq_is_owner() from public;
grant execute on function public.hq_is_owner() to authenticated;

create or replace function public.hq_touch_updated_at() returns trigger
language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

-- ---------------------------------------------------------------- core tables
create table public.hq_business_profile (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  legal_name text not null default '',
  dba text,
  entity_type text not null default 'smllc' check (entity_type in ('sole','smllc','llc','scorp','ccorp')),
  state text not null default 'ID',
  formation_date date,
  formation_date_verified boolean not null default false,
  fiscal_year_end text not null default '12-31',
  timezone text not null default 'America/Los_Angeles',
  address jsonb not null default '{}'::jsonb,
  county text,
  ein_last4 text,
  ein_vault_id uuid,
  registered_agent_contact_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner)
);

create table public.hq_categories (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  key text not null,
  name text not null,
  schedule_c_line text,
  deductible_pct int not null default 100 check (deductible_pct between 0 and 100),
  sort int not null default 100,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, key)
);

create table public.hq_contacts (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name text not null,
  role text,
  company text,
  phone text,
  email text,
  address text,
  notes text,
  secrets_vault_id uuid,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.hq_agencies (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  key text not null,
  name text not null,
  login_url text,
  account_ids jsonb not null default '{}'::jsonb,
  contact_id uuid references public.hq_contacts(id) on delete set null,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, key)
);

create table public.hq_vendors (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name text not null,
  normalized_name text not null,
  default_category_id uuid references public.hq_categories(id) on delete set null,
  website text,
  notes text,
  contact_id uuid references public.hq_contacts(id) on delete set null,
  receipt_exempt boolean not null default false,
  expected_min numeric(12,2),
  expected_max numeric(12,2),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, normalized_name)
);

create table public.hq_vendor_aliases (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  vendor_id uuid not null references public.hq_vendors(id) on delete cascade,
  alias_pattern text not null,
  created_at timestamptz not null default now()
);

create table public.hq_files (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  bucket text not null default 'hq-vault',
  storage_path text not null,
  mime text not null,
  bytes bigint not null default 0,
  sha256 text,
  width int,
  height int,
  page_count int,
  ocr_text text,
  uploaded_via text not null default 'app' check (uploaded_via in ('camera','upload','email','app','ci')),
  created_at timestamptz not null default now(),
  unique (owner, storage_path)
);
create index hq_files_sha_idx on public.hq_files (owner, sha256);

create table public.hq_accounts (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  name text not null,
  kind text not null default 'checking' check (kind in ('checking','card','savings','other')),
  last4 text,
  csv_profile jsonb not null default '{}'::jsonb,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.hq_subscriptions (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  vendor_id uuid references public.hq_vendors(id) on delete set null,
  name text not null,
  amount numeric(12,2),
  cadence text not null default 'monthly' check (cadence in ('monthly','quarterly','annual','usage')),
  next_renewal date,
  payment_method text,
  cancel_by date,
  url text,
  notes text,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.hq_trips (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  date date not null,
  from_place text,
  to_place text,
  miles numeric(8,1) not null default 0,
  purpose text,
  vehicle text,
  entry_mode text not null default 'manual' check (entry_mode in ('manual','odometer','gps')),
  odometer_start numeric(10,1),
  odometer_end numeric(10,1),
  start_ll jsonb,
  end_ll jsonb,
  rate_year int,
  tags text[] not null default '{}',
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.hq_transactions (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  account_id uuid references public.hq_accounts(id) on delete set null,
  posted_on date not null,
  amount numeric(12,2) not null,
  description_raw text not null default '',
  merchant_normalized text,
  category_id uuid references public.hq_categories(id) on delete set null,
  status text not null default 'unmatched' check (status in ('unmatched','matched','exempt','personal')),
  import_batch_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index hq_transactions_owner_date_idx on public.hq_transactions (owner, posted_on desc);

create table public.hq_receipts (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  file_id uuid references public.hq_files(id) on delete set null,
  vendor_id uuid references public.hq_vendors(id) on delete set null,
  transaction_id uuid references public.hq_transactions(id) on delete set null,
  date date,
  subtotal numeric(12,2),
  tax numeric(12,2),
  tip numeric(12,2),
  total numeric(12,2),
  currency text not null default 'USD',
  payment_method text,
  last4 text,
  category_id uuid references public.hq_categories(id) on delete set null,
  status text not null default 'needs_review' check (status in ('needs_review','confirmed','reconciled','void')),
  paid_personally boolean not null default false,
  notes text,
  tags text[] not null default '{}',
  extracted jsonb,
  extracted_text text,
  field_confidence jsonb not null default '{}'::jsonb,
  verified_fields text[] not null default '{}',
  subscription_id uuid references public.hq_subscriptions(id) on delete set null,
  trip_id uuid references public.hq_trips(id) on delete set null,
  source text not null default 'camera' check (source in ('camera','upload','email','manual')),
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  search tsvector generated always as (
    to_tsvector('english', coalesce(notes,'') || ' ' || coalesce(extracted_text,''))) stored
);
create index hq_receipts_owner_date_idx on public.hq_receipts (owner, date desc);
create index hq_receipts_search_idx on public.hq_receipts using gin (search);

create table public.hq_receipt_line_items (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  receipt_id uuid not null references public.hq_receipts(id) on delete cascade,
  description text not null,
  qty numeric(10,3),
  amount numeric(12,2),
  category_id uuid references public.hq_categories(id) on delete set null,
  sort int not null default 0
);

create table public.hq_vendor_rules (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  vendor_id uuid not null references public.hq_vendors(id) on delete cascade,
  category_id uuid references public.hq_categories(id) on delete set null,
  business_pct int not null default 100 check (business_pct between 0 and 100),
  created_from_receipt_id uuid references public.hq_receipts(id) on delete set null,
  created_at timestamptz not null default now()
);

create table public.hq_deadline_rules (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  key text not null,
  title text not null,
  agency_id uuid references public.hq_agencies(id) on delete set null,
  url text,
  description text,
  consequence text,
  playbook text,
  applies_to text[] not null default '{sole,smllc,llc,scorp,ccorp}',
  schedule jsonb not null,
  reminder_offsets int[] not null default '{90,30,7,1}',
  verify_required boolean not null default false,
  enabled boolean not null default true,
  retired_on date,
  retired_reason text,
  source_url text,
  category text not null default 'state' check (category in ('state','federal','county','platform','vendor','internal','custom')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, key)
);

create table public.hq_deadline_occurrences (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  rule_id uuid not null references public.hq_deadline_rules(id) on delete cascade,
  due_on date not null,
  status text not null default 'upcoming' check (status in ('upcoming','done','skipped','overdue')),
  completed_at timestamptz,
  google_event_id text,
  google_calendar_id text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (rule_id, due_on)
);
create index hq_deadline_occ_due_idx on public.hq_deadline_occurrences (owner, due_on);

create table public.hq_documents (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  title text not null,
  doc_type text not null default 'other' check (doc_type in ('inbox','formation','tax','legal','insurance','license','banking','vendor','statement','agency_letter','evidence','other')),
  file_id uuid references public.hq_files(id) on delete set null,
  version int not null default 1,
  supersedes_id uuid references public.hq_documents(id) on delete set null,
  effective_date date,
  expires_at date,
  tax_year int,
  deadline_occurrence_id uuid references public.hq_deadline_occurrences(id) on delete set null,
  agency_id uuid references public.hq_agencies(id) on delete set null,
  tags text[] not null default '{}',
  custom_fields jsonb not null default '{}'::jsonb,
  ai_summary text,
  ai_set_fields text[] not null default '{}',
  text_content text,
  deleted_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  search tsvector generated always as (
    to_tsvector('english', coalesce(title,'') || ' ' || coalesce(ai_summary,'') || ' ' || coalesce(text_content,''))) stored
);
create index hq_documents_search_idx on public.hq_documents using gin (search);
create index hq_documents_expires_idx on public.hq_documents (owner, expires_at);

create table public.hq_document_links (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  from_document_id uuid not null references public.hq_documents(id) on delete cascade,
  to_document_id uuid not null references public.hq_documents(id) on delete cascade,
  relation text not null default 'related',
  created_at timestamptz not null default now(),
  unique (from_document_id, to_document_id, relation)
);

create table public.hq_share_links (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  target text not null check (target in ('document','bundle','package')),
  target_id uuid not null,
  token text not null unique default encode(gen_random_bytes(24), 'hex'),
  expires_at timestamptz not null,
  password_hash text,
  access_log jsonb not null default '[]'::jsonb,
  revoked_at timestamptz,
  created_at timestamptz not null default now()
);

create table public.hq_income_entries (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  source text not null default 'google_play' check (source in ('google_play','stripe','youtube','sponsorship','invoice','other')),
  period_start date,
  period_end date,
  gross numeric(12,2) not null default 0,
  platform_fee numeric(12,2) not null default 0,
  withholding_tax numeric(12,2) not null default 0,
  refunds numeric(12,2) not null default 0,
  fx_adjustment numeric(12,2) not null default 0,
  net numeric(12,2) not null default 0,
  received_on date,
  transaction_id uuid references public.hq_transactions(id) on delete set null,
  file_id uuid references public.hq_files(id) on delete set null,
  notes text,
  import_batch_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.hq_tax_setaside (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  year int not null,
  pct numeric(5,2) not null default 25,
  federal_rate numeric(5,2),
  idaho_rate numeric(5,2) default 5.3,
  se_rate numeric(5,2) default 15.3,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, year)
);

create table public.hq_invoices (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  number text not null,
  client_contact_id uuid references public.hq_contacts(id) on delete set null,
  issued_on date,
  due_on date,
  line_items jsonb not null default '[]'::jsonb,
  total numeric(12,2) not null default 0,
  status text not null default 'draft' check (status in ('draft','sent','paid','overdue','void')),
  pdf_file_id uuid references public.hq_files(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, number)
);

create table public.hq_mileage_rates (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  year int not null,
  cents_per_mile numeric(6,1) not null,
  created_at timestamptz not null default now(),
  unique (owner, year)
);

create table public.hq_tax_years (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  year int not null,
  status text not null default 'open' check (status in ('open','packaged','filed')),
  package_file_id uuid references public.hq_files(id) on delete set null,
  packaged_at timestamptz,
  filed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, year)
);

create table public.hq_retention_rules (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  applies_to text not null,
  keep_years int,
  basis text not null default 'irs' check (basis in ('irs','governance','contract','insurance','custom')),
  note text,
  created_at timestamptz not null default now(),
  unique (owner, applies_to)
);

create table public.hq_evidence_items (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  title text not null,
  why text,
  source_type text,
  source_id uuid,
  file_id uuid references public.hq_files(id) on delete set null,
  immutable boolean not null default true,
  saved_at timestamptz not null default now()
);

create table public.hq_checklist_items (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  key text not null,
  title text not null,
  why text,
  proof_document_id uuid references public.hq_documents(id) on delete set null,
  status text not null default 'missing' check (status in ('ok','missing','expired','na')),
  last_reviewed date,
  sort int not null default 100,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner, key)
);

create table public.hq_contracts (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  title text not null,
  counterparty_contact_id uuid references public.hq_contacts(id) on delete set null,
  file_id uuid references public.hq_files(id) on delete set null,
  starts_on date,
  ends_on date,
  auto_renews boolean not null default false,
  notice_days int,
  termination_terms text,
  reminder_occurrence_id uuid references public.hq_deadline_occurrences(id) on delete set null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table public.hq_settings (
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  key text not null,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now(),
  primary key (owner, key)
);

create table public.hq_audit_log (
  id bigint generated always as identity primary key,
  owner uuid not null default auth.uid() references auth.users(id) on delete cascade,
  table_name text not null,
  row_id uuid,
  action text not null,
  diff jsonb,
  at timestamptz not null default now()
);
create index hq_audit_owner_at_idx on public.hq_audit_log (owner, at desc);

-- App releases: written by CI (service role), read by the app to self-update.
create table public.hq_app_releases (
  id uuid primary key default gen_random_uuid(),
  platform text not null check (platform in ('android','windows')),
  version text not null,
  build_number int not null,
  storage_path text not null,
  bytes bigint,
  sha256 text,
  notes text,
  published_at timestamptz not null default now(),
  unique (platform, build_number)
);

-- ---------------------------------------------------------------- RLS on everything
do $$
declare t text;
begin
  for t in select unnest(array[
    'hq_business_profile','hq_categories','hq_contacts','hq_agencies','hq_vendors','hq_vendor_aliases',
    'hq_files','hq_accounts','hq_subscriptions','hq_trips','hq_transactions','hq_receipts',
    'hq_receipt_line_items','hq_vendor_rules','hq_deadline_rules','hq_deadline_occurrences',
    'hq_documents','hq_document_links','hq_share_links','hq_income_entries','hq_tax_setaside',
    'hq_invoices','hq_mileage_rates','hq_tax_years','hq_retention_rules','hq_evidence_items',
    'hq_checklist_items','hq_contracts','hq_settings','hq_audit_log'])
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists hq_owner_all on public.%I', t);
    execute format(
      'create policy hq_owner_all on public.%I for all to authenticated
         using (public.hq_is_owner() and owner = auth.uid())
         with check (public.hq_is_owner() and owner = auth.uid())', t);
  end loop;
end $$;

alter table public.hq_app_releases enable row level security;
create policy hq_releases_read on public.hq_app_releases for select to authenticated
  using (public.hq_is_owner());

-- updated_at triggers
do $$
declare t text;
begin
  for t in select c.relname from pg_class c join pg_namespace n on n.oid = c.relnamespace
           where n.nspname = 'public' and c.relkind = 'r' and c.relname like 'hq\_%'
             and exists (select 1 from pg_attribute a where a.attrelid = c.oid and a.attname = 'updated_at')
  loop
    execute format('drop trigger if exists hq_touch on public.%I', t);
    execute format('create trigger hq_touch before update on public.%I
                    for each row execute function public.hq_touch_updated_at()', t);
  end loop;
end $$;

-- ---------------------------------------------------------------- EIN in Vault
-- The EIN never sits in a plain column. hq_set_ein stores it in Supabase Vault and keeps
-- only the last 4 digits on the profile; hq_get_ein returns it decrypted for the owner.
create or replace function public.hq_set_ein(p_ein text) returns void
language plpgsql security definer set search_path = public, vault as $$
declare v_id uuid; v_clean text;
begin
  if not public.hq_is_owner() then raise exception 'not allowed'; end if;
  v_clean := regexp_replace(p_ein, '[^0-9]', '', 'g');
  if length(v_clean) <> 9 then raise exception 'EIN must be 9 digits'; end if;
  select ein_vault_id into v_id from public.hq_business_profile where owner = auth.uid();
  if v_id is not null then
    perform vault.update_secret(v_id, v_clean, 'hq_ein', 'RuggedRoute HQ EIN');
  else
    v_id := vault.create_secret(v_clean, 'hq_ein_' || auth.uid()::text, 'RuggedRoute HQ EIN');
  end if;
  update public.hq_business_profile
     set ein_vault_id = v_id, ein_last4 = right(v_clean, 4)
   where owner = auth.uid();
end $$;

create or replace function public.hq_get_ein() returns text
language plpgsql security definer set search_path = public, vault as $$
declare v_id uuid; v_secret text;
begin
  if not public.hq_is_owner() then raise exception 'not allowed'; end if;
  select ein_vault_id into v_id from public.hq_business_profile where owner = auth.uid();
  if v_id is null then return null; end if;
  select decrypted_secret into v_secret from vault.decrypted_secrets where id = v_id;
  return v_secret;
end $$;
revoke all on function public.hq_set_ein(text) from public;
revoke all on function public.hq_get_ein() from public;
grant execute on function public.hq_set_ein(text) to authenticated;
grant execute on function public.hq_get_ein() to authenticated;

-- ---------------------------------------------------------------- storage buckets
insert into storage.buckets (id, name, public, file_size_limit)
values ('hq-vault', 'hq-vault', false, 52428800),
       ('hq-releases', 'hq-releases', false, 314572800)
on conflict (id) do nothing;

drop policy if exists hq_vault_owner on storage.objects;
create policy hq_vault_owner on storage.objects for all to authenticated
  using (bucket_id = 'hq-vault' and public.hq_is_owner() and owner = auth.uid())
  with check (bucket_id = 'hq-vault' and public.hq_is_owner() and owner = auth.uid());

drop policy if exists hq_releases_owner_read on storage.objects;
create policy hq_releases_owner_read on storage.objects for select to authenticated
  using (bucket_id = 'hq-releases' and public.hq_is_owner() and name like 'builds/%');

-- ---------------------------------------------------------------- home-screen summary
create or replace function public.hq_home_summary() returns jsonb
language sql stable security invoker set search_path = public as $$
  select jsonb_build_object(
    'receipts_needs_review', (select count(*) from public.hq_receipts where owner = auth.uid() and status = 'needs_review' and deleted_at is null),
    'transactions_unmatched', (select count(*) from public.hq_transactions t where t.owner = auth.uid() and t.status = 'unmatched' and t.amount < 0),
    'deadlines_30d', (select count(*) from public.hq_deadline_occurrences where owner = auth.uid() and status in ('upcoming','overdue') and due_on <= current_date + 30),
    'deadlines_overdue', (select count(*) from public.hq_deadline_occurrences where owner = auth.uid() and status = 'overdue'),
    'documents_expiring_90d', (select count(*) from public.hq_documents where owner = auth.uid() and deleted_at is null and expires_at is not null and expires_at <= current_date + 90),
    'documents_inbox', (select count(*) from public.hq_documents where owner = auth.uid() and deleted_at is null and doc_type = 'inbox'),
    'agency_letters_open', (select count(*) from public.hq_documents where owner = auth.uid() and deleted_at is null and doc_type = 'agency_letter' and deadline_occurrence_id is null),
    'next_deadline', (select jsonb_build_object('title', r.title, 'due_on', o.due_on, 'status', o.status)
                        from public.hq_deadline_occurrences o join public.hq_deadline_rules r on r.id = o.rule_id
                       where o.owner = auth.uid() and o.status in ('upcoming','overdue') order by o.due_on limit 1),
    'month_spent', (select coalesce(sum(total),0) from public.hq_receipts where owner = auth.uid() and deleted_at is null and status <> 'void' and date >= date_trunc('month', current_date)),
    'month_income', (select coalesce(sum(net),0) from public.hq_income_entries where owner = auth.uid() and received_on >= date_trunc('month', current_date)),
    'month_miles', (select coalesce(sum(miles),0) from public.hq_trips where owner = auth.uid() and deleted_at is null and date >= date_trunc('month', current_date)),
    'profile_complete', (select formation_date is not null and legal_name <> '' from public.hq_business_profile where owner = auth.uid())
  );
$$;
grant execute on function public.hq_home_summary() to authenticated;
