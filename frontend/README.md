# Resume Scanner — Frontend

Next.js 16 (App Router) + React 19 + TypeScript + Tailwind CSS v4.
Consumes the Phase 6 FastAPI backend. See `DESIGN.md` for the visual
design rationale.

## Setup

```bash
npm install
cp .env.local.example .env.local   # points at the backend, default http://localhost:8000
npm run dev
```

Requires the backend (Phases 1-6) running — see `../backend/README.md`.

## Scripts

```bash
npm run dev         # dev server
npm run build        # production build
npm run start         # serve the production build
npm run typecheck      # tsc --noEmit
npm run lint             # eslint (see note below on invocation)
```

**Note on `lint`**: `next lint` changed its CLI argument parsing in
Next 16 in a way that misinterprets the invocation in this project's
setup; run `npx eslint .` directly instead, which is what `npm run
lint` does under the hood here.

## Project structure

```
app/                    # Next.js App Router pages
├── layout.tsx            # root layout, loads fonts via next/font/google
├── page.tsx                # landing page
├── login/, register/        # auth pages
└── dashboard/                 # the core product: upload, analyze, results

components/
├── ui/                    # primitives: Button, Card, Input, Alert, StampBadge
├── auth/                    # AuthProvider (context), login/register forms
├── analysis/                  # ResumeUpload, VerdictGauge, CategoryPanel,
│                                 EvidenceRow, RecommendationsList
└── layout/                      # Navbar

lib/
├── api-client.ts            # typed fetch wrapper against the FastAPI backend
├── types.ts                   # TS types mirroring backend Pydantic schemas
│                                 (kept in sync by hand -- see its docstring)
├── format.ts                    # safe rendering helpers for Evidence's
│                                   unknown-typed found_value/expected_value
└── auth.ts                        # token storage
```

## Real toolchain issues found and fixed during this build

Verified via actual `tsc`, `eslint`, and `next build` runs — not
assumed to work from writing plausible-looking config:

1. **TypeScript 7.0.2 vs. the ecosystem.** The initial `package.json`
   pinned the newest published TypeScript, which turned out to be a
   major-version jump that `@typescript-eslint` (bundled inside
   `eslint-config-next`) explicitly doesn't support (`peer typescript@
   ">=4.8.4 <6.1.0"`). This was the actual root cause of a cryptic
   `The "id" argument must be of type string. Received undefined`
   crash during `next build` — not a bug in this project's code. Fixed
   by pinning `typescript` to the latest stable `5.x` (`5.9.3`).
2. **ESLint 10 vs. `eslint-config-next`'s bundled `eslint-plugin-
   react`.** `eslint-config-next` declares `eslint: ">=9.0.0"` as its
   peer range, but its vendored `eslint-plugin-react` calls a rule-
   context API (`context.getFilename()`) that ESLint 10 changed,
   crashing with `contextOrFilename.getFilename is not a function`.
   Fixed by pinning `eslint` to the latest stable `9.x` (`9.39.5`).
3. **`@eslint/eslintrc`'s `FlatCompat` shim crashes** on this
   dependency graph with `TypeError: Converting circular structure to
   JSON`. Avoided entirely by using `eslint-config-next`'s native flat
   config exports (`eslint-config-next/core-web-vitals` and `/
   typescript`) instead of the legacy compat shim — cleaner and one
   fewer dependency (`@eslint/eslintrc` was removed from
   `package.json` once this was in place).
4. **Tailwind v4's setup is not v3's.** Needs `@tailwindcss/postcss`
   as the actual PostCSS plugin (not `tailwindcss` directly) and no
   longer needs `autoprefixer` (Lightning CSS handles vendor
   prefixing internally) — `package.json` reflects v4's real
   requirements, not v3-era assumptions.
5. **`next/font/google` needs `fonts.googleapis.com`**, which isn't
   reachable from the sandbox this was built in (same class of
   restriction as `huggingface.co` in Phase 2 and `api.openai.com` in
   Phase 3 — confirmed via `curl -I`, returns `x-deny-reason:
   host_not_allowed`). The real `layout.tsx` uses `next/font/google`
   normally and works in any environment with standard internet
   access; verified by temporarily swapping to system fonts for a
   build-verification pass, confirming that was the *only* remaining
   error, then restoring the real font-loading code.

After all of the above, `tsc --noEmit`, `eslint . --max-warnings=0`,
and `next build` all pass cleanly with zero errors or warnings.

## Verified against a real running instance

Beyond compiling cleanly, the actual product flow was driven through
a real Chromium browser (Playwright) against the real Phase 6
backend: register → upload a real `.docx` → run analysis → expand the
evidence ledger — with screenshots captured and reviewed at each step.
This caught one real bug (see `DESIGN.md`'s closing section) that pure
compilation checks couldn't have: the verdict gauge's original
negative-margin text overlay, fragile across viewport sizes, fixed by
rendering the score as SVG `<text>` instead.

## Known follow-ups (not gaps in this phase, intentional next steps)

- Types in `lib/types.ts` are hand-maintained against the backend's
  Pydantic schemas. A codegen step from the live `/openapi.json` would
  remove the manual-sync burden — noted here rather than added now, to
  avoid a build-time dependency this phase doesn't strictly need yet.
- Token storage uses `localStorage` (appropriate for this deployed
  app, not a sandboxed environment). A hardening pass could move to an
  httpOnly cookie set by the backend to reduce XSS exposure — natural
  Phase 9 (observability/hardening) work.
- The `npm audit` moderate-severity findings are inside Next.js's own
  vendored `postcss`, not this project's direct dependency (already
  pinned above the vulnerable range) — not fixable without downgrading
  Next itself.
