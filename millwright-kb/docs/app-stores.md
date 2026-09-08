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

### Android (any computer with Android Studio)

1. Install Android Studio, open `millwright-kb/android`.
2. Create a signing key once: Build → Generate Signed Bundle / APK → Create new keystore. Keep the
   `.jks` file and both passwords somewhere safe and backed up: losing it means you can never
   update the app again. (Play App Signing then manages the final key for you.)
3. Build → Generate Signed Bundle → release. Upload the `.aab` in Play Console → Testing → Closed
   testing first, then Production.
4. For a quick test on your own phone without the store: Build → Build APK, copy the APK to the
   phone and install it (allow "install unknown apps").

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
