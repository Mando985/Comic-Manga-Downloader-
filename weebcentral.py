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

    failed_urls=[]

    @staticmethod
    def download_issue(urls):
        for url in urls:
            try:
                response = StealthyFetcher.fetch(url=url, headless=True, retries=6)
                comic_name = response.css(".line-clamp-1.flex-1::text").get()
                
                image_urls = response.css("img::attr(src)").getall()
                cleaned_image_urls = [str(url) for url in image_urls]
                cleaned_image_urls = [url for url in cleaned_image_urls if url.startswith("https://")]
                
                # Guard: Check images exist
                if not cleaned_image_urls:
                    print(f"[WARN] No image URLs found for chapter {url}. Skipping.")
                    WeebCentral.failed_urls.append(url)
                    continue
                
                # Guard: Safely parse issue number from first image URL
                try:
                    first_url = cleaned_image_urls[0]
                    if '-' not in first_url:
                        print(f"[WARN] Invalid image URL format (no dash): {first_url}. Skipping.")
                        continue
                    issue = first_url[first_url.rindex('/') + 1 : first_url.rindex('-')]
                except (ValueError, IndexError) as e:
                    print(f"[WARN] Failed to parse issue from URL: {e}. Skipping.")
                    continue
                
                thrds = (os.cpu_count() // 2) + 1
                args = [(comic_name, issue, u) for u in cleaned_image_urls]
                with ThreadPoolExecutor(thrds) as pool:
                    results = list(pool.map(download_image, args))
                
                print(f"[OK] Downloaded {len(results)} images for {comic_name} issue {issue}")
                
            except Exception as e:
                print(f"[ERROR] Failed to process chapter {url}: {type(e).__name__}: {e}")
                continue
        if WeebCentral.failed_urls!=[]:
            WeebCentral.download_issue(WeebCentral.failed_urls)

    @staticmethod
    def get_issue_links(url):
        fetcher = StealthyFetcher()

        StealthyFetcher.configure(
        adaptive=True,
        huge_tree=True
        )

        #clicks the button that loads all chapters
        def click_show_all(page):
            button = page.locator("button:has-text('Show All Chapters')")
            button.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            
            box = button.bounding_box()
            if box:
                page.mouse.click(
                    box["x"] + box["width"] / 2,
                    box["y"] + box["height"] / 2,
                    delay=100
                )
            page.wait_for_load_state("networkidle")

        response = fetcher.fetch(
            url=url,
            page_action=click_show_all
        )
        links2issues=[str(i) for i in response.css("#chapter-list a::attr(href)").getall()]
        cleaned_links=[link for link in links2issues if "https://weebcentral.com/chapters/" in link]
        
        if cleaned_links==[]:
            WeebCentral.download_issue([url])
        else:
            print(f"[INFO] Found {len(cleaned_links)} chapters. Starting downloads...")
            WeebCentral.download_issue(cleaned_links)
            
if __name__ == "__main__":
    input_link = input("Enter the comic issue link:\n>>")
    WeebCentral.get_issue_links(input_link)