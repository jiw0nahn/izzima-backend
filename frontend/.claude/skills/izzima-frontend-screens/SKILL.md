---
name: izzima-frontend-screens
description: Conventions for building screens, tabs, and reusable components in the izzima frontend (Expo Router + React Native + TypeScript, at frontend/). Use this skill whenever the user asks to build, add, or update a screen, tab, page, or component in the izzima app — especially when they hand you a design mockup, screenshot, or Figma link and say things like "이 화면 만들어줘", "이거대로 컴포넌트 만들어", "새 탭 추가해줘", "이 디자인대로 화면 구현해줘". Also use it before running any npm/expo install in this project, since it documents a recurring dependency conflict and the fix. Do not use for backend (FastAPI) or ai-pipeline work — this skill is frontend-only.
---

# izzima frontend screens

This skill captures the patterns already established in `frontend/` so new screens and
components look and feel consistent with what's already built, instead of every screen
reinventing its own structure.

## Before you touch anything: install gotcha

This project pins `react@19.2.3`, but transitive Expo packages frequently want a newer
patch of `react`/`react-dom`. Plain `npm install` / `npx expo install` can fail with an
`ERESOLVE` peer-dependency error as a result. `frontend/.npmrc` already sets
`legacy-peer-deps=true` to route around this — as long as you run installs from inside
`frontend/`, no extra flags are needed. If you *do* see an ERESOLVE error, it's this known
issue, not a real conflict; do not down/up-grade `react` to "fix" it.

## Routing (Expo Router)

Routes are files under `app/`. The file path *is* the URL — there's no separate router
config to edit for a new screen.

- **Tab screens** live in `app/(tabs)/` and are wired up in `app/(tabs)/_layout.tsx` via
  `<Tabs.Screen name="..." options={{ title, tabBarIcon }} />`. `name` must match the
  filename (without extension) in that same folder.
- **Non-tab screens** (detail pages, settings sub-pages, etc.) go directly under `app/`,
  outside the `(tabs)` group. **Dynamic detail routes** use the `[param].tsx` filename
  convention (e.g. `app/category/[id].tsx`, `app/item/[id].tsx`), read via
  `useLocalSearchParams<{ id: string }>()`, and are navigated to with
  `router.push(\`/category/${id}\`)`.
- **Modals** (a screen that should cover the tab bar with its own Cancel/Title/Done-style
  header, like the upload flow) are a normal file under `app/` — e.g. `app/upload-modal.tsx`
  — registered with `presentation: 'modal'` via an explicit `<Stack.Screen name="upload-modal"
  options={{ presentation: 'modal' }} />` inside the `<Stack>` in `app/_layout.tsx`. Adding
  one explicit `Stack.Screen` like this doesn't disable auto-registration of the other
  routes, so you only need to do this for routes that need non-default presentation.
- **A tab bar button that shouldn't behave like a normal tab** (e.g. the floating center "+"
  button, which opens the upload modal instead of switching to a tab panel) is done by
  overriding `tabBarButton` on that `Tabs.Screen`. See `UploadTabButton` in
  `app/(tabs)/_layout.tsx`: it ignores the default `onPress` the navigator would hand it and
  calls `router.push('/upload-modal')` directly instead, so the tab is never actually
  "switched to". The route file for that tab (`app/(tabs)/upload.tsx`) still needs to exist
  for the `Tabs.Screen` registration to be valid, even though it's never shown — leave it as
  a minimal placeholder.
- The root `app/_layout.tsx` wraps the whole app in `<SafeAreaProvider>` (from
  `react-native-safe-area-context`). Individual screens that sit under the status bar
  (most top-level tab screens) should wrap their content in `<SafeAreaView edges={['top']}>`
  from the same package — the tab bar itself already handles the bottom safe area, so don't
  add bottom edge padding on top of it.

## Where code goes

| Kind of code | Location | Import via |
|---|---|---|
| One reusable UI piece (card, badge, button, list item) | `components/<Name>.tsx`, one component per file, **named export** (`export function Name(...)`) | `@/components/Name` |
| Shared TypeScript shape used by 2+ components/screens | `types/<domain>.ts` (e.g. `types/home.ts`) | `@/types/<domain>` |
| Mock data reused across more than one screen | `lib/mockData.ts` | `@/lib/mockData` |
| Small non-UI helper (date math, API client, etc.) | `lib/<name>.ts` (e.g. `lib/date.ts`, `lib/api.ts`) | `@/lib/<name>` |
| A screen | `app/**/*.tsx` | — (it's a route, not imported) |

The `@/` alias maps to the `frontend/` root (see `tsconfig.json`), so imports read the
same regardless of how deeply nested the importing file is.

Look at `components/Badge.tsx`, `components/ExpiringItemCard.tsx`, and
`components/CategoryCard.tsx` for the concrete shape these should take: a typed props
object (often just `{ item: SomeType }` pulling the real shape from `types/`), a component
function, and a `StyleSheet.create` at the bottom of the same file.

## Screens hold mock data until there's a real API

There is no backend wiring yet for most screens. Rather than leaving a screen empty or
inventing a loading/fetch layer prematurely, follow the pattern in `app/(tabs)/index.tsx`:
define one or more `const SOME_NAME: SomeType[] = [...]` mock arrays near the top of the
screen file, typed against the shared `types/` definitions, and pass them into the
components that render them. This keeps the screen visually complete and keeps the data
shape identical to what a future API response should look like, so swapping in a real
`fetch`/`api.get(...)` call later is a one-line change, not a rewrite.

Prefer mock data that's generated relative to "now" (e.g. `daysLeft` offsets turned into
real dates) over data frozen to a specific calendar date — see `CALENDAR_EVENTS` in
`lib/mockData.ts`. A frozen date looks right today and silently wrong (or confusing) whenever
someone opens the app later. When you need to format a `Date` as `YYYY-MM-DD` for this kind
of thing, use `toLocalISODate` from `lib/date.ts`, not `date.toISOString().slice(0, 10)` —
`toISOString()` converts to UTC first, which can silently shift the date by one depending on
the device's timezone. Calendar/day-grid logic needs to stay in local time throughout.

