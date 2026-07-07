# AGENTS.md

Guidance for AI agents (and humans) working on this repository.

## What this project is

This repo started as **[Kita](https://github.com/st1020/kita)**, a Zola static-site
theme (a clean/minimal blog theme based on Hugo's `hugo-paper`). It is being
adapted into the **website for a makerspace ("RMS")**, with **Notion used as a
headless CMS** for content (pages, projects, posts, etc.) instead of hand-written
Markdown files.

At the time this file was written, the Notion integration has **not been built
yet** — the repo is still mostly stock Kita theme content/config. Any agent
picking up work here should treat the Notion-sync pipeline as a to-be-designed
feature unless later notes in this file (or commits) say otherwise.

## Tech stack

- **[Zola](https://www.getzola.org/)** — Rust-based static site generator.
  Content lives in `content/`, templates in `templates/` (Tera templating
  language), config in `zola.toml`.
- **Tailwind CSS v4** — styling. `static/app.css` is the source; `static/main.css`
  is the generated output. Built via the CLI, not a bundler.
- **Bun** — used to run the Tailwind CLI (see `package.json`). `bun.lock` is
  present, so use `bun install` / `bun run <script>`.
- No JS framework/build step beyond Tailwind — this is a plain SSG site.

### Key scripts (`package.json`)

- `bun run dev` — watches `static/app.css` and rebuilds `static/main.css`.
- `bun run build` — one-off Tailwind build.

To actually serve/build the site you need the `zola` binary installed
separately (not an npm/bun package): `zola serve` / `zola build`.

## Repo layout

```
zola.toml                  # site config (title, menu, social, theme options — all under [extra])
theme.toml                 # theme metadata (name/author/license) — not site content
content/
  _index.md                # homepage section config (sort_by, paginate_by)
  pages/                   # non-blog pages
    _index.md              # marks this section as render=false, uses pages.html template
    about.md                # /about
    archive.md              # /archive (uses templates/archive.html)
  projects/                # /projects — project section (mirrors events/)
    _index.md              # list page config (sort_by="weight", template="projects.html", page_template="project.html")
    <slug>.md               # one Markdown file per project (title, description, weight, extra.tags, extra.links)
  events/                  # /events — event section
    _index.md              # list page config (sort_by="date", paginate_by, template="events.html", page_template="event.html")
    <slug>.md               # one Markdown file per event (title, date, description, extra.location, extra.cta_*)
  shortcodes/               # demo content showcasing the `gallery` shortcode
  markdown-syntax.md, math-typesetting.md, placeholder-*.md, theme-config.md
                            # example/demo blog posts from the upstream theme — remove for a real site
templates/
  index.html                # base layout (extended by page.html); includes header/footer/profile/page_list
  page.html                 # single post/page layout
  section.html              # section listing layout
  pages.html                # layout used by the "pages" (non-blog) section
  projects.html             # /projects list view — iterates paginator.pages/section.pages
  project.html              # /projects/<slug> detail view — tags + extra.links CTAs
  events.html                # /events list view — iterates paginator.pages/section.pages
  event.html                  # /events/<slug> detail view
  archive.html               # archive listing by date
  taxonomy_list.html / taxonomy_single.html   # tags pages
  404.html
  macros.html                # Tera macros (formatted by oxfmt — see .oxfmtrc.json ignore list)
  partials/                  # header, footer, profile, toc, comment (giscus), page_info, etc.
  shortcodes/                 # admonition, gallery, mermaid, inline_svg
  injects/ (not present yet)  # optional override point — see "Inject support" below; create as needed
static/
  app.css / main.css          # Tailwind input/output
  icons/                       # svg icons referenced by name in zola.toml (social links, avatar)
  images/
```

## Configuration model

Almost all theme/site behavior is driven by the `[extra]` table in
`zola.toml` (profile info, social links, top menu, footer, giscus comments,
math/mermaid toggles, style overrides). When making this a makerspace site,
most day-one changes (title, description, menu items, socials, base_url)
happen here, not in templates.

The `theme = "kita"` line, if set, would point at a themes/ submodule — check
`zola.toml` before assuming templates in `templates/` are actually the ones
in use vs. a theme directory. Currently this repo *is* the theme copy itself
(no `themes/` dir), so templates here are live.

### Inject points (extension mechanism without forking the theme)

The theme supports drop-in HTML overrides via `templates/injects/<name>.html`
(not currently present — create the directory as needed). Available points:
`head`, `header_nav`, `body_start`, `body_end`, `page_start`, `page_end`,
`footer`, `page_info`. All are included with `ignore missing`, so it's safe
to add only the ones you need. **Prefer injects over editing base templates**
when adding makerspace-specific widgets (e.g. an Open/Closed status badge,
embedded calendar, membership CTA) to keep the diff from upstream Kita small.

## Content model notes

- `content/pages/_index.md` has `render = false` — the `pages` section itself
  has no page, it just sets `page_template = "pages.html"` for its children.
- The `projects` page is data-driven: edit `content/pages/projects/data.toml`,
  not the template, to add/remove projects. This TOML-as-data-source pattern
  (`load_data(path=asset, format="toml")` in `projects.html`) is a useful
  precedent for how a Notion sync could work: **a sync script could write
  Notion data out to TOML/JSON files under `content/`, and templates load them
  the same way**, rather than needing custom Tera code per data type.

  **UPDATE:** `projects` is now a full Zola section (`content/projects/`),
  structured identically to `events` — one Markdown file per project with
  `title`, `description`, `weight` (controls sort order via `sort_by =
  "weight"` in `_index.md`), and `extra.tags` / `extra.links` (list of
  `{ name, url }`). Each project gets its own detail page at
  `/projects/<slug>` (rendered by `templates/project.html`), and the list
  page (`templates/projects.html`) links to those pages instead of
  out to external URLs directly. This replaces the old single-page
  `data.toml` approach described above; keep this note as historical context
  for the previous TOML pattern, but new content should follow the
  Markdown-per-item section pattern used by both `events/` and `projects/`.
- Demo/placeholder content (`markdown-syntax.md`, `math-typesetting.md`,
  `placeholder-*.md`, `theme-config.md`, `content/shortcodes/*`) is upstream
  theme sample content — expect to delete it when real makerspace content
  goes in, but keep it around for reference on shortcode usage until then.

## Notion-as-CMS integration (planned, not yet implemented)

No code for this exists yet. When implementing it, consider:

1. **Sync direction**: Notion → static files at build time (not runtime fetch —
   Zola has no server-side runtime). A pre-build script (Node/Bun or a CI step)
   should pull data from the Notion API and write Markdown (with front matter)
   or TOML/JSON files into `content/`.
2. **Where to put the sync script**: likely a new top-level script (e.g.
   `scripts/sync-notion.ts` or `.mjs`) run via a `package.json` script
   (`bun run sync`) before `zola build`, and wired into whatever CI/CD deploys
   the site (check for `.github/workflows/` — none exist yet, so this is
   greenfield).
3. **Secrets**: a Notion integration token and database ID(s) will be needed.
   Store as environment variables / CI secrets — never commit them. Add a
   `.env.example` if env vars are introduced, and ensure `.env` is gitignored
   (currently `.gitignore` does not list it — add it if you add dotenv usage).
4. **Mapping Notion databases to content types**: decide up front which
   Notion databases map to which Zola sections (e.g. a "Projects" database →
   Markdown files under `content/projects/`, an "Events"/"Blog" database →
   Markdown files under `content/events/`, an "Equipment"/"Tools" database →
   a new section or data file). Follow the existing Markdown-per-item section
   pattern used by `events/` and `projects/` where it fits, to minimize new
   template code.
5. **Images/files from Notion**: Notion-hosted file URLs expire; any synced
   images should be downloaded into `static/` (or a `static/notion/` subfolder)
   during sync rather than linked directly.

## Conventions / tooling

- Formatting: `oxfmt` is configured via `.oxfmtrc.json` (`printWidth: 100`,
  Tailwind class sorting enabled). It ignores `templates/macros.html` and
  `static/main.css` (generated/hand-tuned files) — don't hand-format those,
  and don't fight the formatter on them.
- `static/main.css` is a **build artifact** — edit `static/app.css` and run
  the Tailwind build instead of editing `main.css` directly.
- `.gitignore` excludes `/public` (Zola's build output), `/node_modules`, and
  some legacy `giallo*.css` files — don't commit build output.
- No test suite exists in this repo. Validation = `zola build` (or `zola check`)
  succeeding, plus visual review via `zola serve`.
- **Preferred way to verify rendered output**: instead of relying solely on
  `zola build` exit status, check that the live dev server (`zola serve`,
  default `http://127.0.0.1:1111`) actually renders the expected markup. Use
  the `fetch`/`curl` tool to pull the relevant URL and pipe it through `grep`
  to confirm specific elements/links/text are present (e.g.
  `curl -s http://127.0.0.1:1111/projects/ | grep -o '<h1[^>]*>[^<]*</h1>'`).
  This catches template/content bugs that a successful build can silently
  hide (e.g. an empty section, a stale link, wrong data being iterated).
  **If no dev server is already running, do not start one yourself in the
  background** — ask the user to run `zola serve` (or confirm one is already
  running) before attempting to fetch/grep against it.

## Suggested first steps for rebranding to the makerspace site

1. Update `zola.toml`: `base_url`, `title`, `description`, `author`,
   `extra.profile`, `extra.menu`, `extra.footer`, social icons.
2. Replace/remove demo content in `content/` (placeholders, markdown-syntax,
   math-typesetting demo, shortcodes demo) once real content or the Notion
   sync produces replacements.
3. Update `content/pages/about.md` with real makerspace info.
4. Decide on the Notion database schema(s) before writing the sync script, and
   document the chosen mapping in this file once implemented, so future
   agents don't have to reverse-engineer it.
5. Add real branding assets to `static/` (favicon, `apple-touch-icon.png`,
   avatar/logo, social icons) replacing the Kita placeholders.
