# CLAUDE.md

Guidance for AI assistants working in this repository.

## What this is

A **static, build-less website** published via **GitHub Pages** at
`https://ildarsagidullin.github.io/AI/`. It has two kinds of content, both
in **Russian**, aimed at entrepreneurs/experts learning AI tools:

1. **Root prompt library** — `index.html` ("AI Арсенал"): a single-page app
   listing ready-to-use prompts by category, with RU/EN toggle and
   copy-to-clipboard.
2. **Standalone guides** — one per subfolder (e.g. `tokeny-claude-code/`,
   `claude-dlya-novichkov/`, `codex-s-nulya/`): each is a self-contained
   article page about a specific AI topic (Claude Code, ChatGPT, Codex,
   agents, skills, security, etc.).

There is **no build step, no framework, no dependencies, no package manager,
no config files, and no tests.** Every page is hand-written HTML with inline
CSS and vanilla JS. You edit `.html` directly and the change is live once
pushed and Pages redeploys.

## Layout

```
index.html                 # Root prompt-library app ("AI Арсенал")
<topic-slug>/
  index.html               # One standalone guide
  hero.jpg                 # Small pixel mascot shown in the header
  bye.jpg                  # Mascot shown in the footer
  img/ or screenshots/     # Optional inline images for that guide
```

Each guide is a **directory whose name is the URL slug** (kebab-case,
transliterated Russian), served at `.../AI/<slug>/`. Folders are independent —
guides do **not** link to each other or back to the root, and the root nav
does **not** list them. They are shared individually (via Telegram).

## Two page templates — match the one you're editing

The site does not share a stylesheet; each file inlines its own `<style>`.
Two established patterns exist — **copy the conventions of the file you're
working in** rather than importing the other's style.

- **Prompt-library template** (`index.html`): full-height `.layout` with a
  sticky `.sidebar` (category nav) + `.main`; mobile hamburger. All prompt
  content lives in a JS `const data = { <category>: [ {title, hint, ru, en} ]
  }` object near the bottom; `renderAll()` builds the cards. To add/edit a
  prompt, edit the `data` object — do **not** hand-write card HTML. Keep the
  `ru`/`en` pair and the sidebar/`data` category keys in sync
  (`marketing`, `hr`, `ads`, `finance`, `tables`, `docs`, `nego`,
  `productivity`).
- **Guide template** (all subfolder pages): a single centered `.sheet` with
  header (`.kicker`, `h1`, hand-drawn SVG underline, `.lead`, `.meta`), a
  `.toc` of same-page anchors, `h2`/`h3` sections, `.note` callouts,
  `.prompt` blocks with a copy button, and a `.footer-mascot`. Blue accent
  `#1d4ed8`, red underline accents `#dc2626`.

## Conventions

- **Language:** page content is Russian; `<html lang="ru">`. The prompt
  library additionally carries English (`en`) variants toggled in-page.
- **Self-contained files:** inline `<style>` in `<head>`, small vanilla-JS
  `<script>` before `</body>`. No external JS/CSS libraries. The only remote
  asset is Google Fonts (Inter) via `<link>` — safe to keep or drop.
- **Copy buttons:** clipboard copy uses `navigator.clipboard.writeText(...)`
  with a brief "Скопировано/done" state. Reuse the existing snippet in the
  file rather than inventing a new mechanism.
- **Images:** local, relative paths only (`hero.jpg`, `img/...`,
  `screenshots/...`). Mascots use `image-rendering: pixelated`.
- **Responsive:** every page targets mobile — keep the existing
  `@media (max-width: …)` rules and `meta viewport` intact.
- **Monetization links** appear across pages and are intentional: the author's
  Telegram (`t.me/IldarSagidullin`), a closed-chat offer, and referral links
  (e.g. Bybit `ref=...`). Preserve them unless asked to change them; don't add
  new outbound/referral links on your own.

## Editing workflow

- Make the change directly in the target `.html`. Preview by opening the file
  in a browser (or `python3 -m http.server` from the repo root and visit
  `/<slug>/`) — there is nothing to compile.
- Keep each page a single standalone file; don't factor shared CSS/JS into
  new common assets unless explicitly asked.
- When adding a **new guide**: create `<new-slug>/index.html` from the guide
  template of an existing folder, add its `hero.jpg`/`bye.jpg`, and keep all
  asset paths relative.
- Match the surrounding file's formatting, Russian tone, and class names.

## Git & deployment

- Default branch: `main`. GitHub Pages serves the site from the repo, so
  **merging to `main` publishes it** — double-check content before it lands.
- Do work on the feature branch you were assigned; commit with clear messages
  (the existing history uses concise Russian commit messages). Push with
  `git push -u origin <branch>`. Do not open a pull request unless asked.
