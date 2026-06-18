from scrapling import StealthyFetcher
import os
from concurrent.futures import ThreadPoolExecutor


def download_image(pagelists):
        issue = pagelists.split('/')[- 1].split('?')[0]
        comic_name = pagelists.split('Comic/')[- 1].split('/')[0]

        os.makedirs(f'Cache/{comic_name}/{issue}', exist_ok=True)
        page_response = StealthyFetcher.fetch(url=pagelists, headless=True,retries=6)
        image_url = str(page_response.css('#divImage img:not([style*="display: none"])::attr(src)').get())
        img_response = StealthyFetcher.fetch(image_url, headless=True,retries=6)
        with open(f"Cache/{comic_name}/{issue}/{pagelists[pagelists.index('#')+1:]}.jpg", "wb") as f:
            f.write(img_response.body)
        return True

class ReadComicsOnline:
    base_url = "https://readcomiconline.li"

    
    def download_issue(links):
        for url in links:
            url = url.strip()
            if not url.endswith("#1"):
                url = url + "#1"
            response = StealthyFetcher.fetch(url=url, headless=True,retries=6)
            values = response.css('#selectPage option::attr(value)').getall()
            page_numbers = [int(i) for i in values]
            max_page = max(page_numbers)+1

            list_of_page_numbers = [f"{url[0:url.index('#')+1]}{i}" for i in range(1, max_page + 1)]

            if os.cpu_count()==4:
                thrds=2
            else:
                thrds=(os.cpu_count()//2)+1
            with ThreadPoolExecutor(thrds) as pool:
                results = pool.map(download_image, list_of_page_numbers)
    
    @staticmethod
    def get_issue_links(url):
        response = StealthyFetcher.fetch(url=url, headless=True,retries=6)
        issue_links = response.css('table.listing tbody tr td a::attr(href)').getall()
        if issue_links==[]:
            ReadComicsOnline.download_issue([url])
        else:
            links=[f"{ReadComicsOnline.base_url}{link}" for link in issue_links]
            ReadComicsOnline.download_issue(links)

        

if __name__ == "__main__":
    url=''
    ReadComicsOnline.get_issue_links(url)