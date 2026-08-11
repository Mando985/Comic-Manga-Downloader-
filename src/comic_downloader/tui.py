import os
import re

import requests
from PIL import Image as PILImage
from scrapy import Selector
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    OptionList,
    ProgressBar,
    SelectionList,
    Static,
)
from textual.widgets.option_list import Option
from textual.widgets.selection_list import Selection
from textual_image.widget import Image as TextualImage

from comic_downloader.utils import utils
from comic_downloader.weebcentral import weebcentral

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

SEARCH_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://weebcentral.com",
    "Referer": "https://weebcentral.com/",
    "X-Requested-With": "XMLHttpRequest",
    "HX-Request": "true",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
}

COVER_DIR = os.path.join("Cache", "covers")


def search_manga(text: str) -> list[dict]:
    session = requests.Session()
    session.headers.update(SEARCH_HEADERS)
    resp = session.post(
        "https://weebcentral.com/search/simple",
        params={"location": "main"},
        data={"text": text},
        timeout=15,
    )
    selector = Selector(text=resp.text)
    results = []
    for row in selector.css("section#quick-search-result a.join-item"):
        name = (row.css(".line-clamp-2::text").get() or "").strip()
        url = row.css("::attr(href)").get()
        cover = row.css("img::attr(src)").get()
        if name and url:
            results.append(
                {
                    "name": name,
                    "id": url.rstrip("/").split("/")[-2],
                    "cover": cover,
                }
            )
    return results


def get_chapters(manga_id: str) -> list[tuple[str, str]]:
    url = f"https://weebcentral.com/series/{manga_id}/full-chapter-list"
    headers = {"User-Agent": USER_AGENT}
    res = requests.get(url, headers=headers, timeout=15).text
    selector = Selector(text=res)
    pairs = []
    for a in selector.css("a[href*='/chapters/']"):
        href = a.css("::attr(href)").get()
        if not href:
            continue
        cid = href.split("/")[-1]
        raw = " ".join(a.css("::text").getall())
        name = re.split(r"\s+Last Read", raw)[0].strip()
        pairs.append((cid, name))
    # site lists newest first; reverse for ascending order
    return list(reversed(pairs))


class SearchScreen(Screen):
    BINDINGS = [("down", "focus_results", "Results")]

    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict] = []
        self._timer = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Comic Downloader", id="search-title"),
            Input(placeholder="Search manga...", id="search-input"),
            OptionList(id="suggestions"),
            id="search-box",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#suggestions", OptionList).display = False
        self.query_one("#search-input", Input).focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        if self._timer is not None:
            self._timer.stop()
        text = event.value.strip()
        if not text:
            self.results = []
            self.query_one("#suggestions", OptionList).clear_options()
            self.query_one("#suggestions", OptionList).display = False
            return
        self._timer = self.set_timer(0.4, lambda: self.perform_search(text))

    def perform_search(self, text: str) -> None:
        self.run_search(text)

    @work(exclusive=True, thread=True)
    def run_search(self, text: str) -> None:
        try:
            results = search_manga(text)
        except Exception:
            results = []
        self.app.call_from_thread(self._show_results, results, text)

    def _show_results(self, results: list[dict], text: str) -> None:
        current = self.query_one("#search-input", Input).value.strip()
        if current != text:
            return
        self.results = results
        options = self.query_one("#suggestions", OptionList)
        options.clear_options()
        for i, r in enumerate(results):
            options.add_option(Option(r["name"], id=str(i)))
        options.display = bool(results)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        try:
            r = self.results[int(event.option.id)]
        except (IndexError, TypeError, ValueError):
            return
        self.app.push_screen(MangaScreen(r["id"], r["name"], r.get("cover")))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        options = self.query_one("#suggestions", OptionList)
        if not options.display or not options.option_count:
            return
        index = options.highlighted if options.highlighted is not None else 0
        self._open_result(index)

    def action_focus_results(self) -> None:
        options = self.query_one("#suggestions", OptionList)
        if options.display:
            options.focus()

    def _open_result(self, index: int) -> None:
        try:
            r = self.results[index]
        except IndexError:
            return
        self.app.push_screen(MangaScreen(r["id"], r["name"], r.get("cover")))

    def clear_input(self) -> None:
        self.query_one("#search-input", Input).value = ""
        options = self.query_one("#suggestions", OptionList)
        options.clear_options()
        options.display = False
        self.results = []


