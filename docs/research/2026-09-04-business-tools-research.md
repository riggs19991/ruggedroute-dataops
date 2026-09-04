# Research: what existing business-organization tools do well (2025–2026)

**Date:** 2026-09-04 · **Purpose:** steal the best ideas for RuggedRoute HQ
(`docs/plans/2026-09-04-business-ops-tool-plan.md`) · **Method:** four parallel sweeps over
vendor docs, release notes, official Idaho/IRS sources, and independent reviews. ~50 tools.

Sections: 1 receipts & expenses · 2 compliance & deadlines (with **verified Idaho/federal
obligations**) · 3 document vaults · 4 all-in-one "business OS" and AI bookkeeping ·
5 what we adopt · 6 what we deliberately skip.

---

## 1. Receipt capture & expense tracking

| Tool | Standout ideas |
|---|---|
| **Expensify** | Text a photo to a short code and it auto-matches the card charge. Batch back-to-back photos. Auto-merge only when amount matches, dates align, exactly one candidate, card posts within 7 days. "Potential duplicate" banner on *both* records (same day + amount). Workspace rule: **receipt required above $X** (e.g. $25), with exemptions for mileage. Category memory learns from your choices. |
| **Dext** | Capture via email, WhatsApp, clipboard paste, share sheet. **Supplier Rules** (default category/tax per vendor) and **Supplier Name Aliases** ("AMZN Mktp" = "Amazon", confirmed once during review). Line-item extraction with per-line category. Duplicates: contact + date + value within a configurable **±5-day window**, shown as an amber icon, never silently deleted. Pipeline states Inbox → Processing → To Review → Ready → Archive. |
| **Shoeboxed** | Human verification queue behind OCR. Positions scans as IRS-accepted. Mail-in envelope (not worth copying). |
| **Ramp** | SMS after every card swipe; reply with a photo, and **any text in the reply becomes the memo**. Gmail/Amazon/Lyft/Uber auto-receipts. Automation level rises as you accept suggestions and falls when you edit. "Missing items" section with bulk upload. **Auto-approved merchants** exempt from receipt requirements, one-click "dismiss and exempt this merchant". Missing-receipt affidavits stored permanently. |
| **Brex** | Receipt verified if **2 of 3** (date, amount, merchant) match; only receipts under 2 months old; otherwise "failed verification" and it waits in a wallet. Gmail add-on flags emails by keywords (payment, receipt, invoice, order). Auto-generated virtual receipts for Amazon/airlines. |
| **Keeper** | No receipts at all; bank feed is the source of truth, scanned 18 months back against a "tax profile". Suggests write-offs, you tap to confirm, then "create a rule for this?". Running **tax-savings counter**. |
| **Hurdlr / Everlance / MileIQ** | Auto GPS trips; **swipe right = business, left = personal**; "Speed Tagging" multi-select; **Frequent Drives** learns start/end pairs and auto-classifies; Work Hours auto-classify; Named Locations. Reviewers report missed segments and battery-optimization kills on Android. |
| **Found / Lili** | After you categorize: **"make this a rule?"**. Auto-sweep a % of each deposit into a Taxes pocket. Push notification showing **"you saved $X on taxes"** per categorized purchase. Lili generates a **pre-filled Schedule C PDF**. Three mileage entry modes (trip, odometer, annual estimate). |
| **Wave** | Auto-merge receipt with bank line only when exactly one candidate; refuses to guess when several match. |
| **QuickBooks Solopreneur** | Swipe queue with the AI's category guess in a banner; 19 categories each mapped to a Schedule C line; flags purchases over $2,500 as possible assets (de minimis rule); Tax Summary / Tax Details reports. |
| **Zoho Expense** | First expense from a new merchant is manual, subsequent ones auto-categorize. Statuses "scan-in-progress" / "scan-failed". Card match on exact amount within ±3 days. Scheduled "unreported expenses" reminders. |
| **AI-first newcomers** (SparkReceipt, Receiptor AI, ExpenseBot, Kick, Finny) | LLM extraction in 2–3 s; **overnight retroactive Gmail scan**; "AI assists, human confirms" with every field labeled editable before save. Reviewers: LLMs read crumpled receipts far better than OCR but can **hallucinate totals**, so cross-check against the bank amount. |

