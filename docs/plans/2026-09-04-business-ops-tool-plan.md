# RuggedRoute HQ — business back-office tool: full build plan

**Date:** 2026-09-04 · **Owner:** founder (riggs1991@gmail.com) · **Status:** plan v2 (research-informed), awaiting go-ahead
**Companion:** `docs/research/2026-09-04-business-tools-research.md` — what ~50 existing tools do well, and the verified Idaho/federal rules
**Working name:** *RuggedRoute HQ* (rename anytime — nothing depends on it)

---

## 0. What this is, in one paragraph

A private, single-user web app (installable on your phone like a native app) that is the one place
everything about running the business lives: every receipt (photographed, emailed, or uploaded),
every important document (formation papers, EIN letter, insurance, contracts, licenses), every
recurring bill and subscription, every income payout, every mile driven for the business, and every
deadline the state of Idaho, the IRS, Google Play, Cloudflare, and your domain registrar will ever
impose on you. Deadlines push into your Google Calendar so reminders reach your phone without you
opening the app. At year end you press one button and get a ZIP your accountant (or you, doing
taxes) can use directly: every receipt organized by category and month, a spreadsheet totaled by
Schedule C line, a mileage log, an income summary, and a PDF cover sheet.

Guiding rules for the build:

1. **Capture must take under 10 seconds.** If photographing a receipt is slower than tossing it in
   a shoebox, the shoebox wins. Camera → auto-extract → one tap to confirm.
2. **Nothing is ever lost.** Files live in private object storage, the database is backed up
   nightly to your own R2 bucket, and a "download everything" button exists from day one.
3. **You own it.** Your Supabase project, your Cloudflare account, your Google account, your repo.
   No vendor holds your business records hostage. Monthly running cost is approximately $0.
4. **Reminders live where you already look.** Google Calendar is the reminder engine. The app is
   the system of record; the calendar is the notification surface.
5. **Built for one user, built to last.** No multi-tenant complexity. But built correctly (row-level
   security, typed schema, migrations in git) so it is still trustworthy in ten years.

---

## 1. What already exists (verified 2026-09-04)

| Asset | State | How HQ uses it |
|---|---|---|
| Cloudflare account `c13779e4…` with zone `ruggedroutehq.com` | Live (tiles worker, R2, KV) | Host the app on Pages at `hq.ruggedroutehq.com`; Email Routing for a `receipts@` inbox; R2 bucket for backups |
| Supabase org **Rugged Route** (`fogmcfumcigxaoxnokip`), one project `tzucpijgyjhpgwukjsau` (us-east-1, Postgres 17, tables `trails`, `spatial_ref_sys`) | Active | That project is the **app** database. HQ gets its **own** Supabase project (see §5) so business records are never behind the same keys as the mobile app |
| Google account riggs1991@gmail.com, calendars "riggs1991@gmail.com" (tz America/Los_Angeles) and "Family" | Connected | HQ creates a dedicated **"RuggedRoute Business"** calendar and pushes deadlines into it |
| GitHub `riggs19991/ruggedroute-dataops` | This repo | Holds this plan. The app itself gets a new repo `ruggedroute-hq` (see §5) |

Two things I noticed along the way:

- Your Google primary calendar is set to **America/Los_Angeles**. If you are in Idaho (Mountain
  time), deadline reminders will fire an hour off. HQ will store its own timezone setting
  (default America/Boise) and set it explicitly on every event it creates, so this cannot bite you,
  but you may want to fix the calendar itself too.
- Supabase's advisor flags `public.spatial_ref_sys` in the app project as having RLS disabled.
  That is the PostGIS reference table (8,500 rows of coordinate-system definitions, public data) and
  this is a well-known false positive. Nothing to do, just noting I saw it.

---

## 2. Feature modules

Listed in the order they will be built. Each one is usable on its own; you will not wait for the
whole thing before it helps.

### 2.1 Receipts (the core)

- **Capture from anywhere:** phone camera (opens straight to the rear camera from the home-screen
  icon), photo-library upload, PDF upload, drag-and-drop on desktop, and **email forwarding** to
  `receipts@ruggedroutehq.com` (Google Play invoices, Cloudflare, Mapbox, Supabase, domain renewals,
  Amazon — most of your spend already arrives as email; you should never have to screenshot it).
- **Automatic extraction:** every image/PDF is sent to Claude (vision) which returns vendor, date,
  subtotal, tax, total, payment method (last 4 digits if visible), line items, and a **suggested
  category**, each with a **confidence score**. You review a pre-filled form and tap Save. Every
  AI-filled field stays marked *AI-set* until you confirm it (M-Files), low-confidence fields are
  highlighted, and the source snippet is shown next to the value (Box/Juro). Wrong guess → change
  it; HQ remembers vendor→category so the same vendor is right next time.
- **Categories aligned to IRS Schedule C lines** (so year-end is a sum, not a sort): Advertising ·
  Car & truck · Contract labor · Insurance · Legal & professional · Office expense · Supplies ·
  Taxes & licenses · Travel · Meals (flagged 50%) · Utilities/phone/internet · Software &
  subscriptions · Equipment (possible depreciation) · Home office · Bank/merchant fees · Other. Fully
  editable; if you turn out to file as an S-corp the mapping changes in one table.
- **Status flow:** *needs review* (auto-extracted, unconfirmed) → *confirmed* → *reconciled*
  (matched to a bank/card transaction). **Transactions are first-class:** you import the bank/card
  statement CSV monthly (a live bank feed is an optional later upgrade), and receipts attach to
  transactions. That flips the question from "did I photograph everything?" to "which charges have
  no receipt?" (Keeper/Found/Kick). Matching is deterministic: a receipt is auto-attached only when
  **2 of 3** of date (±3 days), amount, and merchant match **and** there is exactly one candidate;
  otherwise it waits for you (Brex/Wave). The extracted total is cross-checked against the bank
  amount to catch a hallucinated digit.
