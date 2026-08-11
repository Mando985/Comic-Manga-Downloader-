# AGENTS.md

Textual TUI app that searches weebcentral.com, downloads chapters, and converts them to PDFs.

## Branch

- **Work on `rewrite`** — the only branch with the TUI app (`src/comic_downloader/`).
- `main` is the abandoned flat CLI layout (root-level `main.py`/`utils.py`/`weebcentral.py`, no `src/`, no TUI). Do not edit or branch from `main`. The repo defaults to `origin/main`, so always `git checkout rewrite` first.

## Commands

- Run: `uv run comic` (alias for `comic_downloader.main:main` → `ComicApp().run()`). Also `uv run python -m comic_downloader.main`.
- Do **not** use `textual run` — the app is launched via plain `.run()`.
- Lint (not a gate): `uv run ruff check src`. BLE001 (blind `except Exception`) and RUF012 (`BINDINGS` class attr) are pervasive and accepted; only the I001 import-order errors are worth fixing (`--fix`).
- Python 3.12 (`uv` manages env, deps in `pyproject.toml`).

## Testing

- No test suite in the repo. Verify UI changes with Textual's `run_test()` Pilot harness headlessly:
  - Headless `Footer` renders `Blank` — assert bindings via `app.screen.active_bindings`, not footer text.
  - `q` is swallowed by the focused `Input`; the app-quit binding is `ctrl+q`.
- Live visual checks (cover rendering, image drivers) need a graphical terminal; PIL driver errors only surface in a real `PIL_DRIVER` env.

## Textual gotchas (hard-earned)

- `pop_screen()` is a coroutine and **must not be awaited inside an async message handler** — it deadlocks the message pump. Button handlers are sync and call `self.app.pop_screen()` fire-and-forget.
- Every `@work(exclusive=True, thread=True)` worker must have its **own `group=`** (`cover`, `chapters`, `download`, `pdf`). Two exclusive workers sharing the default group cancel each other, and a thread worker can't be aborted — the second start stalls the first forever.

## Architecture

- `src/comic_downloader/tui.py` — the whole UI: `SearchScreen` (search + suggestions dropdown), `MangaScreen` (cover + chapter `SelectionList`), `DownloadScreen` (progress), `ComicApp` (worker dispatch). Editable.
- `src/comic_downloader/main.py` — entry point. Editable.
- `src/comic_downloader/weebcentral.py` — backend, **read-only** by convention. `weebcentral(id)` class: `get_issue_links` (chapter ids from `.../series/{id}/full-chapter-list`, anchors `a[href*='/chapters/']`, ascending), `issue_downloader` (writes PNGs to `Cache/{Title}/{issue}/`), `manga_downloader(chosen_ids, progress_callback, status_callback)`.
- `src/comic_downloader/utils.py` — backend, **read-only**. `utils.convert2pdf()` → `Books/{Title}/...pdf` (sorts `*.png` by trailing int), then deletes `Cache/`.
- Search is a POST to `https://weebcentral.com/search/simple?location=main` with htmx headers; rows are `section#quick-search-result a.join-item`, name `.line-clamp-2::text`, id from URL segment, cover `img::attr(src)`.
- `Cache/` and `Books/` are gitignored runtime dirs.

## Tooling

- `opencode.json` wires the Textualize MCP (launch/debug the running app) via `uv --directory mcp run textualize-mcp`. `.agents/skills/` has a `textual` skill — load it for TUI work.
- Repo has `.agents/`, `mcp/`, `reference.md`, and `file1.md` gitignored as local scratch/context.
