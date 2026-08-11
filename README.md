# Comic Downloader

A terminal (TUI) app to search for, download, and convert manga from [weebcentral.com](https://weebcentral.com) into PDFs.

Built with Textual for TUI, Scrapy for cleaning the response htmls.

## Features

- Live search with an autocomplete dropdown as you type
- Manga page with a cover preview and a full chapter checklist
- Download every chapter or just the ones you select
- Live progress and status while downloading
- Automatic PDF conversion after a download finishes
- Keyboard-friendly, mouse clickable, and works in any modern terminal

## Requirements

- Python 3.12+
- uv python package manger
- A terminal that supports graphical images (kitty, sixel/iTerm2, etc.) for full cover previews

## Get UV 

Download it from the [official site](https://docs.astral.sh/uv/getting-started/installation/#installation-methods) 

For Windows, simply paste in the terminal
```sh
winget install --id=astral-sh.uv  -e
```
For Linux/MacOS
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Installation
Download/git clone the project first and then open the project in your terminal and type
```sh
uv sync
```
This sets up all the packages needed for it to work

## How to use

Simply type in the terminal 
```sh
uv run comic
```

## How it works

1. `tui.py` — the Textual app (search, manga, and download screens)
2. `weebcentral.py` — fetches chapter lists and downloads page images in parallel
3. `utils.py` — converts the downloaded pages into PDFs with `img2pdf`

Downloads are staged in `Cache/` as images and are removed after conversion.

All your downloaded mangas will be in the `Books/` directory.

## Disclaimer

I am not affiliated with Weebcentral in anyway, this project is done purely for educational purposes only