from concurrent.futures import ProcessPoolExecutor
from readcomics import ReadComicsOnline as Read
from weebcentral import WeebCentral as Weeb
from pathlib import Path
import img2pdf

def convert_issue(args):
        comic_name, issue_dir = args
        images = sorted(issue_dir.glob("*.jpg"), key=lambda p: int(p.stem))
        Path(f"Books/{comic_name}").mkdir(exist_ok=True)
        out_path = Path("Books") / comic_name / f"{comic_name}-{issue_dir.name}.pdf"
        with open(out_path, "wb") as f:
            f.write(img2pdf.convert([str(img) for img in images]))

class Utils:
    @staticmethod
    def validate_url(url):
        if url.startswith("https://readcomiconline.li"):
            Read.get_issue_links(url)
        elif url.startswith("https://weebcentral.com"):
            Weeb.get_issue_links(url)
        else:
            print("Invalid link. Please provide a link from readcomiconline.li or weebcentral.com")

    @staticmethod
    def convert2pdf():
        jobs = [
            (comic_dir.name, issue_dir)
            for comic_dir in Path("Cache").iterdir() if comic_dir.is_dir()
            for issue_dir in comic_dir.iterdir() if issue_dir.is_dir()
        ]

        with ProcessPoolExecutor() as pool:
            pool.map(convert_issue, jobs)
                    

