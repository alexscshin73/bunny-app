# Bunny App MVP Final Summary

Date: March 23, 2026

## 1. Final MVP Goal

`Bunny App` MVP was finalized as a bilingual conversation service for Korean and Spanish speakers with:

- private room invite flow
- realtime text translation conversation
- room/member history
- profile and room management UI
- notification support on web and mobile-facing flows

This document is the final snapshot of what was completed by the end of the MVP phase on March 23, 2026.

## 2. What Was Completed

### 2.1 Core conversation product

- private invite-based room join flow
- realtime room websocket flow
- text/demo/upload turn history
- room title editing
- room member tracking and history persistence
- guest join support

### 2.2 Account and profile layer

- user register/login/logout
- `My Page` and `My Profile` screens
- profile save flow
- avatar selection
- preferred language setting
- notification preference setting
- room history list and room detail view

### 2.3 Notification layer

- backend notification records
- invite / new turn / announcement notification types
- unread count handling
- room-level unread badge handling
- web push support
- mobile local notification flow for native client work

## 3. Backend Scope

The backend now supports:

- room creation and join
- invite-code based room access
- room persistence on SQLite by default
- turn persistence
- user/session management
- room membership tracking for signed-in users
- notification persistence and read-state updates
- web push subscription storage and delivery
- guest numbering logic

Important room behavior:

- guests now join as `Guest1`, `Guest2`, `Guest3`, ...
- guest numbers are sequential and not reused casually after leave/rejoin history
- invite-based join is the primary path
- signed-in room creation is enforced on the current backend

## 4. Web MVP Scope

The web app is the primary fully-integrated MVP client.

### 4.1 Main completed web UX

- room create/join/invite/share flow
- realtime conversation screen
- text input, emoji, attachment, mic controls
- room title edit with `Edit -> Save`
- room history list and detail view
- profile editing and save flow
- top-right notification bell and logout

### 4.2 Notification UX

- `My Page` no longer shows a full notification list as the main UI
- unread counts are shown directly on room items
- opening a room marks that room's notifications as read
- bell icon reflects notification state
- notification preference is linked to profile `Yes / No`

### 4.3 Profile UX updates

- `Notification` field added beside `Name` and `Language`
- default notification preference is `Yes`
- profile save icon uses the shared disk/save icon
- mobile responsive profile layout was tightened for small screens
- `Tag line` order on mobile was adjusted to appear after `Name / Language / Notification`

### 4.4 Mobile-web responsive fixes on the web UI

- top header text shortened from `"이름" 님의 홈입니다.` to `"이름" 님의 홈`
- long names are truncated with `...`
- mobile bell/logout icons were reduced
- profile save icon remains fixed at top-right on mobile layout
- iOS-only phone underline issue was fixed by disabling Safari auto telephone detection and overriding detector styles

## 5. Mobile App Scope

The Expo mobile app was updated to align with the current backend where feasible.

### 5.1 Completed mobile alignment

- mobile join flow now uses `invite_code`
- mobile room/session types were updated to match backend fields
- mobile now trusts the backend-assigned participant identity, including guest numbering
- mobile room title edit follows the same `Edit -> Save` behavior

### 5.2 Mobile notification work

- mobile notification preference state was added
- notification toggle was added in mobile UI
- local native notification permission flow was added with `expo-notifications`
- Android notification channel setup was added
- local app-side notifications can be shown when the app is not active

### 5.3 Current mobile limitation

The mobile app is not yet full parity with the web app.

Still limited compared with the web:

- no full mobile auth/profile/history product surface equal to web
- backend room creation still depends on signed-in web/backend flow
- remote mobile push is not fully completed yet
- current mobile alert flow is local/native notification oriented, not final APNs/FCM production push

## 6. Android / iOS Notes

Platform differences were reviewed and partially normalized.

### 6.1 Backend URL differences

- Android emulator local backend: `http://10.0.2.2:8000`
- iOS simulator / web local backend: `http://127.0.0.1:8000`

### 6.2 Notification differences

- Android requires notification channel setup
- Android 13+ may prompt for notification permission when alerts are enabled
- iOS requires explicit user permission for notifications
- real remote push on iOS requires physical device and APNs-ready flow
- real remote push on Android production also requires device-build push setup

### 6.3 UI differences handled

- iOS Safari phone auto-link underline issue fixed
- small-screen responsive profile/header layout adjusted to behave more consistently across Android and iPhone browsers

## 7. Room and Notification Rules in Final MVP

### 7.1 Room rules

- room access is based on private invite code
- guests can join shared rooms
- guest names increment sequentially
- room title can be edited and saved directly from the UI

### 7.2 Notification rules

- notification preference is per-user
- default profile notification setting is `Yes`
- if notification preference is `No`, notification creation/delivery is suppressed where connected
- supported notification types:
  - `invite`
  - `turn`
  - `announcement`

## 8. Operational / Runtime Notes

The MVP codebase now includes:

- SQLite-backed room/user state
- web push code path and subscription handling
- static asset cache/versioning updates through `index.html` and `sw.js`
- launch/runtime scripts and docs for public demo paths

Relevant supporting docs already in repo:

- [`README.md`](/Users/sclshin/Projects/bunny-app/README.md)
- [`docs/REAL_TWO_USER_DEMO.md`](/Users/sclshin/Projects/bunny-app/docs/REAL_TWO_USER_DEMO.md)
- [`docs/BUNNY_CARROAMIX_SETUP.md`](/Users/sclshin/Projects/bunny-app/docs/BUNNY_CARROAMIX_SETUP.md)
- [`docs/CLOUDFLARE_TUNNEL.md`](/Users/sclshin/Projects/bunny-app/docs/CLOUDFLARE_TUNNEL.md)
- [`docs/MAC_AUTOSTART.md`](/Users/sclshin/Projects/bunny-app/docs/MAC_AUTOSTART.md)

## 9. Remaining Post-MVP Items

These items were intentionally left for a later phase:

- full mobile auth / my page / history parity with web
- full production-grade remote mobile push
- broader admin announcement tooling
- more polished multi-device presence behavior
- broader test coverage across all web/mobile/backend flows

## 10. Final MVP Status

As of March 23, 2026, the MVP is complete enough to close the first delivery phase with:

- working web-first bilingual conversation product
- invite-based room sharing
- profile and room management
- unread notification model
- web push foundation
- mobile backend alignment and notification groundwork
- Android/iOS responsive fixes for the current product surface

## 11. Recommended Next Phase

If development resumes later, the highest-value next steps are:

1. complete mobile auth/profile/history parity
2. complete production mobile remote push
3. strengthen automated tests
4. refine multi-user room behavior and polish

