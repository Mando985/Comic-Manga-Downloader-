import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from scrapy import Selector


class weebcentral:
    def __init__(self, id):
        self.id = id

    def get_issue_links(self,id):
        url = f"https://weebcentral.com/series/{id}/full-chapter-list"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }

        res = requests.get(url, headers=headers)
        res = res.text

        selector = Selector(text=res)
        links = selector.css("a[href*='/chapters/']::attr(href)").getall()
        issue_ids = [i.split("/")[-1] for i in links]
        return issue_ids

    def chosen_links(self, chosen_ids: list[str] | None = None) -> list[str]:
        """Return either the ids the user picked, or every chapter if none were passed."""
        all_ids = self.get_issue_links(self.id)
        if chosen_ids is None:
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

    def manga_downloader(self,chosen_ids: list[str] | None = None, progress_callback=None, status_callback=None):
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
