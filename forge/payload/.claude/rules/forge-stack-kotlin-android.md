---
paths:
  - "**/*.kt"
  - "**/*.kts"
---
# Forge stack rules — Kotlin / Android
- MVVM boundaries: composables render state and forward events; ViewModels own state; repositories own data access. Do not reach across a layer.
- Hilt scopes: keep each binding in the scope its module already uses; widening a scope (for example to `SingletonComponent`) is a design decision for the plan, not a fix.
- Mapbox v11: refer to style layers and sources by their existing ids; a new id is a design decision, not a rename.
- Design tokens only: colours, spacing and typography come from the token resources; never hard-code a value a token already names.
- Unit tests live under `app/src/test` and run with `./gradlew :app:testDebugUnitTest`; compile with `./gradlew :app:compileDebugKotlin`.
- UI checks that need a device or emulator are planned as `check: external` (for example `./gradlew connectedDebugAndroidTest` on a local device); in a cloud container they are tagged `env-cannot-run` and attested by the operator.
- Run every command from the repository root.