class MangaScreen(Screen):
    def __init__(self, manga_id: str, name: str, cover_url: str | None) -> None:
        super().__init__()
        self.manga_id = manga_id
        self.manga_name = name
        self.cover_url = cover_url
        self.manga = weebcentral(manga_id)
        self.all_chapters: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static(self.manga_name, id="manga-name"),
                Container(
                    TextualImage(id="cover-image"),
                    Static("Cover unavailable", id="cover-fallback"),
                    id="cover",
                ),
                id="left-panel",
            ),
            Vertical(
                Static("Loading chapters...", id="status"),
                Static(
                    "For specific issues, click on the chapters to check it",
                    id="hint",
                ),
                SelectionList(id="picker"),
                Horizontal(
                    Button("Cancel", variant="error", id="cancel"),
                    Button("Download All", variant="success", id="dl-all"),
                    Button("Download Selected", variant="primary", id="dl-selected"),
                    id="buttons",
                ),
                id="right-panel",
            ),
            id="manga-layout",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#dl-all", Button).disabled = True
        self.query_one("#dl-selected", Button).disabled = True
        self.load_cover()
        self.fetch_chapters()

    @work(group="cover", exclusive=True, thread=True)
    def load_cover(self) -> None:
        path = None
        try:
            os.makedirs(COVER_DIR, exist_ok=True)
            path = os.path.join(COVER_DIR, f"{self.manga_id}.jpg")
            if not os.path.exists(path):
                url = self.cover_url or (
                    f"https://temp.compsci88.com/cover/fallback/{self.manga_id}.jpg"
                )
                r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
                r.raise_for_status()
                with open(path, "wb") as f:
                    f.write(r.content)
        except Exception:
            path = None
        self.app.call_from_thread(self.set_cover, path)

    def set_cover(self, path: str | None) -> None:
        cover = self.query_one("#cover-image", TextualImage)
        fallback = self.query_one("#cover-fallback", Static)
        image = None
        if path and os.path.exists(path):
            try:
                image = PILImage.open(path)
            except Exception:
                image = None
        cover.image = image
        cover.display = image is not None
        fallback.display = image is None

    @work(group="chapters", exclusive=True, thread=True)
    def fetch_chapters(self) -> None:
        try:
            pairs = get_chapters(self.manga_id)
        except Exception as e:
            self.app.call_from_thread(self.update_status, f"Failed to fetch chapters: {e}")
            return
        self.app.call_from_thread(self.populate_list, pairs)

    def populate_list(self, pairs: list[tuple[str, str]]) -> None:
        self.all_chapters = pairs
        picker = self.query_one("#picker", SelectionList)
        picker.clear_options()
        for cid, name in pairs:
            picker.add_option(Selection(name, cid))
        self.update_status(f"Found {len(pairs)} chapters.")
        self.query_one("#dl-all", Button).disabled = False
        self.query_one("#dl-selected", Button).disabled = False

    def update_status(self, msg: str) -> None:
        self.query_one("#status", Static).update(msg)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        b = event.button.id
        if b == "cancel":
            self.app.pop_screen()
            if isinstance(self.app.screen, SearchScreen):
                self.app.screen.clear_input()
        elif b == "dl-all":
            ids = [cid for cid, _ in self.all_chapters]
            self.app.push_screen(DownloadScreen(self.manga, ids, self.manga_name))
        elif b == "dl-selected":
            picker = self.query_one("#picker", SelectionList)
            selected = set(picker.selected)
            if not selected:
                return
            ids = [cid for cid, _ in self.all_chapters if cid in selected]
            self.app.push_screen(DownloadScreen(self.manga, ids, self.manga_name))


