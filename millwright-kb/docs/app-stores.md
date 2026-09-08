# Getting Millwright KB into the app stores

The site is already an installable app (see `/install` on the site): students add it from the
browser and it works offline. The stores are a second, optional route that needs paid developer
accounts and signed native builds. This page is the checklist for that route.

## What the stores need from you

| | Google Play | Apple App Store |
|---|---|---|
| Account | Google Play Console, one-time US$25, at play.google.com/console (individual account is fine; Google may ask for ID verification and, for personal accounts created after late 2023, a 14-day closed test with 12 testers before production) | Apple Developer Program, US$99 per year, at developer.apple.com/programs (individual account uses your Apple ID; no D-U-N-S number needed for an individual) |
| Build | Signed Android App Bundle (`.aab`) | Signed `.ipa` uploaded with Xcode or Transporter; needs a Mac or a macOS CI runner |
| Listing | Title, short and full description, 2-8 phone screenshots (1080 × 1920 or similar), 512 × 512 icon, 1024 × 500 feature graphic, privacy policy URL, content rating questionnaire, data-safety form | Name, subtitle, description, screenshots for 6.7 in and 6.5 in iPhones (and iPad if supported), 1024 × 1024 icon, privacy policy URL, App Privacy answers, age rating |
| Privacy policy URL | https://millwright-kb.riggs1991.workers.dev/privacy | same |
| Review time | hours to a few days | one to three days typically |

## The native projects in this repo

Both wrap the same web build in a native shell with Capacitor:

- `android/` : app id `com.millwrightkb.app`; version in `android/app/build.gradle`
  (`versionCode` must go up by 1 every upload; `versionName` is what people see).
- `ios/App/` : bundle id `com.millwrightkb.app`; version and build number in Xcode
  (General tab) or `ios/App/App.xcodeproj/project.pbxproj`.

Build the web app into them:

```
cd millwright-kb
npm ci
npm run cap:sync        # builds dist/ and copies it into android/ and ios/
```

### Android: built by GitHub Actions, no computer needed

The workflow `.github/workflows/millwright-kb-android.yml` runs on every push:

- It always produces a **sideload APK** signed with the committed debug key
  (`android/debug.keystore`, standard Android debug password) and publishes it to the rolling
  release **android-latest**:
  https://github.com/riggs19991/ruggedroute-dataops/releases/download/android-latest/millwright-kb.apk
  Because the key is constant, each new build installs over the previous one. This key is for
  sideloading only; it is public, so it must never be used for the store.
- When these four repository secrets exist (GitHub → Settings → Secrets and variables → Actions)
  it also builds the **signed Play Store bundle** `millwright-kb-release.aab` and a signed release
  APK, attached to the same release and as a workflow artifact:
  `ANDROID_KEYSTORE_BASE64` (the .jks file base64-encoded), `ANDROID_KEYSTORE_PASSWORD`,
  `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`.
- `versionCode` is the workflow run number (always increasing, as Play requires); `versionName`
  is the `package.json` version.

Creating the Play keystore without a computer: open the repository in **GitHub Codespaces** from
the phone browser (Code → Codespaces → Create), then in its terminal run

```
keytool -genkeypair -keystore play.jks -alias millwrightkb -keyalg RSA -keysize 2048 -validity 10000
base64 -w0 play.jks
```

and paste the printed text into the `ANDROID_KEYSTORE_BASE64` secret with the passwords and alias
you chose. Download `play.jks` to somewhere safe as well: losing it means no more updates to the
listing (Play App Signing keeps a copy of the final key, but you still need this upload key).
Then upload the `.aab` from the release page in Play Console → Testing → Closed testing, then
Production.

### iOS (needs macOS)

Without a Mac, use a macOS GitHub Actions runner:

1. In the Apple developer site create an App ID `com.millwrightkb.app`, a Distribution certificate
   and an App Store provisioning profile. Export the certificate as a `.p12`.
2. Add repository secrets: `IOS_CERT_P12_BASE64`, `IOS_CERT_PASSWORD`, `IOS_PROFILE_BASE64`,
   `APPSTORE_KEY_ID`, `APPSTORE_ISSUER_ID`, `APPSTORE_PRIVATE_KEY` (an App Store Connect API key).
3. Add a workflow job on `macos-latest` that runs `npm ci && npm run cap:sync`, installs the
   certificate and profile into a keychain, runs `xcodebuild -workspace ios/App/App.xcworkspace
   -scheme App -configuration Release archive` and `xcodebuild -exportArchive`, then uploads with
   `xcrun altool` or the `apple-actions/upload-testflight-build` action. Ask for this job when the
   account exists; the secrets decide the exact steps.
4. TestFlight first (internal testers, no review), then submit for review in App Store Connect.

### Native-only details to check before submitting

- Sign-in links: the confirmation and reset emails open the website. In the native apps add
  Android App Links / iOS Universal Links for `millwright-kb.riggs1991.workers.dev` (Capacitor
  `@capacitor/app` handles the `appUrlOpen` event) so the links open inside the app.
- Icons and splash: run `npx @capacitor/assets generate --iconBackgroundColor '#0f172a'` from
  a 1024 × 1024 source icon to fill every native size.
- Camera and photos: the file picker uses the standard browser inputs, which work in the
  Capacitor WebView without extra permissions on Android; iOS needs `NSCameraUsageDescription`
  and `NSPhotoLibraryUsageDescription` strings in `ios/App/App/Info.plist`.
- Bump `versionCode` and the iOS build number on every upload.

## Order that works

1. Home-screen install now (done: site is offline-capable, install page at `/install`).
2. Google Play account, Android signed bundle, closed test with the class, production.
3. Apple account, macOS CI job, TestFlight with the class, App Store.

## Store listing URLs

Both stores ask for these; they are live pages in the app:

- Privacy policy: https://millwright-kb.riggs1991.workers.dev/privacy
- Terms of use: https://millwright-kb.riggs1991.workers.dev/terms
- Support / contact: https://millwright-kb.riggs1991.workers.dev/support (email riggs1991@gmail.com)
- Developer name on the listing: Addictive Media Productions LLC