## Typography: always use `@/components/Text`, never `Text` from `react-native`

The app font is **Pretendard**, loaded in `app/_layout.tsx` via `expo-font`'s `useFonts`
(files live in `assets/fonts/`, currently Regular/SemiBold/Bold/ExtraBold — that's all four
weights the UI has needed so far; pull another weight from the `pretendard` npm package's
`dist/public/static/*.otf` files if a design calls for one that isn't there yet).

Pretendard ships as separate font files per weight, not one variable font, so React
Native's `fontWeight` style **does nothing useful here** — it won't switch files. Weight is
selected through `fontFamily` instead, and `components/Text.tsx` wraps that up for you:

```tsx
import { Text } from '@/components/Text';

<Text>기본은 regular</Text>
<Text weight="semiBold">강조하고 싶을 때</Text>
<Text weight="bold">더 굵게</Text>
<Text weight="extraBold">타이틀 급</Text>
```

Every screen and component in this codebase imports `Text` from `@/components/Text`
instead of `react-native` — do the same for anything new. If you ever see a `fontWeight` in
a `StyleSheet`, that's leftover from before this convention landed; replace it with the
matching `weight` prop instead of leaving both (having both can look like faux-bold on some
platforms since the OS may synthesize bold on top of an already-bold file).

## Styling

Plain React Native `StyleSheet.create`, defined at the bottom of each file — no styling
library (no NativeWind/Tailwind/styled-components). Reuse these tokens rather than picking
new colors ad hoc, so screens stay visually consistent:

| Token | Hex | Use |
|---|---|---|
| Brand / active blue | `#2F6FED` | active tab tint, links, primary buttons/badges |
| Dark text | `#111827` | titles, primary text |
| Gray text | `#9CA3AF` | subtitles, secondary/meta text, inactive tab tint |
| Light gray background | `#F3F4F6` | image/thumbnail placeholders, icon button backgrounds |
| Border | `#EEEEEE` | card borders |
| Danger red | `#EF4444` (bg) / `#FFFFFF` (text) | urgent badges (e.g. D-1) |
| Info blue | `#DBEAFE` (bg) / `#2563EB` (text) | soft badges (e.g. D-3) |

If a design calls for a color that isn't in this table, it's fine to add it — but check
first whether it's actually a close match to an existing token before introducing a near-
duplicate shade.

## Icons

`@expo/vector-icons`, specifically the `Ionicons` set, e.g.
`<Ionicons name="home" color={color} size={size} />`. Prefer an existing Ionicons name
over pulling in a different icon set or a custom SVG unless nothing reasonable exists.

## Workflow: turning a design mockup into code

When the user gives you a screenshot, Figma link, or description of a screen to build:

1. **Scan it for repeating pieces** — a card that appears more than once, a badge, a list
   row. Anything that repeats (or is likely to be reused on another screen later) becomes a
   `components/*.tsx` file. If its data shape doesn't already exist in `types/`, add it
   there rather than inlining an anonymous prop type.
2. **Build the screen file** by composing those components with a mock data array (see
   above), matching the layout/spacing/colors from the design using the token table.
3. **Verify before reporting success.** There's no way to keep an interactive dev server
   running in this environment, so instead run:
   ```bash
   npx tsc --noEmit
   npx expo export --platform web --output-dir /tmp/izzima-export && rm -rf /tmp/izzima-export
   ```
   `tsc` catches type errors; `expo export` actually runs the Metro bundler, which is the
   only reliable way to catch a broken `@/` import or an unresolved package before handing
   the result back to the user. Don't skip the export step just because `tsc` passed — path
   aliases and Metro-specific resolution issues won't show up in `tsc` alone.
4. Tell the user what you built and where, and explicitly flag anything you guessed at
   (an icon that wasn't 100% clear in the mockup, an exact color, spacing you eyeballed) so
   they can correct it quickly instead of you silently committing to a guess.
