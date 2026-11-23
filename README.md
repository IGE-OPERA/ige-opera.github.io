# ige-opera.github.io

Website of the OPERA research group @ IGE (Grenoble). Jekyll + Minimal
Mistakes, deployed to GitHub Pages on every push to `main`.

## Setup locally

1. Install ***Ruby***: [https://www.ruby-lang.org/en/documentation/installation/](https://www.ruby-lang.org/en/documentation/installation/),
2. Install ***Bundler***: `gem install bundler`,
3. Install dependencies (listed in the `Gemfile`): `bundle install`,
4. Build and serve the website locally: `bundle exec jekyll serve`.

You may also consult Jekyll Splash layout documentation [here](https://mmistakes.github.io/minimal-mistakes/docs/layouts/#splash-page-layout) and Minimal Mistakes helpers [here](https://mmistakes.github.io/minimal-mistakes/docs/helpers/)

## How to edit the site (runbook)

Most content lives in `_data/*.yml` and is maintained in the **Grist content
database** — the daily `grist-sync` workflow pulls it back into those files.
See [docs/grist-setup.md](docs/grist-setup.md) for the table layouts and the
one-time setup.

| I want to…              | Where                                             |
|-------------------------|---------------------------------------------------|
| add/remove a project    | Grist `Projects` table (or `_data/projects.yml`) |
| add outreach content    | Grist `Outreach` table                             |
| post a news item        | Grist `News` table                                 |
| open / close a position | Grist `Positions` table (empty table = "no open positions" on [Join us](https://ige-opera.github.io/join/)) |
| add a team member       | new file in `_people/` (schema documented in `_people/README.md`) + photo in `assets/images/people/` |
| edit research themes    | `_data/themes.yml`, `_data/methods.yml`, `_pages/research.md` |
| summarise a new paper   | follow [docs/pills-runbook.md](docs/pills-runbook.md) |

Publications are fully automated: the daily `zotero-sync` workflow regenerates
`_data/publications.bib` and `_data/publications.json` from the group's Zotero
library (id `6427155`), downloads banner artwork for new papers (best effort,
via `scripts/fetch_publication_artwork.py`) and opens a "papers needing pills"
issue. The one-line pills live in `_data/pills.yml`.

## Repository layout

```
_pages/        top-level pages (home, research, people, projects, software,
               publications, outreach, join)
_people/       one markdown file per team member (front matter only)
_data/         content files, most of them synced from Grist or Zotero
_includes/opera/  custom components (hero, publications grid …)
_sass/opera*.scss the OPERA design layer over Minimal Mistakes
scripts/       sync + generation scripts (stdlib Python, CI-friendly)
docs/          runbooks (Grist setup, research pills)
```

## Preview of work in progress

The `redesign` branch (and any branch adapted in `preview.yml`) is built with
`--baseurl /preview` and pushed to [IGE-OPERA/preview](https://github.com/IGE-OPERA/preview),
served at <https://ige-opera.github.io/preview/>.
