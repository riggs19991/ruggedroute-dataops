# Millwright KB: make the Stripe donation flow live (handoff runbook)

Written 2026-09-22 for a Claude Desktop session that controls the owner's Chrome (signed in to Stripe,
GitHub, Supabase and Cloudflare). Everything below is a browser action; no code changes are needed.

**Starter prompt for the new session** (paste as the first message):

> Open https://github.com/riggs19991/ruggedroute-dataops/blob/claude/millwright-knowledge-database-pg5n1c/millwright-kb/docs/donations-golive.md
> in Chrome and follow it top to bottom. Do the clicks yourself in my signed-in tabs. Never paste the
> Stripe key or the donation token into chat, a file or a commit: copy them straight from the source
> into the GitHub secret field. Stop and ask me before paying the $1 test and before any refund or delete.

## 0. What is already true (verified 2026-09-22)

- Live app: https://millwright-kb.riggs1991.workers.dev (Cloudflare Worker `millwright-kb`, static site plus
  `/api/donate/status|checkout|confirm|display`). Code: repository `riggs19991/ruggedroute-dataops`,
  branch `claude/millwright-knowledge-database-pg5n1c`, folder `millwright-kb/` (`worker/index.ts`,
  `worker/stripe.ts`, `src/pages/Support.tsx`, `src/pages/SupportThanks.tsx`, `src/components/DonorWall.tsx`).
- `GET https://millwright-kb.riggs1991.workers.dev/api/donate/status` returns `{"configured":false}` because the
  Worker has neither `STRIPE_SECRET_KEY` nor `DONATION_TOKEN`. While false, the Support page silently falls back to
  the old Stripe Payment Link (buy.stripe.com), which takes money but adds nothing to the supporters wall.