- **Search & filter** by vendor, category, date range, amount, text inside the receipt (extracted
  text is stored and indexed), tag (e.g. a trip or project name), and whether it is reimbursable /
  personal-card-paid.
- **Duplicate detection:** same vendor + same total within a **±5-day window** (Dext's rule) or an
  identical file hash flags *both* records with an amber badge. Never auto-deleted; you merge or
  keep. Email + photo of the same receipt is the most common double-count.
- **Rules that compound:** after you change a category, HQ asks **"make this a rule for this
  vendor?"** (Found/Dext). Vendor aliases ("AMZN Mktp" = "Amazon") are confirmed once. The first
  receipt from a new vendor is manual; the rest auto-file (Zoho).
- **Receipt-required threshold:** below a settable amount (default $25) a bank line without a
  receipt is *not* nagged about; above it, it is. Exempt merchants ("dismiss and exempt Cloudflare")
  stop the nagging for known subscriptions (Expensify/Ramp).
- **Original always kept.** Extracted fields are metadata; the image/PDF is never modified.

### 2.2 Compliance calendar & reminders

- A **deadline library** seeded with everything in §4, each with: what it is, who it is filed with,
  the link to file it, what happens if you miss it, how the date is computed (fixed date vs.
  "anniversary month" vs. "N days after year end"), and lead-time reminder offsets (e.g. 30 / 7 / 1
  days).
- Deadlines are **recurring rules**, not one-off dates. HQ materializes the next 24 months of
  occurrences, rolls weekend/holiday dates forward, and keeps them moving. Default reminder ladder
  **90 / 30 / 7 / 1 days** (Northwest starts at 90; LegalZoom caps at five touches).
- **Entity-type switch:** choosing LLC vs. S-corp vs. sole proprietor swaps the rule set (adds or
  removes 1120-S/41S, the $20 Idaho minimum tax, Form 2553). Retired rules (BOI, DBA renewal) are
  shown as *retired* with the reason, never silently deleted (Mosey).
- **Good-standing tile** on the dashboard: green/amber/red from open vs. overdue items, and a
  **"days until dissolution risk"** countdown that turns on the day after the Idaho annual-report
  due date (60-day cure window) (ZenBusiness/Northwest).
- **Missed-deadline playbook:** every rule carries a "what to do if you miss it" (Idaho:
  reinstatement form, $30, within 10 years) shown the moment it goes overdue (Rippling).
- **Jurisdiction cards:** one card per agency — Idaho SOS, Idaho State Tax Commission, IRS, your
  city — with your account IDs, login link, next due, last filed, and the agency letters you
  scanned (Firstbase/Mosey).
- **One-way sync to Google Calendar:** each occurrence becomes an event on the "RuggedRoute
  Business" calendar with Google-native reminders (popup + email). HQ stores the Google event id so
  edits/deletes update the same event instead of duplicating. Marking a deadline *done* in HQ
  updates the event title to "✓ Filed — Idaho Annual Report 2027".
- **Completion log:** when you mark a filing done you can attach the confirmation (PDF/screenshot)
  right there, and it lands in the document vault linked to that deadline. Next year you can see
  exactly what you filed and what it looked like.
- **Weekly digest email** (Monday morning): what is due in the next 30 days, receipts awaiting
  review, subscriptions renewing, documents expiring. Optional; on by default.
- **Custom deadlines/tasks:** anything else ("renew trailer registration", "call accountant about
  Q3") with the same reminder machinery.

### 2.3 Document vault

- Folders by type: **Formation** (Articles of Organization, Certificate of Organization, operating
  agreement, EIN confirmation letter CP-575, Idaho SOS filings), **Tax** (returns by year, 1099s,
  estimated-payment confirmations, state tax permits), **Legal** (contracts, terms of service,
  privacy policy versions, trademark filings), **Insurance** (policies, certificates), **Licenses &
  registrations** (business license, assumed business name), **Banking** (account opening docs,
  statements), **Vendors** (agreements: Google Play developer, Apple, Mapbox, Cloudflare,
  Supabase), **Statements** (monthly bank/card PDFs — a good habit for reconciliation), **Other**.
- Every document can carry an **effective date, expiration date, and renewal reminder** → feeds
  the same reminder engine (insurance renewal, license expiry, contract end).
- Version history: uploading a new version of "Operating Agreement" keeps the old one.
- Full-text search across PDFs (text extracted on upload).
- **Inbox-first:** everything lands unsorted; Claude proposes title, type, counterparty, dates,
  and a one-line summary; you approve or set a folder to auto-file (Trustworthy/Paperless-GPT).
- **Typed custom fields** per document type — money with currency, dates, URLs, and
  **document links with an automatic reverse link** (amendment ↔ master agreement, filing
  confirmation ↔ deadline) (Paperless-ngx).
- **Agency letters:** scan any letter from the SOS/Tax Commission/IRS, tag the agency, and it
  spawns a task with a due date (Mosey).
- **Share links** for your accountant or attorney: expiring (1 h / 1 d / 1 w / 1 mo), optional
  password, single document or a bundle, every access logged (Paperless/Box/Trustworthy).

### 2.4 Recurring costs & subscriptions

- Every recurring bill with vendor, amount, cadence, next renewal, payment method, what it is for,
  and cancel-by date. Seed list from your known stack: Cloudflare (Workers/R2), Mapbox, Supabase,
  Google Play developer account, Apple Developer Program (if/when iOS), domain registrations,
  Google Workspace, GitHub, phone/internet share, any SaaS.
- **Expected vs. actual:** when a receipt from that vendor is confirmed, it is auto-linked to the
  subscription. The dashboard shows "expected this month" vs. "received" so a missing invoice
  (or a surprise price hike) is visible.
- Renewal reminders 14 days ahead for annual items (developer accounts, domains, insurance).
- **Expected-amount ranges and variance alerts** (Firefly III/Puzzle): each subscription has an
  expected range; a charge outside it, or any vendor more than a settable % above its 3-month
  average, shows up in the exceptions inbox as "Mapbox went from $12 to $31". Monthly vendor
  breakdown with trend arrows for cutting waste (Kick).

### 2.5 Income & payouts

- Simple ledger, not double-entry: each Google Play payout / Stripe transfer / invoice paid, with
  gross, fees, net, period covered, and the PDF statement attached. Monthly and YTD totals.
- **Google Play payout parser.** No mainstream tool does this cleanly (Stripe's connector ignores
  withholding and commission). HQ imports the Play Console monthly earnings CSV (and RevenueCat
  exports if you use it), splits gross / Google fee / withholding tax / refunds / FX, and reconciles
  the net to the bank deposit. This is the highest-leverage custom piece for an app business.
- **Tax set-aside:** a settable % of every payout is shown as "already spoken for" with a one-tap
  "move $X to savings" prompt, and the dashboard shows what is yours to keep (Found/Relay/Lettuce).
- Optional **invoices** for any consulting/custom work: generate a PDF invoice from a template,
  track sent / paid, remind on overdue. (Small module; only built if you want it.)

### 2.6 Mileage & field trips

- RuggedRoute's whole product is ground-truthing routes, so driving to trailheads *is* business
  travel and is deductible at the IRS standard mileage rate. Log: date, from, to, miles, purpose,
  vehicle. **Three entry modes** (Found): a trip with GPS assist while the app is open, an
  odometer start/end, or a manual entry — background auto-detection is deliberately *not* the
  primary path because Android battery optimization kills it and trailheads have no signal.
  Named places ("home", "Boise office") and remembered routes fill in the rest (MileIQ). Rate table by year kept in the app (you enter the year's rate; I will
  not hard-code a number that changes annually).
- Trips can be tagged and linked to receipts (fuel, meals, campground) so a field-verification trip
  is one bundle at year end.

### 2.7 Contacts & vendors

- Your accountant, registered agent, attorney, bank contact, insurance agent, key vendors. Name,
  role, phone, email, account numbers (encrypted at rest), notes, and links to related documents
  and deadlines ("Idaho SOS annual report → registered agent info lives here").

### 2.8 Year-end package

One button, with a year selector, produces `RuggedRoute-2026-tax-package.zip`:

```
RuggedRoute-2026-tax-package/
├── 00-README.pdf               cover sheet: entity info, EIN, totals by Schedule C line, counts
├── 01-Expenses-by-category.xlsx one sheet per category + summary sheet + all-receipts sheet
├── 02-Income.xlsx               payouts / invoices with fees and net
├── 03-Mileage-log.xlsx          IRS-format log (date, purpose, from/to, miles) + total deduction
├── 04-Subscriptions.xlsx        recurring costs, annualized
├── receipts/
│   ├── 01-Advertising/2026-03-14_Google-Ads_45.00.jpg
│   ├── 07-Software-subscriptions/2026-01-05_Cloudflare_5.00.pdf
│   └── ...                       every receipt renamed to date_vendor_amount, sorted by category
├── documents/                    everything in the vault tagged with that tax year
└── filings/                      confirmations you attached to completed deadlines that year
```

Also available anytime, not just year end: quarterly versions of the same (for estimated-tax
math) and a "download everything" full export for backup.

### 2.9 Home screen = the exceptions inbox

The best tools in the research (Digits, Ramp, Puzzle) share one design: the home screen shows
**only things that need a decision**, and when it is empty it says so. HQ's home screen:

- **Capture** button, the biggest thing on the page.
- **Good-standing tile** (green / amber / red) with the next deadline and days remaining.
- **Exceptions list**, each with a one-tap action: receipts awaiting review · bank charges over the
  threshold with no receipt · possible duplicates · subscription price changes · documents expiring
  within 90 days · agency letters not yet actioned · deadlines due within 30 days · backup older
  than 36 h.
- **This month strip:** spent, income, tax set-aside, miles — small and out of the way.
- Everything else (charts, vendor breakdown, reports) lives one tap deeper.

### 2.10 Legal-safety checklist & record retention

You said the point is to keep yourself legally safe and never miss a deadline. Deadlines are §2.2;
this module covers the *rest* of staying safe — the things that, if neglected, let a plaintiff or
the IRS pierce your LLC's protection or disallow deductions.

- **Corporate-veil checklist**, reviewed by HQ once a year (a deadline like any other) and shown
  as a scorecard on the dashboard: separate business bank account and card (no commingling);
  signed operating agreement on file; contracts and accounts opened in the entity's name and
  signed with your title; annual report current; registered agent current; annual member
  resolution / minutes on file (a one-page template HQ generates and you sign); adequate
  insurance; business address consistent everywhere; EIN letter on file. Each item links to the
  document that proves it. Anything missing is red.
- **Record-retention rules baked in.** HQ never auto-deletes anything, but it knows the clocks:
  tax records and receipts **7 years** after the return they support (IRS says 3, 6 in some
  cases, 7 is the safe rule); employment-tax records 4 years; asset/equipment records until 3
  years after disposal; formation and governance documents **forever**; contracts 7 years after
  they end; insurance policies for as long as a claim could arise. Every file shows its
  "keep until" date and the reason. An "eligible to purge" report exists, but purging is always
  a deliberate manual act.
- **Evidence capture for disputes.** A "Save for later" button anywhere (receipt, email, document,
  note) files an item into an **Evidence** folder with a timestamp, source, and your note about
  why it matters (a customer threatening a chargeback, a vendor promise, a policy screenshot from
  Google Play). Immutable once saved; the audit log shows it was not altered.
- **Policy & terms versioning.** Your app's Terms of Service and Privacy Policy, each dated
  version kept with its effective date, so you can prove what users agreed to at any point.
- **Contract register.** Every agreement (vendor, contractor, customer) with parties, dates,
  renewal/termination terms, notice period, and a reminder before the notice window closes.

### 2.11 "Ask HQ" — the assistant

A chat box that answers from *your* records, not the internet: "When is my annual report due and
what did I file last year?", "How much did I pay Mapbox in 2026?", "Do I have my EIN letter?",
"Which contractors need a 1099?", "What is expiring in the next 90 days?". Under the hood it is
Claude with read-only tools over your database and vault (search receipts, search documents, list
deadlines, sum by category) so every answer cites the actual rows and files it used. It can also
draft things — a member resolution, a vendor cancellation email, a summary for your accountant —
into the vault for you to review. It never writes to records without you tapping confirm.
Every answer shows the data it used and which AI features are on (each is individually
toggleable — HoneyBook's trust pattern). The same tools are exposed as a **read-only MCP server**
so Claude Code or Claude.ai can query your books directly ("what did I spend on software last
year?") — Kick, Mercury, Digits, and Lili all shipped this in 2026 and it is how you and I will
work on the business together. Built in Phase 8; the tools it uses are the same queries the rest
of the app already has.

### 2.12 Things you did not mention but I recommend

- **Bank/card statement reconciliation** (now Phase 6, moved up after the research): upload a CSV
  from the bank, HQ matches lines to receipts and lists unmatched charges above the threshold →
  "you have 6 charges with no receipt." This is the single most effective way to make sure
  nothing is missing at year end.
- **Estimated-tax helper:** quarterly view of net profit → rough federal + Idaho estimate using
  rates you enter, with the four federal due dates already on the calendar (Idaho does not require
  individual estimates). Shows "you saved about $X on taxes" when you confirm a deductible receipt
  (Found/Keeper) — a small reward that keeps capture going. Not tax advice; a nudge.
- **Personal vs. business card flag** on receipts: if you sometimes pay with a personal card, HQ
  tracks "owed to me" so the reimbursement (or the capital contribution) is documented.
- **Audit trail:** every edit to a receipt/document is logged. If anyone ever asks "when did you
  record this", the answer exists.
- **Offline capture:** the phone app queues photos taken without signal (trailheads) and uploads
  when back online.

---

## 3. Architecture

```
┌──────────────────────────────── your phone / laptop ────────────────────────────────┐
│  hq.ruggedroutehq.com  — React + TypeScript PWA (installable, camera, offline queue) │
└───────────────┬────────────────────────────────────────────────────┬────────────────┘
                │ Supabase JS client (auth session, RLS-scoped)      │ Google OAuth (calendar scope)
                ▼                                                    ▼
┌──────────── Supabase project "rr-hq" (new, us-west) ───────────┐   Google Calendar API
│  Postgres 17  — all records, full-text search, pg_cron         │◄── "RuggedRoute Business" calendar
│  Auth         — Google sign-in, allowlist = your email only    │
│  Storage      — private bucket `vault` (receipts/, documents/) │
│  Edge Functions:                                                │
│    extract-receipt   → Claude API (vision) → JSON fields        │
│    sync-calendar     → creates/updates Google events            │
│    weekly-digest     → Monday email (Resend)                    │
│    build-package     → year-end ZIP → signed download URL       │
│    ingest-email      → receives forwarded receipts              │
│    nightly-backup    → DB dump + storage manifest → R2          │
└────────▲──────────────────────────────────────────────▲─────────┘
         │                                              │
  Cloudflare Email Routing                       Cloudflare R2 `rr-hq-backup`
  receipts@ruggedroutehq.com → Email Worker      (nightly, versioned, 90-day retention)
```

### Why this stack (and what I rejected)

| Choice | Why | Rejected alternative |
|---|---|---|
| **PWA first, not a native Android app** | One codebase, installs to home screen, camera + offline work fine in Chrome on Android, deploys in seconds, usable on laptop for the desk work (reviewing, year-end). | Native Kotlin app: 3–4× the effort for marginal gain. Can be added later as a thin wrapper (Capacitor) if you want push notifications beyond what Calendar gives. |
| **Supabase (Postgres + Auth + Storage + Edge Functions)** | I can build, migrate, and deploy it directly from this session via the connector; RLS makes single-user lock-down trivial; Postgres full-text search covers receipt/document search without another service; storage is S3-compatible so a backup is a copy. | Cloudflare D1 + R2 + Workers only: doable and consistent with dataops, but D1 lacks full-text search maturity and Auth would be hand-rolled. Firebase: NoSQL makes the year-end reporting queries painful. |
| **New Supabase project, not the existing app project** | Your business records should not sit behind the same anon key your public mobile app ships with. Separate project = separate keys, separate blast radius, separate backups. Free tier allows two projects. | Same project with a separate schema: cheaper conceptually but one leaked app key exposes both. |
| **Cloudflare Pages for hosting** | Already your account, free, custom domain on your zone, previews per branch. | Vercel/Netlify: another account for no benefit. |
| **Google Calendar as the reminder engine** | You asked for it explicitly, and it is genuinely the right call: reminders reach your phone/watch/desktop with zero extra infra, and you see business deadlines next to personal ones. | Web push notifications: fragile on Android PWAs, and you still want it on the calendar. Done as a later add-on if wanted. |
| **Claude API (`claude-sonnet-5`) for receipt extraction** | Vision + structured JSON output in one call, handles crumpled/angled photos, PDFs, and emails, and returns a category suggestion — no separate OCR service. At your volume (tens of receipts a month) cost is negligible. | Google Vision / Tesseract: text only, then you still need a model to structure it. |
| **Resend for the weekly email** | Free tier is far more than one email a week; a single verified sender on your domain. | Gmail API sending: works, but scopes are heavier than needed. |
| **Cloudflare Email Routing → Worker for the receipts inbox** | Zone is already on Cloudflare; free; the worker forwards the raw MIME to the ingest function. | Gmail label + polling: works too and is the fallback if Email Routing is not enabled on the zone. |

### Repository layout (new repo `riggs19991/ruggedroute-hq`)

```
ruggedroute-hq/
├── apps/web/                 React + Vite + TypeScript + Tailwind PWA
│   ├── src/features/         receipts/ deadlines/ vault/ subscriptions/ income/ mileage/ contacts/ package/
│   ├── src/lib/supabase.ts   typed client (types generated from the DB)
│   └── public/manifest.webmanifest, sw.ts (offline queue)
├── supabase/
│   ├── migrations/           every schema change, in order, in git
│   ├── functions/            extract-receipt/ sync-calendar/ weekly-digest/ build-package/ ingest-email/ nightly-backup/
│   └── seed/                 deadline library, categories, subscription templates
├── workers/email-ingest/     Cloudflare Email Worker (receipts@ → ingest-email)
├── .github/workflows/        ci.yml (typecheck, tests, migration dry-run), deploy.yml (Pages + functions)
└── docs/                     this plan (copied), runbook, decisions log
```

---

## 4. Compliance calendar — seed content (verified against official sources 2026-09-04)

Everything below is preloaded. The research pass checked each item against Idaho statute,
sos.idaho.gov, tax.idaho.gov, irs.gov, and fincen.gov; full citations are in the research doc
§2.2. Items marked ⚠ still depend on **your** entity type or city and need one confirmation from
you (or an accountant). Several assumptions from the first draft were **wrong and are corrected
here** — which is exactly why the app carries a *verify* flag and a source link on every rule.

### Idaho

| Deadline | When | Where | Notes |
|---|---|---|---|
| **Annual Report — Idaho Secretary of State** | Every year by the **last day of your formation anniversary month**; first one the year after formation | sosbiz.idaho.gov | **$0**, no late fee. SOS emails a reminder 1–2 months prior (no postcards). Missing it is grounds for administrative dissolution: SOS serves notice, you get **60 days** to cure; reinstatement within 10 years, **$30**. HQ computes the date from the formation date you enter and starts the "dissolution risk" countdown the day after. (Idaho Code §30-21-213, -601/-602/-603) |
| Assumed Business Name | **No renewal — Idaho ABNs no longer expire** | — | Shown as a *retired* rule with the reason. Only amendments/cancellation are tracked. |
| Idaho income tax return | **April 15** for all of: Form 40 (single-member LLC, Schedule C flow-through), Form 65 (multi-member LLC), Form 41S (S-corp) | tax.idaho.gov (TAP) | ⚠ Which form depends on your entity. Note Idaho's 65/41S date is a month *later* than the federal March 15. S-corps owe the **$20 minimum tax**. Extension is automatic if 80% of this year's or 100% of last year's tax is paid by April 15. |
| Idaho estimated payments | **Not required for individuals; no underpayment penalty.** C-corps only (Form 41ES, Apr/Jun/Sep/Dec 15 if liability ≥ $500) | TAP | Disabled unless entity = C-corp. The first draft had this wrong. |
| Idaho Permanent Building Fund tax ($10) | Only if the entity itself pays Idaho tax | with the return | ⚠ Off by default for a pass-through with no entity-level tax. |
| Idaho sales tax | **None for app subscriptions / SaaS** — electronically delivered software and digital subscriptions are not tangible personal property (§63-3616(b)); Google/Apple are marketplace facilitators elsewhere | — | Rule shown as *not applicable* with the citation. Turns on only if you start selling taxable goods (merch, printed maps). |
| Idaho withholding / unemployment insurance | Only with W-2 employees | TAP / Dept. of Labor | Off by default; turns on with the entity-type switch to "S-corp with payroll". |
| City license | **No general business license** in Boise, Meridian, Nampa, Idaho Falls, or Pocatello. Idaho Falls and Pocatello require a free **home-occupation permit**; Coeur d'Alene a home-occupation certificate | your city | ⚠ Tell me your city; HQ enables the matching card. |

### Federal

| Deadline | When | Notes |
|---|---|---|
| Quarterly estimated income tax (Form 1040-ES) | **Apr 15 · Jun 15 · Sep 15 · Jan 15** | HQ's estimated-tax helper pairs with these. |
| Annual federal return | **Mar 15** (1120-S / 1065) or **Apr 15** (Schedule C on 1040, or 1120) | ⚠ entity dependent. Extension (Form 7004 / 4868) reminder 14 days before. |
| Form 2553 (S-corp election) | Within 2 months + 15 days of the start of the year it should take effect | Only if you decide to elect; HQ surfaces it when you flip the entity switch. |
| 1099-NEC to contractors + IRS | **Jan 31** | **Threshold is now $2,000** per payee for payments made after Dec 31, 2025 (was $600), inflation-indexed from 2027. HQ's *Contract labor* category totals per payee and tells you who crosses it; collect W-9s into the vault. |
| Beneficial Ownership Information (FinCEN BOI) | **Retired** — FinCEN's Aug 11, 2026 final rule permanently exempts all U.S.-created entities | Kept as a retired rule with the citation so you know it was considered. |
| EIN | No renewal | Store the CP-575 letter in the vault; you will need it constantly. |
| Record retention (IRS Pub 583) | 3 yrs general · 6 if >25% income omitted · 7 bad debt · **4 yrs employment tax** · asset records until disposal-year limitations end | Drives the retention clocks in §2.10 (HQ uses 7 as the safe default). |

### Platform, vendor, and operational

| Deadline | Cadence | Notes |
|---|---|---|
| Google Play developer account — policy/declaration updates, target API level deadlines (typically **Aug 31** each year), data-safety form | Annual + ad hoc | Missing the target-SDK deadline blocks app updates. |
| Apple Developer Program renewal | Annual, $99 | Only when/if iOS ships. |
| Domain renewals (`ruggedroutehq.com` + any others) | Annual | Enter registrar; reminder 30 days out. |
| Business insurance (general liability / E&O) renewal | Annual | ⚠ if you carry it. |
| Cloudflare / Mapbox / Supabase billing review | Monthly | Auto-satisfied when the receipt arrives; flagged if it does not or if the amount drifts. |
| Trademark (if filed): Section 8 & 15 declarations at years 5–6, renewal at year 10 | Multi-year | ⚠ only if registered. |
| Vehicle registration (if business vehicle) | Annual | Optional. |
| Annual member resolution / minutes | Annual, same month as the annual report | Template → PDF → vault (§2.10). |
| Backup restore test | Quarterly | HQ reminder to actually open the backup and confirm it restores. |
| Idaho SOS status check | Quarterly | Deep link to your SOSBiz entity page; SOSBiz has no API so this stays a 30-second manual check. |

## 5. Data model

Postgres, one schema `hq`. All tables carry `id uuid`, `created_at`, `updated_at`, `owner uuid`
(= your auth user id) with RLS `owner = auth.uid()` on every table. `deleted_at` soft-delete on
user-facing tables so "undo" is always possible.

```
business_profile   legal_name, dba, entity_type, state, formation_date, ein (encrypted),
                   fiscal_year_end, timezone, address, registered_agent → contact
categories         name, schedule_c_line, deductible_pct (100 / 50), sort, active
transactions       account_id, posted_on, amount, description_raw, merchant_normalized, receipt_id?,
                   category_id?, status (unmatched|matched|exempt|personal), import_batch_id
accounts           name, kind (checking|card|savings), last4, csv_profile jsonb
receipts           file_id, vendor_id?, transaction_id?, date, subtotal, tax, tip, total, currency, payment_method,
                   last4, category_id, status (needs_review|confirmed|reconciled|void),
                   paid_personally bool, notes, tags text[], extracted jsonb (raw model output),
                   extracted_text (tsvector), subscription_id?, trip_id?, source (camera|upload|email),
                   field_confidence jsonb, verified_fields text[]   (AI-set until you confirm)
receipt_line_items receipt_id, description, qty, amount
files              storage_path, bucket, mime, bytes, sha256 (dedupe), width/height, page_count,
                   ocr_text, uploaded_via
vendors            name, normalized_name, default_category_id, website, notes, contact_id?,
                   receipt_exempt bool, expected_min, expected_max
vendor_aliases     vendor_id, alias_pattern   ("AMZN Mktp*" → Amazon)
vendor_rules       vendor_id, category_id, business_pct, created_from_receipt_id
agencies           name (Idaho SOS | Idaho STC | IRS | city), account_ids jsonb (encrypted), login_url,
                   contact_id?, notes
documents          title, doc_type (formation|tax|legal|insurance|license|banking|vendor|statement|agency_letter|other),
                   file_id, version, supersedes_id?, effective_date, expires_at, tax_year?,
                   deadline_occurrence_id? (a filing confirmation), tags, text (tsvector),
                   custom_fields jsonb (typed: money/date/url/select/doc_link), ai_summary,
                   ai_set_fields text[]
document_links     from_document_id, to_document_id, relation   (reverse link is implicit)
share_links        target (document|bundle|package), target_id, expires_at, password_hash?,
                   access_log jsonb
deadline_rules     title, agency_id, url, description, consequence, playbook (what to do if missed),
                   applies_to text[] (llc|smllc|scorp|ccorp|sole), retired_on?, retired_reason?,
                   source_url, schedule jsonb
                   ({kind: fixed_md|anniversary_month_end|days_after_fye|custom_rrule, ...}),
                   reminder_offsets int[] (days, default {90,30,7,1}), verify_required bool, enabled bool
deadline_occurrences rule_id, due_on, status (upcoming|done|skipped|overdue), completed_at,
                   google_event_id, google_calendar_id, notes
subscriptions      vendor_id, name, amount, cadence (monthly|annual|quarterly|usage),
                   next_renewal, payment_method, cancel_by, url, notes, active
income_entries     source (google_play|stripe|invoice|other), period_start, period_end,
                   gross, platform_fee, withholding_tax, refunds, fx_adjustment, net, received_on,
                   transaction_id? (the deposit), file_id?, notes, import_batch_id?
tax_setaside       year, pct, federal_rate, idaho_rate, se_rate   (you enter; HQ computes)
invoices           number, client_contact_id, issued_on, due_on, line_items jsonb, total,
                   status (draft|sent|paid|overdue), pdf_file_id
trips              date, from_place, to_place, miles, purpose, vehicle, start_ll?, end_ll?,
                   rate_year, tags
mileage_rates      year, cents_per_mile   (you enter the year's IRS rate)
contacts           name, role, company, phone, email, address, notes, secrets jsonb (encrypted)
tax_years          year, status (open|packaged|filed), package_file_id, packaged_at
retention_rules    doc_type/category, keep_years, basis (irs|governance|contract|insurance), note
evidence_items     title, why, source_type, source_id?, file_id?, immutable bool, saved_at
checklist_items    key, title, proof_document_id?, status (ok|missing|expired), last_reviewed
contracts          title, counterparty_contact_id, file_id, starts_on, ends_on, auto_renews,
                   notice_days, termination_terms, reminder_occurrence_id?
audit_log          table, row_id, action, diff jsonb, at
settings           key, value jsonb  (digest on/off, calendar id, reminder defaults, tz)
```

Storage layout: `vault/receipts/{yyyy}/{mm}/{uuid}.{ext}` and `vault/documents/{doc_type}/{uuid}.{ext}`.
Bucket is private; the app reads via short-lived signed URLs only.

---

## 6. Key flows in detail

### 6.1 Receipt capture → extraction → confirm

1. Tap **Capture** (home screen icon opens directly here). Rear camera. Snap; optional second page.
2. Client compresses to ≤ 2 MB, computes SHA-256, uploads to Storage. If offline, the file and a
   pending row are queued in IndexedDB and uploaded when connectivity returns.
3. Insert `receipts` row with `status = needs_review`, `source = camera`. A database trigger enqueues
   an extraction job; the `extract-receipt` Edge Function picks it up.
4. Edge Function sends the image (or first PDF page rendered to PNG) to Claude with a strict JSON
   schema: `{vendor, date, subtotal, tax, total, currency, payment_method, last4, line_items[],
   suggested_category, confidence}`. It also asks for the full transcribed text (stored for
   search). Vendor is matched against `vendors` by normalized name; if that vendor has a default
   category it overrides the model's suggestion.
5. The receipt row is updated; the phone shows a pre-filled form. Anything with
   `confidence < 0.7` is highlighted. You fix or accept, tap **Save** → `confirmed`.
6. Dedupe check before save: same vendor + total within ±3 days, or identical SHA-256 → warning.

Time budget: capture ≤ 10 s of your attention; extraction runs in the background (~5 s).

### 6.2 Email receipts

`receipts@ruggedroutehq.com` → Cloudflare Email Worker → POST raw MIME to `ingest-email` (shared
secret). The function: verifies the sender is you or an allow-listed vendor domain, extracts PDF
attachments (each becomes a receipt) or, if none, renders the HTML body to PDF and treats that as
the receipt, then runs the same extraction as 6.1. You get a "3 receipts arrived by email, 2 need
review" line on the dashboard. You can also **forward** any email receipt from Gmail to that
address, which is the everyday path.

### 6.3 Deadline rule → occurrences → Google Calendar

- Nightly `pg_cron` job materializes occurrences for every enabled rule out to 24 months, marks
  overdue ones, and enqueues calendar sync for anything new/changed.
- `sync-calendar` uses the refresh token from your Google sign-in (calendar scope requested at
  first login; you can revoke anytime) to upsert events on the "RuggedRoute Business" calendar
  (created on first run; id stored in `settings`). Event: all-day on `due_on`, description with the
  filing link + consequence + "mark done in HQ" link, reminders at each `reminder_offset` (popup)
  plus email at the largest offset. Timezone from `business_profile.timezone`.
- Marking done in HQ → event retitled with ✓ and reminders removed. Skipping → event deleted.
- Deleting the calendar in Google → HQ notices on next sync (404s), recreates, and logs it.

### 6.4 Year-end package

`build-package` Edge Function, for a given year: queries everything, writes XLSX (via a small JS
lib) and the cover PDF, streams a ZIP into Storage under `packages/`, records it in `tax_years`,
returns a signed URL that lasts 7 days. Re-runnable; each run is versioned. Large receipt sets are
fine (streams, does not hold everything in memory).

### 6.5 Backups

Nightly GitHub Action in the `ruggedroute-hq` repo (same pattern as dataops): `pg_dump` the `hq`
schema, list + copy any Storage objects newer than the last manifest, upload both to
R2 `rr-hq-backup/{yyyy-mm-dd}/`. Keep 90 daily, 24 monthly. The export is a **human-browsable
folder** — `receipts/2026/03/2026-03-14_Google-Ads_45.00.jpg`, originals untouched, plus a JSON
manifest of all metadata (Paperless-ngx's exporter pattern) — so it is useful even if HQ itself
never runs again. That is the Bench lesson: no proprietary ledger without a full export. A restore runbook lives in `docs/`
and a quarterly deadline reminds you to test it. "Download everything" in the UI is the same
artifact, on demand.

---

## 7. Security & privacy

- **Auth:** Supabase Auth, Google provider, `authorize` hook rejects any email other than yours.
  Sessions expire in 7 days on desktop, 30 on the installed PWA.
- **RLS on every table**, `owner = auth.uid()`. Service-role key exists only inside Edge Functions
  and the backup action; never in the browser.
- **Storage bucket private**; signed URLs valid for 10 minutes; no public objects, ever.
- **Secrets at rest:** EIN, account numbers, and contact `secrets` are encrypted with `pgsodium`
  (key held by Supabase, not in the DB), shown masked with a reveal button.
- **Claude API:** receipt images are sent for extraction and are not used for training under API
  terms; no personal financial data beyond what is on the receipt is sent. Toggle exists to turn
  extraction off (manual entry only) if you ever prefer.
- **Audit log** on receipts, documents, deadlines, and settings.
- **Repo hygiene:** no secrets committed; `.env.example` only; CI blocks a push containing a key
  pattern (same secret-scan you get from GitHub).

---

## 8. Build phases

Each phase ends with something deployed at `hq.ruggedroutehq.com` that you can use that day. Effort
is in **working sessions** (one session ≈ one focused build-and-deploy pass with me).

| Phase | Deliverable | Sessions | What I need from you |
|---|---|---|---|
| **0 — Decisions & setup** | Answers to §10; new Supabase project `rr-hq`; new GitHub repo; Cloudflare Pages project + `hq.` DNS; Google OAuth client; Claude API key; Resend sender | ½ | Answers to §10, approve creating the Supabase project + repo, paste 3 keys into repo/Supabase secrets |
| **1 — Foundation** | Repo scaffold, CI, schema migration for all tables, RLS, Google sign-in with allowlist, installable PWA shell, dashboard skeleton, business profile form | 1 | Sign in once to verify |
| **2 — Receipts** | Camera/upload/PDF capture, extraction with per-field confidence, review form, vendor rules + aliases, receipt-required threshold, list/search/filter, ±5-day dedupe, categories seeded | 1–2 | Photograph ~10 real receipts so the extraction prompt is tuned on your actual vendors |
| **3 — Deadlines + Calendar** | Verified deadline library (§4) with source links and playbooks, rule engine with entity-type switch, 90/30/7/1 ladder, Google Calendar sync, good-standing tile, jurisdiction cards, mark-done with attachment, custom deadlines | 1 | Formation date / entity type / city; confirm the calendar appears on your phone |
| **4 — Document vault** | Inbox-first upload with AI triage, folders, versions, typed custom fields + document links, expirations → reminders, agency letters → tasks, full-text search, expiring share links | 1 | Upload your formation docs + EIN letter |
| **5 — Subscriptions + Income + Mileage** | Recurring costs with expected ranges and variance alerts, income ledger with **Google Play payout parser**, tax set-aside, trip log (three entry modes), rate table | 1 | Your subscription list; a Google Play earnings CSV |
| **6 — Transactions + Year-end package** | Statement CSV import, 2-of-3 matcher, "charges with no receipt" exceptions, then the ZIP/XLSX/PDF builder, tax-year states, quarterly variant, accountant share link | 1–2 | A bank/card statement CSV; how your accountant likes to receive things (or if you self-file) |
| **7 — Email ingestion + weekly digest + backups** | `receipts@` inbox, Monday digest, nightly R2 backup + restore runbook | 1 | Enable Email Routing on the zone (one dashboard click) |
| **8 — Legal-safety + Ask HQ + extras** | Veil checklist scorecard, retention clocks, evidence folder, contract register, annual-resolution template → PDF, "Ask HQ" assistant with citations + read-only MCP server, per-feature AI toggles, estimated-tax helper with "you saved $X", vendor trend report, offline queue hardening, audit log UI, invoices (optional) | 2 | Use it for a month and tell me what annoys you |

Rough total: **10–12 sessions.** Phases 1–3 alone (three sessions) already give you receipts +
the Idaho/IRS calendar on your phone, which is the part you are most worried about.

Sequencing rationale: receipts before deadlines because receipts are daily and deadlines are
monthly; deadlines before the vault because the annual report has a hard date and documents do
not; year-end before email ingestion because the package proves the data model is right, and
email ingestion is a convenience on top.

---

## 9. Running cost

| Item | Tier | Monthly |
|---|---|---|
| Supabase (2nd project) | Free (500 MB DB, 1 GB storage, 500K function calls) — upgrade to Pro ($25) only if receipts exceed ~1 GB, which is years away at phone-compressed sizes | $0 |
| Cloudflare Pages + Email Routing + R2 backup | Free tiers (R2 10 GB free) | $0 |
| Claude API extraction | Pay-per-use; tens of receipts a month is well under a dollar | ≈ $0–1 |
| Resend | Free (3,000 emails/mo) | $0 |
| Domain | Already owned | $0 |

---

## 10. Decisions I need from you (with the default I will use if you just say "go")

1. **Entity type and formation month.** LLC / S-corp / sole prop, and the month/year Idaho SOS
   shows as your organization date. *Default: the app asks you on first login; the annual-report
   date stays "unset" until then.*
2. **PWA first, native Android later if wanted.** *Default: yes.*
3. **New Supabase project `rr-hq` in your Rugged Route org (free tier).** *Default: yes, I create
   it (I will ask for the confirm since it is a billable-capable action even at $0).*
4. **New repo `riggs19991/ruggedroute-hq`.** *Default: yes; this plan is copied there.*
5. **Hostname `hq.ruggedroutehq.com`.** *Default: yes.*
6. **Receipts inbox `receipts@ruggedroutehq.com` via Cloudflare Email Routing.** *Default: yes,
   with Gmail-forwarding as fallback if Email Routing is not enabled on the zone.*
7. **Timezone America/Boise** for all deadlines. *Default: yes.*
8. **Categories:** Schedule C mapping as listed in §2.1. *Default: yes; editable later.*
9. **Weekly Monday digest email** on. *Default: yes.*
10. **Do you have an accountant** who should get the year-end package, and do they use anything
    specific (QuickBooks, Xero)? If so, I add a QuickBooks-compatible CSV export. *Default: generic
    XLSX only.*
11. **Which city** you operate from (for the home-occupation permit card) and **which bank/card**
    you use for the business (so the statement CSV importer is built against its real format).
    *Default: no city card; generic CSV importer.*
12. **Receipt-required threshold.** *Default: $25.*

---

## 11. What happens next

Reply with "go" (plus any changes to §10) and the next session is Phase 0 + Phase 1: I create the
Supabase project and repo, lay down the schema and auth, and deploy the empty shell to
`hq.ruggedroutehq.com` so you can install it on your phone the same day. Phase 2 (receipts) follows
immediately after, and I will ask you for a handful of real receipts to tune extraction against.

This plan is a living document. It moves to `ruggedroute-hq/docs/plans/` when that repo exists and
every deviation gets a dated note in `docs/decisions.md`.