Sources: Expensify product updates Jul/May 2025 and help center; Dext release logs and duplicate
handling article; Ramp support "receipts and memos", "excluding merchants"; Brex "receipts for
expenses"; Keeper write-off detection; MileIQ intelligence features; Found bookkeeping guide;
Lili Schedule C help; Wave receipts help; QuickBooks Solopreneur category help; Zoho Expense
autoscan; SparkReceipt, Receiptor AI, ExpenseBot, Finny 2026 roundups.

## 2. Compliance & deadline tools — and the verified Idaho/federal rules

### 2.1 Tools

| Tool | Standout ideas |
|---|---|
| **ZenBusiness** Worry-Free Compliance ($199/yr) | **Compliance scorecard** ("status at a glance"), calendar with direct action links, guided **Meeting Minutes Manager** that produces a minutes document even for LLCs. |
| **LegalZoom** Compliance Calendar ($199/yr) | Up to **five reminders per filing** via email + SMS; SOS status monitoring; AI-generated meeting minutes from notes; free public compliance-check lookup. |
| **Northwest Registered Agent** | Reminder **≥90 days** before due, then they file; Idaho page confirms $0 fee, 60-day dissolution window, $30 reinstatement. |
| **Harbor Compliance** | Rules DB auto-sets due dates; **integrates with SOS databases** to verify status rather than trusting self-report; unified calendar with printable reports. |
| **Firstbase Agent** | **Jurisdiction cards**: one card per state/agency showing requirements, deadlines, action button; mailroom digitizes physical agency mail into the same dashboard. |
| **Mosey** (acquired by Gusto, Apr 2026) | Rules engine generates the calendar; stores agency credentials for one-click login; registered-agent mail in browser with agency-letter alerts. |
| **Rippling Compliance 360** | Every flagged infraction comes with a **recommended plan of action**. |
| **Clerky / Carta** | Corporate records as **workflows**: templated consents/resolutions linked to the decision they approve, e-signed, permanently stored; 83(b) reminders. |
| **Stripe Atlas** | Just a "key tax dates" page and reminder emails; does not file for you. |

### 2.2 Verified obligations for an Idaho LLC (official sources, checked 2026-09-04)

These **correct** several assumptions in the first draft of the plan.

