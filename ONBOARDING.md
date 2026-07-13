# Onboarding — Covariate (React Native app)

Welcome! Two ways to get the sensor app running, fastest first.

## Fastest: see it on your phone in ~2 minutes (no install, no repo access)

1. Install **Expo Go** (free): [iPhone](https://apps.apple.com/app/expo-go/id982107779) · [Android](https://play.google.com/store/apps/details?id=host.exp.exponent).
2. Ask Caitlin to run `npx expo start --tunnel` and send you the QR code (or the `exp://…exp.direct` link it prints).
3. Open your phone's **Camera**, point it at the QR, tap **Open in Expo Go**.
4. The app loads → tap **▶ Start recording**. You'll see `accel` / `mag` / `barometer` live.
   (`light` + `mic` show "dev build" — see the last section.)

That alone lets you test sensors on your phone. Two phones reading at once *is* our H2 reliability setup.

## Full setup: run it from your own copy (to contribute)

One-time:

1. **GitHub account** — sign in at github.com, then send Caitlin your **username** so she can add you to the repo.
2. Install:
   - **Git** — https://git-scm.com/downloads
   - **Node.js (LTS)** — https://nodejs.org
   - **Expo Go** on your phone (links above)
3. Clone + run:
   ```
   git clone https://github.com/CaitlinEverett/ambient-recorder.git
   cd ambient-recorder
   npm install
   npx expo start --tunnel
   ```
   Scan the QR it prints with your phone's Camera → **Open in Expo Go**.

The repo's default branch is already the React Native app, so a plain clone gives you the right thing.

## About "dev build" (the light + mic rows)

`accel` / `mag` / `barometer` are stock Expo sensors — they run in Expo Go. Ambient **light** and **mic level** use small custom native modules (`modules/covariate-light`, `modules/covariate-mic`) that Expo Go can't load, so they read "dev build" until we build a **dev client**.

Building the dev client — and validating those two sensors on-device — needs a **Mac with Xcode**. If you've got a Mac, that's a clean piece to own. If not, the Expo Go path above still lets you run and test the other three.

## Stuck?

Ping Caitlin. The usual culprits: wrong folder (make sure you `cd ambient-recorder` first), or the QR won't connect (use `--tunnel`, and update Expo Go to the latest from the store).
