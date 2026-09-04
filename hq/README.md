# RuggedRoute HQ

Private back-office app for **Addictive Media Productions LLC**: receipts, deadlines, documents,
year-end tax package. Android phone + Windows PC, one Flutter codebase, no app store.

- Plan: `../docs/plans/2026-09-04-business-ops-tool-plan.md`
- Research: `../docs/research/2026-09-04-business-tools-research.md`
- App: `app/` (Flutter) · Database: `supabase/migrations/` (applied to project `tzucpijgyjhpgwukjsau`)
- CI: `../.github/workflows/hq-ci.yml` (analyze + test) and `hq-release.yml` (build + publish)

## How the pieces fit

```
phone (Android APK) ──┐                      ┌── hq_* tables (row-level security: founder only)
                      ├── Supabase project ──┤── hq-vault bucket   (receipts, documents)
PC (Windows .exe)  ───┘                      └── hq-releases bucket (APK / installer builds,
                                                  read by the apps to self-update)
GitHub Actions "hq-release" ── builds both, uploads to hq-releases, adds a row to hq_app_releases
```

Sign-in is email + 6-digit code. The database only accepts the email in `hq_allowed_emails`.
The EIN is stored in Supabase Vault (encrypted); only its last four digits sit in a table.

## One-time setup (founder, ~10 minutes, on the PC)

1. **Email code template.** Supabase dashboard → Authentication → Emails → *Magic Link*.
   Replace the body with:
   ```html
   <h2>RuggedRoute HQ sign-in code</h2>
   <p>Your code: <strong style="font-size:24px">{{ .Token }}</strong></p>
   <p>It expires in 1 hour. If you did not request it, ignore this email.</p>
   ```
   Save. (Without `{{ .Token }}` the email carries a link instead of a code and the app cannot
   use it.) Note: Supabase's built-in mailer allows only a couple of sign-in emails per hour;
   sessions last for weeks so this rarely matters, and a custom sender comes in Phase 7.

2. **Release secret.** GitHub → this repo → Settings → Secrets and variables → Actions →
   *New repository secret*: name `HQ_SUPABASE_SERVICE_ROLE_KEY`, value from Supabase dashboard
   → Project Settings → API Keys → *service_role* (click Reveal). This key is what lets CI
   upload builds; it never ships inside the app.

3. **Build the first release.** GitHub → Actions → *hq-release* → *Run workflow* → version
   `0.1.0` → Run. About 10 minutes. The first run also creates the Android signing key and
   stores it in the private `hq-releases/signing/` folder so every future build is signed
   identically.

4. **Install.**
   - **Phone:** Actions → the finished run → *Artifacts* → `android-apk` → download on the phone →
     open the APK → allow "install from this source" once → Install. (Later updates come from
     inside the app.)
   - **PC:** same run → `windows-installer` → download → run `RuggedRouteHQ-Setup-0.1.0.exe`.
     Windows SmartScreen will warn because the installer is not code-signed: *More info → Run
     anyway*. That is expected for a private app.

5. **Sign in** with riggs1991@gmail.com, enter the emailed code, then fill in *Business*.

After this, new versions are published by re-running *hq-release* with a higher version number;
both apps notice on launch and offer a one-tap update.

## Local development

```
cd hq/app
flutter pub get
flutter analyze && flutter test
flutter run -d windows     # or an attached Android device
```

Schema changes go in `supabase/migrations/NNNN_name.sql` and are applied to the project with the
Supabase MCP `apply_migration` (or `supabase db push` with the CLI).

## Where things are

| Piece | Path |
|---|---|
| Config (Supabase URL + publishable key) | `app/lib/config.dart` |
| Router, theme, app frame | `app/lib/app.dart` |
| Sign-in | `app/lib/features/auth/sign_in_screen.dart` |
| Home (exceptions inbox) | `app/lib/features/home/home_screen.dart` |
| Business profile + EIN vault | `app/lib/features/profile/profile_screen.dart` |
| Settings + updater UI | `app/lib/features/settings/settings_screen.dart` |
| Self-updater | `app/lib/updater/updater.dart` |
| Data layer | `app/lib/data/hq.dart` |
| Android signing | `app/android/app/build.gradle.kts` (reads `android/key.properties`, written by CI) |
| Windows installer | `app/windows/installer/hq.iss` |
| Schema | `supabase/migrations/0001_hq_init.sql` |
| Seed defaults (categories, deadline rules, checklist) | `supabase/migrations/0002_hq_seed_defaults.sql` |
