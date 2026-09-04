-- RuggedRoute HQ — default data, seeded per owner on first sign-in via hq_bootstrap().
-- Everything here is idempotent (on conflict do nothing) so it is safe to call repeatedly.

create or replace function public.hq_bootstrap() returns jsonb
language plpgsql security invoker set search_path = public as $$
declare
  v_uid uuid := auth.uid();
  a_sos uuid; a_stc uuid; a_irs uuid; a_bonner uuid; a_play uuid;
  v_year int := extract(year from current_date)::int;
begin
  if v_uid is null or not public.hq_is_owner() then
    raise exception 'not allowed';
  end if;

  insert into public.hq_business_profile (owner, legal_name, entity_type, state, county, timezone)
  values (v_uid, 'Addictive Media Productions LLC', 'smllc', 'ID', 'Bonner', 'America/Los_Angeles')
  on conflict (owner) do nothing;

  -- Schedule C categories (line numbers from Form 1040 Schedule C, Part II)
  insert into public.hq_categories (owner, key, name, schedule_c_line, deductible_pct, sort) values
    (v_uid,'advertising','Advertising','8',100,10),
    (v_uid,'car_truck','Car & truck (mileage)','9',100,20),
    (v_uid,'commissions','Commissions & fees','10',100,30),
    (v_uid,'contract_labor','Contract labor','11',100,40),
    (v_uid,'equipment','Equipment (cameras, drones, computers)','13 / de minimis',100,50),
    (v_uid,'insurance','Insurance (not health)','15',100,60),
    (v_uid,'interest','Interest','16b',100,70),
    (v_uid,'legal_professional','Legal & professional','17',100,80),
    (v_uid,'office','Office expense','18',100,90),
    (v_uid,'rent_lease','Rent or lease','20b',100,100),
    (v_uid,'repairs','Repairs & maintenance','21',100,110),
    (v_uid,'supplies','Supplies','22',100,120),
    (v_uid,'taxes_licenses','Taxes & licenses','23',100,130),
    (v_uid,'travel','Travel','24a',100,140),
    (v_uid,'meals','Meals','24b',50,150),
    (v_uid,'utilities','Utilities, phone & internet','25',100,160),
    (v_uid,'software_subscriptions','Software & subscriptions','27a',100,170),
    (v_uid,'bank_fees','Bank & merchant fees','27a',100,180),
    (v_uid,'education','Education & training','27a',100,190),
    (v_uid,'home_office','Home office / shop','30',100,200),
    (v_uid,'other','Other','27a',100,900),
    (v_uid,'personal','Personal (not deductible)',null,0,999)
  on conflict (owner, key) do nothing;

  -- Agencies (jurisdiction cards)
  insert into public.hq_agencies (owner, key, name, login_url, notes) values
    (v_uid,'id_sos','Idaho Secretary of State','https://sosbiz.idaho.gov','Annual report, ABN filings, entity status.'),
    (v_uid,'id_stc','Idaho State Tax Commission (TAP)','https://tax.idaho.gov','Form 40 income tax. No sales tax obligation for services/app subscriptions.'),
    (v_uid,'irs','IRS','https://www.irs.gov/payments','Schedule C on Form 1040, 1040-ES quarterlies, 1099-NEC.'),
    (v_uid,'bonner_planning','Bonner County Planning','https://www.bonnercountyid.gov/home-occupation','Home Occupation permit. 208-265-1458, planning@bonnercountyid.gov'),
    (v_uid,'google_play','Google Play Console','https://play.google.com/console','Developer account, target SDK deadlines, payouts.'),
    (v_uid,'cloudflare','Cloudflare','https://dash.cloudflare.com','Domain, Workers, R2.'),
    (v_uid,'supabase','Supabase','https://supabase.com/dashboard','App + HQ database.')
  on conflict (owner, key) do nothing;

  select id into a_sos from public.hq_agencies where owner = v_uid and key = 'id_sos';
  select id into a_stc from public.hq_agencies where owner = v_uid and key = 'id_stc';
  select id into a_irs from public.hq_agencies where owner = v_uid and key = 'irs';
  select id into a_bonner from public.hq_agencies where owner = v_uid and key = 'bonner_planning';
  select id into a_play from public.hq_agencies where owner = v_uid and key = 'google_play';

  -- Deadline rules (verified 2026-09-04; see docs/research/2026-09-04-business-tools-research.md §2.2)
  insert into public.hq_deadline_rules
    (owner, key, title, agency_id, category, applies_to, schedule, reminder_offsets, verify_required, enabled, url, description, consequence, playbook, source_url, retired_on, retired_reason)
  values
    (v_uid,'id_sos_annual_report','Idaho annual report', a_sos,'state','{smllc,llc,scorp,ccorp}',
      '{"kind":"anniversary_month_end"}','{90,30,7,1}', true, true,
      'https://sosbiz.idaho.gov',
      'Due by the last day of the anniversary month of formation, every year. $0 online. No late fee.',
      'Grounds for administrative dissolution. SOS serves notice, then 60 days to cure. A dissolved LLC gives no liability protection.',
      'File the report on SOSBiz now ($0). If already dissolved: file the reinstatement application ($30, allowed within 10 years), then the overdue report.',
      'https://legislature.idaho.gov/statutesrules/idstat/title30/t30ch21/sect30-21-213/', null, null),
    (v_uid,'id_abn_renewal','Idaho assumed business name renewal', a_sos,'state','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"none"}','{}', false, false, 'https://sos.idaho.gov',
      'Idaho ABNs no longer expire. Only amendments or cancellation are filed.', null, null,
      'https://sos.idaho.gov/business-services-resources/business-entities-assumed-business-names-faq/',
      '2026-09-04', 'Idaho ABNs no longer expire (SOS FAQ).'),
    (v_uid,'id_form40','Idaho Form 40 income tax return', a_stc,'state','{sole,smllc}',
      '{"kind":"fixed","month":4,"day":15}','{60,30,7,1}', false, true,
      'https://tax.idaho.gov', 'Schedule C flows onto your Idaho Form 40. Extension is automatic if 80% of this year or 100% of last year is paid by April 15.',
      'Penalties and interest on unpaid tax.', 'File on TAP; pay what you can by April 15 to keep the automatic extension.',
      'https://tax.idaho.gov/taxes/income-tax/individual-income/', null, null),
    (v_uid,'id_form65_41s','Idaho Form 65 / 41S entity return', a_stc,'state','{llc,scorp}',
      '{"kind":"fixed","month":4,"day":15}','{60,30,7,1}', true, true,
      'https://tax.idaho.gov', 'Multi-member LLC (Form 65) or S-corp (Form 41S). S-corps owe the $20 minimum tax.',
      'Penalties and interest.', 'File on TAP.', 'https://tax.idaho.gov/taxes/income-tax/business-income/', null, null),
    (v_uid,'id_41es','Idaho Form 41ES estimated payments (C-corp only)', a_stc,'state','{ccorp}',
      '{"kind":"fixed_multi","dates":[[4,15],[6,15],[9,15],[12,15]]}','{14,3}', true, true,
      'https://tax.idaho.gov', 'Only if Idaho liability is $500 or more. Individuals and pass-throughs have no Idaho estimate requirement.',
      'Underpayment interest.', 'Pay on TAP.', 'https://tax.idaho.gov/document-mngr/forms_ein00035/', null, null),
    (v_uid,'id_sales_tax','Idaho sales tax', a_stc,'state','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"none"}','{}', false, false, 'https://tax.idaho.gov',
      'Not applicable: services, ad revenue, sponsorships, app subscriptions and streamed video are not taxable in Idaho (Idaho Code 63-3616(b)). Turn on only if you sell downloads with a permanent right to use, merch, or printed goods.',
      null, 'Register for a seller''s permit on TAP before the first taxable sale.',
      'https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch36/sect63-3616/', null, null),
    (v_uid,'bonner_home_occupation','Bonner County Home Occupation permit', a_bonner,'county','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"once"}','{14,3}', true, true, 'https://www.bonnercountyid.gov/home-occupation',
      'Bonner County requires a Home Occupation permit for home-based businesses (Level I: resident-run, up to four employees). Blanchard is unincorporated, so no city license applies.',
      'Zoning complaint exposure.', 'Call Planning (208-265-1458) to confirm a no-visitor digital business needs it, then file once and attach the approval here.',
      'https://www.bonnercountyid.gov/home-occupation', null, null),
    (v_uid,'fed_1040es','Federal estimated tax (Form 1040-ES)', a_irs,'federal','{sole,smllc}',
      '{"kind":"fixed_multi","dates":[[4,15],[6,15],[9,15],[1,15]]}','{21,7,1}', false, true,
      'https://www.irs.gov/payments', 'Quarterly. Pay through IRS Direct Pay or your IRS online account.',
      'Underpayment penalty (interest-based).', 'Pay what the estimate helper shows; safe harbor is 100% of last year''s tax (110% if AGI over $150k).',
      'https://www.irs.gov/publications/p509', null, null),
    (v_uid,'fed_1040','Federal return (Form 1040 with Schedule C + SE)', a_irs,'federal','{sole,smllc}',
      '{"kind":"fixed","month":4,"day":15}','{60,30,7,1}', false, true,
      'https://www.irs.gov', 'Business income and expenses on Schedule C; self-employment tax on Schedule SE.',
      'Failure-to-file penalty is 5%/month of unpaid tax.', 'File Form 4868 for an automatic six-month extension if needed; pay by April 15 regardless.',
      'https://www.irs.gov/publications/p509', null, null),
    (v_uid,'fed_1120s_1065','Federal entity return (1120-S / 1065)', a_irs,'federal','{llc,scorp}',
      '{"kind":"fixed","month":3,"day":15}','{60,30,7,1}', true, true,
      'https://www.irs.gov', 'Partnership or S-corp return, a month before the personal return.',
      '$220+ per partner/shareholder per month late.', 'File Form 7004 for an extension.',
      'https://www.irs.gov/publications/p509', null, null),
    (v_uid,'fed_1120','Federal corporate return (Form 1120)', a_irs,'federal','{ccorp}',
      '{"kind":"fixed","month":4,"day":15}','{60,30,7,1}', true, true, 'https://www.irs.gov', null, null, null,
      'https://www.irs.gov/publications/p509', null, null),
    (v_uid,'fed_2553','S-corp election (Form 2553)', a_irs,'federal','{smllc,llc}',
      '{"kind":"fixed","month":3,"day":15}','{30,7}', true, false, 'https://www.irs.gov/forms-pubs/about-form-2553',
      'Only if you decide to elect S-corp status. Due within 2 months and 15 days of the start of the tax year it should take effect. Usually only worth it above roughly $60-80k net profit; ask an accountant.',
      null, null, 'https://www.irs.gov/publications/p509', null, null),
    (v_uid,'fed_1099_nec','1099-NEC to contractors + IRS', a_irs,'federal','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"fixed","month":1,"day":31}','{30,14,3}', false, true, 'https://www.irs.gov/forms-pubs/about-form-1099-nec',
      'For each contractor paid $2,000 or more during the year (threshold raised from $600 for payments after Dec 31, 2025). Collect a W-9 from every contractor before paying them.',
      'Penalties per missed form.', 'HQ totals the Contract labor category per payee; file through IRIS (free) or your tax software.',
      'https://www.irs.gov/publications/p509', null, null),
    (v_uid,'fincen_boi','FinCEN beneficial ownership report (BOI)', a_irs,'federal','{smllc,llc,scorp,ccorp}',
      '{"kind":"none"}','{}', false, false, 'https://www.fincen.gov/boi',
      'Permanently eliminated for all U.S.-created entities by FinCEN final rule of Aug 11, 2026.', null, null,
      'https://www.fincen.gov/boi', '2026-09-04', 'FinCEN final rule (Aug 2026) exempts domestic entities.'),
    (v_uid,'play_target_sdk','Google Play target API level deadline', a_play,'platform','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"fixed","month":8,"day":31}','{60,30,7}', true, true, 'https://developer.android.com/google/play/requirements/target-sdk',
      'New apps and updates must target the required API level by the annual deadline (typically Aug 31). Missing it blocks app updates.',
      'Cannot publish updates.', 'Bump targetSdk in the RuggedRoute app and ship a release before the date.',
      'https://developer.android.com/google/play/requirements/target-sdk', null, null),
    (v_uid,'domain_renewal','Domain renewal (ruggedroutehq.com)', null,'vendor','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"annual_from","date":null}','{30,7,1}', true, false, null,
      'Enter the renewal date from your registrar to enable this reminder.', 'Site, email and tile server go dark.', 'Renew at the registrar; turn on auto-renew.', null, null, null),
    (v_uid,'insurance_renewal','Business insurance renewal', null,'vendor','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"annual_from","date":null}','{45,14,3}', true, false, null,
      'Enter the policy renewal date to enable this reminder.', 'Lapse in coverage.', null, null, null, null),
    (v_uid,'annual_resolution','Annual member resolution / minutes', null,'internal','{smllc,llc,scorp,ccorp}',
      '{"kind":"anniversary_month_end"}','{30,7}', false, true, null,
      'One-page written consent of the sole member approving the year''s actions and financials. Keeps the corporate veil intact.',
      'Weakens liability protection.', 'Generate from the template in HQ, sign, file in the Formation folder.', null, null, null),
    (v_uid,'backup_restore_test','Test the HQ backup restores', null,'internal','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"fixed_multi","dates":[[1,15],[4,15],[7,15],[10,15]]}','{3}', false, true, null,
      'Open the latest backup and confirm a receipt and a document open from it.', null, null, null, null, null),
    (v_uid,'sos_status_check','Check entity status on SOSBiz', a_sos,'internal','{smllc,llc,scorp,ccorp}',
      '{"kind":"fixed_multi","dates":[[2,1],[5,1],[8,1],[11,1]]}','{0}', false, true, 'https://sosbiz.idaho.gov',
      'SOSBiz has no API, so this is a 30-second manual check that the entity still shows Active.', null,
      'If not Active: see the annual report playbook.', null, null, null),
    (v_uid,'address_change','Move business address to Blanchard', null,'internal','{sole,smllc,llc,scorp,ccorp}',
      '{"kind":"once"}','{7}', true, true, null,
      'When operations move: IRS Form 8822-B, Idaho SOS (next annual report or an amendment), bank, registrar, Google Play developer profile.',
      'Mail from the IRS or SOS goes to the old address.', 'Work the checklist top to bottom and attach confirmations.', null, null, null)
  on conflict (owner, key) do nothing;

  -- Retention clocks (IRS Pub 583; null keep_years = keep forever)
  insert into public.hq_retention_rules (owner, applies_to, keep_years, basis, note) values
    (v_uid,'receipts',7,'irs','IRS says 3 (6 if income under-reported >25%); 7 is the safe rule.'),
    (v_uid,'tax_returns',null,'irs','Keep returns forever; supporting records 7 years.'),
    (v_uid,'employment_tax',4,'irs','4 years after the tax is due or paid.'),
    (v_uid,'asset_records',null,'irs','Until 3 years after the year the asset is disposed of.'),
    (v_uid,'formation',null,'governance','Articles, operating agreement, EIN letter, resolutions: forever.'),
    (v_uid,'contracts',7,'contract','7 years after the contract ends.'),
    (v_uid,'insurance',null,'insurance','As long as a claim could still arise.'),
    (v_uid,'statements',7,'irs','Bank and card statements.'),
    (v_uid,'agency_letters',7,'irs',null)
  on conflict (owner, applies_to) do nothing;

  -- Legal-safety checklist (corporate veil)
  insert into public.hq_checklist_items (owner, key, title, why, sort) values
    (v_uid,'separate_bank_account','Separate business bank account','No commingling of personal and business money is the #1 veil protection.',10),
    (v_uid,'business_card','Business debit/credit card','Pay business expenses only from business accounts.',20),
    (v_uid,'operating_agreement','Signed operating agreement on file','Even a single-member LLC should have one; banks and courts ask for it.',30),
    (v_uid,'ein_letter','IRS CP-575 EIN letter in the vault','The IRS never reissues it.',40),
    (v_uid,'annual_report_current','Idaho annual report current','Missing it leads to administrative dissolution.',50),
    (v_uid,'registered_agent_current','Registered agent current with the SOS','Required for the LLC to exist in good standing.',60),
    (v_uid,'annual_resolution','Annual member resolution signed','Shows the LLC is run as a real entity.',70),
    (v_uid,'dba_ruggedroute','RuggedRoute registered as an assumed business name','Ties the product name back to the LLC ($25, never expires).',80),
    (v_uid,'play_account_in_llc_name','Google Play developer account in the LLC''s name with the EIN','Revenue and contracts belong to the entity, not you personally.',90),
    (v_uid,'contracts_signed_as_llc','Contracts signed as "Addictive Media Productions LLC, by [name], Member"','Signing personally can make you personally liable.',100),
    (v_uid,'address_consistent','Same business address everywhere (IRS, SOS, bank, Play)','Mismatches cause lost mail and identity flags.',110),
    (v_uid,'home_occupation_permit','Bonner County Home Occupation permit','County requirement for home-based businesses.',120),
    (v_uid,'insurance','Business insurance in place (or a documented decision not to carry it)','General liability / E&O if clients or the public are involved.',130)
  on conflict (owner, key) do nothing;

  insert into public.hq_tax_setaside (owner, year) values (v_uid, v_year)
  on conflict (owner, year) do nothing;

  insert into public.hq_tax_years (owner, year) values (v_uid, v_year)
  on conflict (owner, year) do nothing;

  return public.hq_home_summary();
end $$;
grant execute on function public.hq_bootstrap() to authenticated;