| Obligation | Rule | Fee | Source | Confidence |
|---|---|---|---|---|
| **Idaho annual report** | Due by the **last day of the anniversary month** of formation, every year; first one the year after formation. SOS emails a reminder 1–2 months prior. | **$0** online (SOSBiz). No late fee. | Idaho Code §30-21-213; sos.idaho.gov FAQ | High |
| Missed report → administrative dissolution | Grounds on the missed due date; SOS serves notice and you have **60 days** to cure. Reinstate within **10 years**. | $30 reinstatement | §30-21-601/602/603; sos.idaho.gov forms | High |
| Assumed Business Name (DBA) | **No renewal — ABNs no longer expire.** (The old 5-year rule is gone.) Track amendments only. | — | sos.idaho.gov ABN FAQ | High |
| Idaho income tax, single-member LLC | Schedule C flows to the owner's **Form 40**, due **April 15**. | — | tax.idaho.gov | High |
| Idaho income tax, multi-member LLC / S-corp | **Form 65 / Form 41S**, due 15th day of the 4th month = **April 15** (a month *later* than the federal 1065/1120-S on March 15). Rate 5.3%. S-corp owes the **$20 minimum tax**. Optional pass-through-entity (ABE) election. | $20 (41S) | tax.idaho.gov S-corp & partnership guides; Form 41S instructions | High |
| Idaho estimated payments, individual | **Not required; no underpayment penalty.** Form 51 is voluntary. | — | tax.idaho.gov | High |
| Idaho estimated payments, C-corp only | Form 41ES if Idaho liability ≥ $500: Apr/Jun/Sep/**Dec** 15. | — | Form 41EST instructions | High |
| Idaho Permanent Building Fund tax | $10, but for S-corps/partnerships **only if the entity itself pays tax** (built-in gains, composite return). Resident-owned pass-through with no entity-level tax owes none. | $10 | Form 41S instructions | High |
| Idaho sales tax on app subscriptions / SaaS | **Not taxable**: remotely accessed or electronically delivered software and digital subscriptions are not tangible personal property (§63-3616(b)). Google/Apple are marketplace facilitators for states that do tax them. **No Idaho seller's permit needed** unless you sell taxable goods. | — | Idaho Code §63-3616; tax.idaho.gov online sellers guide | High |
| Federal estimated tax (1040-ES) | Apr 15 · Jun 15 · Sep 15 · Jan 15 | — | IRS Pub 509 | High |
| Federal return | Mar 15 (1120-S / 1065) · Apr 15 (1040 with Schedule C, 1120) | — | Pub 509 | High |
| Form 2553 (S-corp election) | Within 2 months + 15 days of the start of the tax year it should take effect | — | Pub 509 | High |
| **1099-NEC** | Furnish + file by **Jan 31**. **Threshold rises from $600 to $2,000 for payments made after Dec 31, 2025** (One Big Beautiful Bill Act §70432–33), inflation-indexed from 2027. | — | OBBBA; Pub 509 | High |
| FinCEN Beneficial Ownership (BOI) | **Permanently eliminated for all U.S.-created entities** by FinCEN final rule of Aug 11, 2026 (effective Aug 14). Remove from the app; keep a "retired" note. | — | fincen.gov/boi | High |
| City business license | **No state general license.** Boise, Meridian, Nampa, Idaho Falls, Pocatello: **no general city license** (activity-specific only). Idaho Falls and Pocatello require a free **home-occupation permit** for home-based businesses; Coeur d'Alene requires a home-occupation certificate (verify by phone). | $0 | city sites | High (CdA medium) |
| IRS record retention (Pub 583) | 3 years general · 6 if >25% of income omitted · 7 for bad debt/worthless securities · **4 years employment tax** · asset records until the limitations period of the disposal year ends · unlimited if no return/fraud | — | IRS Pub 583 | High |

## 3. Document vaults

| Tool | Standout ideas |
|---|---|
| **Paperless-ngx** (open source, the reference design) | Consumption folder; IMAP mail rules tracked by message UID so nothing is ingested twice; correspondent / document type / storage path / nested tags; **typed custom fields** (monetary with currency, date, URL, select, **document-link with automatic reverse link**); **scheduled workflows** that fire "N days before a date field" (e.g. 30 days before `expires`); document versions; audit log on by default; 30-day trash; expiring public share links and ZIP bundles; **exporter writes originals + JSON manifest in a browsable folder with templated filenames**; built-in "chat with your archive". Saved views on the dashboard act as labeled binders. |
| **Paperless-GPT / Paperless-AI** | Tag a document `-auto` to run hands-off AI titling/tagging, or a review tag to see suggestions first. Editable prompt templates; blacklist correspondents from ever being sent to an LLM. |
| **Papra** (2025) | Per-org **generated intake email address**; MIME sniffing by magic bytes for mislabeled attachments; share links with expiry + password; roadmap "document request links" for external upload. |
| **Docspell** | **Due-items task**: a saved query + reminder days on a schedule, with a preview of the next run times. Password-protected share links. |
| **Mayan EDMS** | Auto-generated hierarchical indexes (year/month) from metadata without moving files; smart links (rule-based cross-references); retention via workflow state expiration. |
| **M-Files** | Every AI-set metadata value is **flagged as AI-set until a human confirms it**. |
| **Box Extract / Juro** | Extracted fields carry a **confidence score and a highlight of the source snippet** on the page. |
| **Google Drive (2026)** | Sharing expirations that revert to parent permission; "Organize My Files" suggestions; Gemini semantic search with citations. |
| **Trustworthy / Everplans / 1Password** | **Inbox-first**: everything lands unsorted, AI proposes title/type/dates/one-line summary, you approve. Expiring "SecureLinks" (1h/1d/1w/1mo). Expiry date on any item with reminders. Deputy access tiers. |
| **Corporate records book** best practice | Tabs: charter/articles + amendments, bylaws/operating agreement, organizational consent, minutes/consents chronologically, ownership ledger, EIN/qualification, annual reports. Every material action traces to a consent; an annual calendar (annual report, approve financials). |

## 4. All-in-one "business OS" and AI bookkeeping

| Tool | Standout ideas |
|---|---|
| **HoneyBook** | Every morning an AI **daily action plan**; each AI feature individually toggleable; UI **shows the data sources behind each AI output**. (Also: 89% price hike, surprise card surcharge — reviewers furious.) |
| **Moxie** | **Monday-morning digest** you can interrogate with follow-up questions; "conversational configuration" (describe an invoice in prose, it builds it). |
| **Digits** | Home screen is a **checklist of open items / inbox of exceptions** (anomalies, duplicates, needs-review) so you review exceptions, not every transaction. Exposes an MCP server. |
| **Puzzle** | **User-defined variance thresholds** ("flag any vendor >20% above its 3-month average") → directly yields "this subscription price went up". Governed automation: AI drafts, human approves. Reviewers: hard to override wrong AI categorizations — avoid that. |
| **Kick** | Monthly **vendor breakdown to cut unnecessary spend**; deduction discovery; visual rule builder; MCP read-write for Claude. |
| **Jupid** | Bookkeeper that lives in WhatsApp/iMessage: asks **one-tap clarifying questions** on ambiguous transactions, persistent vendor memory, every transaction mapped to a Schedule C line, MCP server for terminal queries. |
| **Xero JAX** (Sept 2025) | Predicts when each customer will actually pay and times reminders to it; "JAX Assure" hallucination guardrail; plain-English report generation. |
| **Intuit / QuickBooks** | Feb 2026 Anthropic partnership exposes invoicing/tax-estimate tools via MCP inside Claude. Solopreneur: real-time quarterly estimate from a "tax profile". Complaints: chat capped at 25 questions/month. |
| **Mercury** (Mar 2026) | Insights dashboard with AI alerts; **read-only MCP** with OAuth and 24-hour tokens; invoice reminders at −7/−1/+1/+7 days; missing-receipt SMS where you reply with a photo. |
| **Relay** | Profit First: **percentage auto-transfer rules on every deposit** into named sub-accounts. |
| **Found / Lettuce** | Auto-sweep a % of every deposit into Taxes; dashboard shows "what's already spoken for and what's yours to keep". |
| **Bench** (collapsed Dec 2024) | Shut down with no notice, users locked out of their own books. **Lesson: never a proprietary ledger without a full export.** |
| **Firefly III** (open source) | Best data model for recurring costs: **Bills/Subscriptions objects with expected amount ranges and next-due prediction**; rule engine; recurring transactions. |
| **Google Play payouts** | No mainstream tool ingests Play payouts cleanly. Stripe Revenue Recognition has a daily Play connector (but ignores withholding and commission); RevenueCat has scheduled exports + webhooks; Play Console monthly earnings CSV (fee-description column format changes July 2026). This is a gap worth owning. |
| **MCP everywhere** | Kick, Mercury, Bonsai, Lili, Twenty CRM, Docmost all shipped MCP servers in 2026. Exposing your own data to Claude is now table stakes. |

## 5. What we adopt (ranked by value ÷ effort)

| # | Idea | From | Lands in HQ as | Effort |
|---|---|---|---|---|
| 1 | **Exceptions inbox as the home screen** — only things needing a decision | Digits, Ramp "missing items", Dext pipeline | Dashboard §2.9 rewritten | Easy |
| 2 | **Transactions as first-class records; receipts attach to transactions** — statement CSV import first, live bank feed optional later | Keeper, Found, Kick, Wave | New `transactions` table; reconciliation moves from Phase 8 to Phase 6 | Medium |
| 3 | **Deterministic matcher, 2-of-3 rule, refuse to guess on multiple candidates** | Brex, Expensify, Wave | Receipt→transaction matching spec | Easy |
| 4 | **Duplicate flag with ±5-day window, shown on both records, never auto-delete** | Dext, Expensify | Receipts §2.1 (replaces ±3-day rule) | Easy |
| 5 | **"Make this a rule?" + vendor aliases + first-time-manual-then-auto** | Found, Dext, Zoho | `vendor_rules`, `vendor_aliases` | Easy |
| 6 | **Receipt-required-above-$X and exempt merchants; "dismiss and exempt"** | Expensify, Ramp | Settings + rule | Easy |
| 7 | **Per-field confidence, AI-set flag until human-confirmed, cross-check total against bank line** | Finny, M-Files, Box, Juro | Extraction UI; `verified_fields` | Easy–Medium |
| 8 | **Rule-driven date engine + reminder ladder 90/30/7/1 with roll-forward for weekends/holidays** | Mosey, Harbor, Northwest, LegalZoom | Deadline engine §6.3 | Easy |
| 9 | **Good-standing tile + days-until-dissolution countdown + missed-deadline playbook** | ZenBusiness, Rippling, Northwest | Dashboard + deadline rules (`playbook` field) | Easy |
| 10 | **Jurisdiction cards** (SOS, Tax Commission, IRS, city): account IDs, login link, next due, last filed | Firstbase, Mosey | New `agencies` table; Contacts module | Easy |
| 11 | **Entity-type switch swaps the rule set**; **sunset flags** for retired rules (BOI, ABN renewal) | Mosey, research findings | Deadline rules `applies_to`, `retired_on` | Easy |
| 12 | **Records-as-workflows**: annual minutes/resolution template → PDF → stored, linked to what it approves | Clerky, Carta, ZenBusiness | Legal-safety §2.10 | Medium |
| 13 | **Scheduled date-field workflows + due-items digest with next-run preview** | Paperless-ngx, Docspell | Vault expirations; weekly digest | Easy |
| 14 | **Typed custom fields incl. document-link with reverse link** | Paperless-ngx | Vault data model | Easy |
| 15 | **Export = browsable folder + templated filenames + JSON manifest, originals untouched** | Paperless exporter, Bench lesson | Backups §6.5, year-end package | Easy |
| 16 | **Expiring, password-protected share links and bundles for the accountant** | Paperless, Box, Trustworthy | Vault + year-end package | Easy |
| 17 | **Subscription objects with expected-amount ranges + variance thresholds** ("vendor >20% above 3-mo avg") | Firefly III, Puzzle | Subscriptions §2.4 | Easy |
| 18 | **Google Play payout parser** (gross / fees / withholding / refunds / FX → reconcile to deposit) | gap in market | Income §2.5 | Medium |
| 19 | **Tax set-aside % per deposit + live estimate + "you saved $X" feedback** | Found, Relay, Lettuce, Keeper | Estimated-tax helper | Easy |
| 20 | **Queryable Monday digest** and one-tap clarifying questions | Moxie, HoneyBook, Jupid | Weekly digest + Ask HQ | Medium |
| 21 | **Per-feature AI toggles + show the data sources behind each AI answer** | HoneyBook | Settings; Ask HQ citations | Easy |
| 22 | **MCP server over HQ** (read-only token) so Claude Code / Claude.ai can query your books | Kick, Mercury, Digits, Lili | Phase 8 | Easy–Medium |
| 23 | **Agency mail inbox**: scan a letter, tag the agency, spawn a task | Mosey, Firstbase | Vault doc type `agency_letter` | Easy |
| 24 | **Monthly vendor breakdown with trend arrows** | Kick, Pilot | Reports | Easy |
| 25 | **Mileage: three entry modes (trip, odometer, annual estimate); GPS assist optional, never required** | Found, MileIQ complaints | Mileage §2.6 | Easy |

## 6. What we deliberately skip

- **Background GPS auto-trip detection** as the primary mileage path (Android battery optimization kills it; remote areas have no signal). Manual/odometer/GPS-assisted-when-open instead.
- **SMS/WhatsApp reply-with-photo** (Ramp, Mercury, Jupid). Nice, but needs Twilio and a phone number; email reply and the PWA camera cover it. Revisit if it turns out to be the friction point.
- **Vendor-fetched receipts** (Amazon/Lyft scraping). Gmail rules do 90% of it.
- **AI-generated receipt detection**, **human verification queue**, **mail-in envelope**. Single user; irrelevant.
- **Live SOSBiz status polling**. Worth a look later; SOSBiz has no public API, so it would be scraping. A quarterly "check status" reminder with a deep link is the honest version.
- **Anything that resembles a proprietary ledger.** Full export exists from day one (Bench).
