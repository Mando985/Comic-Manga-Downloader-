from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import img2pdf
import shutil

class utils:
    @staticmethod
    def convert_issue(args):
        comic_name, issue_dir = args
        images = sorted(issue_dir.glob("*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        Path(f"Books/{comic_name}").mkdir(parents=True, exist_ok=True)
        out_path = Path("Books") / comic_name / f"{comic_name}-{issue_dir.name}.pdf"
        with open(out_path, "wb") as f:
            f.write(img2pdf.convert([str(img) for img in images]))

    @staticmethod
    def convert2pdf():
        jobs = [
            (comic_dir.name, issue_dir)
            for comic_dir in Path("Cache").iterdir() if comic_dir.is_dir()
            for issue_dir in comic_dir.iterdir() if issue_dir.is_dir()
        ]

        with ProcessPoolExecutor() as pool:
            list(pool.map(utils.convert_issue, jobs))
        shutil.rmtree("Cache")