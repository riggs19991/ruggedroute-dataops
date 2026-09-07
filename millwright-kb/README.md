# Millwright Knowledge Base

A searchable library of millwright procedures, charts and manufacturer manuals that any
student at any school can open, search, and add to. Teachers create a group for their
class, hand out a join code, and post each week's reading, handouts and files to it.

Live data lives in the shared Supabase project (all tables are prefixed `mw_`). The web
app is a static Vite + React build that talks to Supabase directly with the publishable key.

## What is in it

| Area | What it does |
|---|---|
| **Search** | Postgres full-text search with weighting (title and tags first, then manufacturer and model numbers, then summary, then body), typo tolerance via trigram similarity, and exact model-number matching (`TA4207H`, `22220 EK`). Anyone can search, signed in or not. |
| **Browse** | 13 topic categories: alignment, bearings, oxy-fuel, belts/chains/couplings, gearboxes, pumps and seals, rigging, measurement, fasteners, hydraulics, safety, manufacturer manuals, shop math. |
| **Articles** | Markdown with tables, procedures, charts. Kinds: procedure, reference, chart, manual, tip, safety. Attachments (PDF, images, documents, 50 MB each) in private storage with signed links. Bookmarks, view counts, print. |
| **Contribute** | Any signed-in user can write an article or upload a manual. Students' public submissions wait for a **teacher review**; teachers publish directly. Anything shared with a group is visible to that group immediately. |
| **Groups** | A teacher creates a group (class) and gets a 6-character join code. Students join with the code. The teacher posts to **week N** with a message, a linked library article and files. The term start date tells everyone which week is "this week". |
| **Roles** | Everyone signs up as a student. A teacher unlocks teacher tools on the profile page with the **teacher access code** (see below). |

Seed content (26 articles) covers, among others: shaft-to-shaft alignment (fundamentals
and tolerance table, rim-and-face with shim math, reverse dial, laser, soft foot, thermal
growth), setting a tapered-bore spherical roller bearing on an adapter sleeve with the full
SKF drive-up card (PUB BU/P9 14231 EN) and the FAG inch table, the Victor acetylene tip
chart (form 65-2505: cutting, welding and heating tips with pressures), oxy-acetylene
setup/lighting/shutdown, bearing designation codes, hot mounting, V-belts, roller chain,
couplings, gearbox lubrication, Dodge Torque-Arm installation, mechanical seals, rigging,
micrometers, dial indicators, bolt torque, lockout/tagout and shop reference tables.

## Layout

```
millwright-kb/
  content/              markdown source of truth for seed articles (+ categories.json)
  scripts/seed.mjs      pushes content/ into the database (npm run seed)
  scripts/build-seed.mjs writes supabase/seed/seed_content.sql for psql users
  supabase/migrations/  schema, RLS policies, search RPC, storage bucket, hardening
  src/                  the app (React + TypeScript, react-router, supabase-js, marked)
```

## Run it locally

```bash
cd millwright-kb
npm install
cp .env.example .env     # publishable key; safe to ship in a browser bundle
npm run dev              # http://localhost:5173
```

`npm run build` type-checks and produces `dist/` (a static site; `public/_redirects`
makes single-page routing work on Cloudflare Pages / Netlify).

## Database

Migrations in `supabase/migrations/` have already been applied to project
`tzucpijgyjhpgwukjsau`. To recreate on a fresh project, apply them in order (Supabase SQL
editor, `supabase db push`, or the MCP `apply_migration` tool), then seed.

Tables: `mw_profiles`, `mw_categories`, `mw_articles`, `mw_files`, `mw_groups`,
`mw_group_members`, `mw_group_posts`, `mw_bookmarks`, `mw_settings` (no API access).
Storage bucket: `mw-files` (private; uploads go to `<user id>/…`).

Row-level security in one paragraph: published community articles are readable by
everyone; pending/draft/rejected ones only by the author and teachers; group articles and
group posts only by group members and the group's teacher; students can only insert
draft/pending; only teachers can set `published`; files inherit the visibility of their
article or post; profiles are readable (names show as authors) and editable only by the
owner; the `role` column can only change through the `mw_become_teacher` RPC.

### Teacher access code

Stored in `mw_settings` (never readable through the API). Default is
`MILLWRIGHT-TEACHER`. **Change it before handing the app out:**

```sql
update public.mw_settings set value = 'YOUR-NEW-CODE' where key = 'teacher_access_code';
```

### Re-seeding content from `content/`

Edit or add markdown files (front-matter: `title`, `slug`, `category`, `kind`, `tags`,
`manufacturer`, `model_numbers`, `source`, `summary`), then:

```bash
SEED_TOKEN=<value of seed_token in mw_settings> npm run seed
```

The import is an upsert keyed on `slug`, so re-running is safe. Rotate the token with
`update public.mw_settings set value = encode(gen_random_bytes(24),'hex') where key = 'seed_token';`.

### Auth settings worth knowing

The project currently has **email confirmation on** (`mailer_autoconfirm = false`), so a
new student has to click the link in the confirmation email before signing in. Turn it off
in Supabase → Authentication → Providers → Email if the school would rather skip that.
Leaked-password protection is off (advisor warning); enable it under Authentication →
Password settings.

## Deploy

The app is a static site. Any of these work:

- **Cloudflare Pages** (matches the rest of this repo): `npx wrangler pages deploy dist --project-name millwright-kb`.
  The `millwright-kb.yml` workflow does this on pushes to `main` when
  `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` secrets exist (the token needs
  *Cloudflare Pages: Edit*). Without them it just builds and type-checks.
- **Netlify / Vercel / GitHub Pages**: publish `dist/`, keep the SPA fallback.

After deploying, add the site URL to Supabase → Authentication → URL Configuration
(Site URL and Redirect URLs) so confirmation and magic-link emails land back on the app.

## Adding a manual (for students and teachers)

Sign in → Contribute → pick *Manufacturer Manuals*, type the manufacturer and the exact
model numbers from the nameplate, paste the key numbers (torques, oil quantities) into
the body so they are searchable, attach the PDF, submit. A teacher approves it.
The in-app article *How to add a manufacturer manual* walks through this.

## Testing

`npm run build` runs `tsc -b` and Vite. An end-to-end Playwright smoke test (anonymous
search and article rendering, teacher code, group creation, weekly post with file, student
join, student submission, teacher review, publish) was run against the live project during
development; it is not checked in because it needs throwaway accounts.