class DownloadScreen(Screen):
    def __init__(self, manga, chosen_ids: list[str], name: str) -> None:
        super().__init__()
        self.manga = manga
        self.chosen_ids = chosen_ids
        self.manga_name = name

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static(f"Downloading {self.manga_name}", id="dl-title"),
            Static("Preparing...", id="status"),
            ProgressBar(id="progress", total=100),
            Button("Done", variant="success", id="done"),
            id="dl-box",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#done", Button).display = False
        self.query_one("#progress", ProgressBar).update(
            total=len(self.chosen_ids), progress=0
        )
        self.run_download(self.chosen_ids)

    @work(group="download", exclusive=True, thread=True)
    def run_download(self, ids: list[str]) -> None:
        self.manga.manga_downloader(
            chosen_ids=ids,
            progress_callback=lambda c, t: self.app.call_from_thread(
                self.update_progress, c, t
            ),
            status_callback=lambda m: self.app.call_from_thread(
                self.update_status, m
            ),
        )
        self.app.call_from_thread(self.after_download)

    def after_download(self) -> None:
        self.update_status("Download complete. Converting to PDF...")
        self.convert_pdf()

    @work(group="pdf", exclusive=True, thread=True)
    def convert_pdf(self) -> None:
        try:
            utils.convert2pdf()
            self.app.call_from_thread(self.update_status, "Done! PDFs saved to Books/")
        except Exception as e:
            self.app.call_from_thread(
                self.update_status, f"PDF conversion failed: {e}"
            )
        self.app.call_from_thread(self.show_done)

    def update_progress(self, completed: int, total: int) -> None:
        self.query_one("#progress", ProgressBar).update(
            total=total, progress=completed
        )
        self.update_status(f"Downloaded {completed}/{total} chapters...")

    def update_status(self, msg: str) -> None:
        self.query_one("#status", Static).update(msg)

    def show_done(self) -> None:
        self.query_one("#progress", ProgressBar).display = False
        done = self.query_one("#done", Button)
        done.display = True
        done.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "done":
            self.app.pop_screen()
            self.app.pop_screen()
            if isinstance(self.app.screen, SearchScreen):
                self.app.screen.clear_input()


class ComicApp(App):
    TITLE = "Comic Downloader"
    BINDINGS = [("ctrl+q", "quit", "Quit")]

    CSS = """
    SearchScreen {
        align: center middle;
    }
    #search-box {
        width: 60%;
        height: auto;
        border: round $primary;
        background: $panel;
        padding: 2 3;
    }
    #search-title {
        height: auto;
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
    }
    #search-input {
        width: 100%;
    }
    #suggestions {
        width: 100%;
        max-height: 12;
        margin-top: 1;
        border: solid $surface;
    }

    #manga-layout {
        height: 1fr;
        margin: 0 1;
    }
    #left-panel {
        width: 2fr;
        height: 100%;
        padding: 1;
    }
    #right-panel {
        width: 3fr;
        height: 100%;
        padding: 1 2;
    }
    #manga-name {
        height: 3;
        text-align: center;
        text-style: bold;
        color: $primary;
    }
    #cover {
        height: 1fr;
        border: round $primary;
        padding: 1;
        align: center middle;
        overflow: hidden;
    }
    #cover-image {
        width: auto;
        height: 100%;
    }
    #cover-fallback {
        color: $text-muted;
        text-style: italic;
    }
    #status {
        height: 1;
        padding: 0 1;
    }
    #hint {
        height: 1;
        padding: 0 1;
        color: $text-muted;
    }
    #picker {
        height: 1fr;
        border: solid $primary;
        margin-top: 1;
    }
    #buttons {
        height: auto;
        align: center middle;
        padding: 1;
    }
    #buttons Button {
        margin: 0 1;
    }

    DownloadScreen {
        align: center middle;
    }
    #dl-box {
        width: 60%;
        height: auto;
        border: round $primary;
        background: $panel;
        padding: 2 3;
    }
    #dl-title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
    }
    #progress {
        width: 100%;
        margin: 1 0;
    }
    #done {
        width: 50%;
        margin-top: 1;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(SearchScreen())


def main() -> None:
    ComicApp().run()


if __name__ == "__main__":
    main()