- Deploy: GitHub Actions workflow **millwright-kb** (`.github/workflows/millwright-kb.yml`). It builds, runs
  `wrangler deploy`, then runs `wrangler secret put STRIPE_SECRET_KEY` and `wrangler secret put DONATION_TOKEN`
  from the GitHub repository secrets of the same names. The last run (#46, 2026-09-22 17:24 UTC) pushed no secrets
  because neither GitHub secret exists yet. The workflow has a manual "Run workflow" button.
- Supabase project `tzucpijgyjhpgwukjsau` (the app's database): the row `mw_settings.key = 'donation_token'`
  exists and is a 48-character lowercase hex string. Table `mw_donations` has 0 rows. The token-gated functions
  `mw_record_donation`, `mw_set_donation_display`, `mw_hide_donation` and the wall's read policy are in place.
- The Worker makes exactly two Stripe calls: `POST /v1/checkout/sessions` (inline `price_data`, product name
  "Support Millwright KB", `submit_type=donate`) and `GET /v1/checkout/sessions/{id}`. A restricted key with
  **Checkout Sessions: Write** covers both (write includes read).

## Rules

- Live mode in Stripe (key starts with `rk_live_`), not a sandbox.
- Secrets travel only from Stripe's copy button or the Supabase result cell into GitHub's secret value field.
  Do not read them aloud, echo them, screenshot-describe them, or store them anywhere else.
- Keep the Stripe tab open until the key is saved in GitHub: a self-created live key cannot be revealed again.
- Ask the owner before paying, refunding or deleting anything.

## 1. Create the restricted Stripe key

1. Open https://dashboard.stripe.com/apikeys. Confirm the Dashboard is in **live mode** (no sandbox banner).
2. Click **Create restricted key**. If Stripe asks what the key is for, choose the option for building your own
   integration (not "agent access" and not "providing this key to another website"). Start from zero permissions.
3. **Key name:** `Millwright KB`.
4. Permissions: find **Checkout Sessions** and set it to **Write**. Leave every other resource at **None**.
5. Click **Create key** and complete the two-factor prompt.
6. Click the key value to copy it (clipboard only). In **Add a note** type `GitHub secret STRIPE_SECRET_KEY`, click **Done**.

## 2. GitHub secret `STRIPE_SECRET_KEY`

1. Open https://github.com/riggs19991/ruggedroute-dataops/settings/secrets/actions.
2. Click **New repository secret**. **Name:** `STRIPE_SECRET_KEY`. **Secret:** paste the clipboard. Click **Add secret**.

## 3. GitHub secret `DONATION_TOKEN`

1. Open https://supabase.com/dashboard/project/tzucpijgyjhpgwukjsau/sql/new and run:
   ```sql
   select value from public.mw_settings where key = 'donation_token';
   ```
   Copy the single result cell (48 characters). If a Supabase connector is available instead of the browser,
   the same query works there, but still copy the value only into GitHub.
2. Back on https://github.com/riggs19991/ruggedroute-dataops/settings/secrets/actions click **New repository secret**.
   **Name:** `DONATION_TOKEN`. **Secret:** paste. Click **Add secret**.
3. Confirm the list now shows both `STRIPE_SECRET_KEY` and `DONATION_TOKEN` (the existing `CLOUDFLARE_*` secrets stay).

## 4. Redeploy so the Worker receives the secrets

1. Open https://github.com/riggs19991/ruggedroute-dataops/actions/workflows/millwright-kb.yml.
2. Click **Run workflow**, choose branch `claude/millwright-knowledge-database-pg5n1c`, click the green **Run workflow**.
3. Wait for the new run to finish (about one minute). Open it, open job **build**, expand step
   **Deploy to Cloudflare Workers (static assets)** and check the log shows the deploy URL and two successful
   `wrangler secret put` uploads (one for each secret).
4. If the run is green but a `secret put` line failed or is missing: open https://dash.cloudflare.com, go to
   **Workers & Pages → millwright-kb → Settings → Variables and Secrets**, add `STRIPE_SECRET_KEY` and
   `DONATION_TOKEN` with type **Secret** (paste from Stripe / Supabase exactly as in steps 1 and 3), then **Deploy**.

## 5. Check the Worker is configured

Open https://millwright-kb.riggs1991.workers.dev/api/donate/status in a new tab. It must show `{"configured":true}`.
If it still shows false, the deploy did not carry the secrets: repeat step 4 (or its contingency).

Optional pre-check without paying, if a terminal is available (creates an unpaid Checkout session that
expires by itself after 24 hours, no charge):
```sh
curl -sS -X POST https://millwright-kb.riggs1991.workers.dev/api/donate/checkout \
  -H 'Content-Type: application/json' -d '{"amount_cents":100}'
```
Expected: `{"url":"https://checkout.stripe.com/...","session_id":"cs_live_..."}`. A 502 whose `error` text
names a missing Stripe permission means step 7-B below applies.

## 6. The real $1 test (ask the owner first; their own card is fine)

1. Open https://millwright-kb.riggs1991.workers.dev/support (a private window avoids stale app caches).
2. Tap the **$ other** box, type `1`. The button reads **Donate $1 with Stripe**. Tap it.
3. Stripe Checkout (checkout.stripe.com) must open showing **Support Millwright KB** for **$1.00**. Pay.
4. Stripe returns to `/support/thanks?session_id=...`. The page must say **Your $1 donation is confirmed**.
5. Choose **My business**, type the business name the owner wants (60 characters max, the filter rejects URLs,
   phone numbers and offensive words), click **Save**. Expect **Saved. Thank you again!** and the entry in the
   wall below with the name, `$1`, "today" and a **business** tag.
6. Open https://millwright-kb.riggs1991.workers.dev/support and confirm the same entry on the wall
   ("1 donation, $1 given so far").

## 7. If something fails

- **7-A. The button opened buy.stripe.com (the old Payment Link).** The Worker still answers 503: `configured`
  is false. Cancel that page without paying and go back to step 5.
- **7-B. "Could not start the donation. Please try again in a minute."** The Stripe call failed. Open
  https://dashboard.stripe.com/workbench/logs (live mode) and read the newest failed `POST /v1/checkout/sessions`:
  the error message names the missing permission. Typical fix for inline `price_data`: Stripe → API keys →
  **⋯ → Edit key** on `Millwright KB` → add **Products: Write** and **Prices: Write** → **Save**. The key value
  does not change, so no new GitHub secret and no redeploy are needed. Retry step 6.
- **7-C. "Stripe has not confirmed this payment yet" on the thanks page.** Reload once after a minute. If it
  persists, the key cannot read Checkout Sessions (it should, with Write); check the key's permissions as in 7-B.
- **7-D. "That name was not accepted."** The moderation filter (`millwright-kb/src/lib/moderation.ts`) rejected it;
  pick a plain business name or choose **My name**.

## 8. Clean up the test (ask the owner first)

1. Optional refund: https://dashboard.stripe.com/payments → open the $1.00 payment → **Refund** (Stripe keeps its
   processing fee either way).
2. Remove the wall entry, one of:
   - As the owner's admin account on https://millwright-kb.riggs1991.workers.dev/support, click **hide** beside
     the row (keeps the row in the database, hidden from the wall), or
   - In the Supabase SQL editor (https://supabase.com/dashboard/project/tzucpijgyjhpgwukjsau/sql/new):
     ```sql
     select count(*) from public.mw_donations where amount_cents = 100 and created_at > now() - interval '1 hour';
     -- expect 1, then:
     delete from public.mw_donations where amount_cents = 100 and created_at > now() - interval '1 hour';
     ```
3. Reload /support: the wall should read **No donations yet** again.

## Done when

- `/api/donate/status` returns `{"configured":true}`.
- A real $1 donation appeared on the wall with the chosen business name.
- The test entry has been hidden or deleted (and refunded, if the owner wanted).

## Reference

- `millwright-kb/README.md`, section "Donations and legal pages" (same setup, shorter).
- `millwright-kb/wrangler.toml` documents the two secrets; `millwright-kb/supabase/migrations/20260922000100_mw_donations.sql`
  is the database side (already applied). To rotate the token later: update `mw_settings` per the comment at the top
  of that migration, then update the `DONATION_TOKEN` GitHub secret and redeploy.
