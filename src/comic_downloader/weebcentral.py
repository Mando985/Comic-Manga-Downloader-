import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from scrapy import Selector
import re


class weebcentral:
    def __init__(self, id):
        self.id = id

    # gets the list of chapters and its ids
    def get_issue_links(self, id: str) -> list[tuple[str, str]]:
        url = f"https://weebcentral.com/series/{id}/full-chapter-list"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

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
        return list(reversed(pairs))  # [(id1,chap1),(id2,chap2)...]

    def chosen_links(self, chosen_ids: list[str] | None = None) -> list[str]:
        # Return either the ids the user picked, or every chapter if none were passed.
        all_ids = [link[0] for link in self.get_issue_links(self.id)]
        if chosen_ids is None:  # chosen_id is recived from the TUI end
            return all_ids
        # preserve the site's ordering, just filter down to what was chosen
        chosen_set = set(chosen_ids)
        return [i for i in all_ids if i in chosen_set]

    def issue_downloader(self, issue_id):
        iurl = f"https://weebcentral.com/chapters/{issue_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        ires = requests.get(iurl, headers=headers)
        ires = ires.text

        selector = Selector(text=ires)

        titles = selector.css(
            "title::text"
        ).get()  # "Chapter n | Manga Title | Weeb Central"
        issue = titles.split("|")[0].strip()
        title = titles.split("|")[1].strip()

        url = f"https://weebcentral.com/chapters/{issue_id}/images?is_prev=False&reading_style=long_strip&current_page=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        res = requests.get(url, headers=headers)
        res = res.text

        selector = Selector(text=res)
        page_links = selector.css("img::attr(src)").getall()

        os.makedirs(f"Cache/{title}/{issue}", exist_ok=True)

        for i in page_links:
            try:
                img_res = requests.get(i, headers=headers)
                img_res.raise_for_status()
                filename = i.split("/")[-1].split("?")[0]
                with open(os.path.join(f"Cache/{title}/{issue}", filename), "wb") as f:
                    f.write(img_res.content)
            except Exception as e:
                print(f"[{issue_id}] failed on {i}: {e}")

    def manga_downloader(
        self,
        chosen_ids: list[str] | None = None,
        progress_callback=None,
        status_callback=None,
    ):
        # progress_callback and status_callback is for tracking the progress so the TUI can display it

        links = self.chosen_links(chosen_ids)
        total = len(links)
        completed = 0

        if status_callback:
            status_callback(f"Found {total} chapters, starting download...")

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
            futures = {pool.submit(self.issue_downloader, link): link for link in links}

            for future in as_completed(futures):
                link = futures[future]
                try:
                    future.result()
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total)
                except Exception as e:
                    if status_callback:
                        status_callback(f"Failed: {link} ({e})")

        if status_callback:
            status_callback("Download complete ")
