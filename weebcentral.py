from scrapling import StealthyFetcher
import os
import requests
from concurrent.futures import ThreadPoolExecutor

def download_image(args):
    comic_name, issue, image_url = args
    pageno = image_url[image_url.rindex('-') + 1 : image_url.rindex('.png')]
    os.makedirs(f'Cache/{comic_name}/{issue}', exist_ok=True)
    response = requests.get(image_url)
    with open(f"Cache/{comic_name}/{issue}/{pageno}.jpg", "wb") as f:
        f.write(response.content)
    return True

class WeebCentral:

    @staticmethod
    def download_issue(url):
        response = StealthyFetcher.fetch(url=url, headless=True, retries=6)
        comic_name = response.css(".line-clamp-1.flex-1::text").get()
        image_urls = (response.css("img::attr(src)").getall())[2:]
        thrds = (os.cpu_count() // 2) + 1
        issue=image_urls[0][image_urls[0].rindex('/') + 1 : image_urls[0].rindex('-')]
        args = [(comic_name, issue, u) for u in image_urls]
        with ThreadPoolExecutor(thrds) as pool:
            results = list(pool.map(download_image, args))

    @staticmethod
    def get_issue_links(url):
        WeebCentral.download_issue(url)

if __name__ == "__main__":
    input_link = input("Enter the comic issue link:\n>>")
    WeebCentral.get_issue_links(input_link)