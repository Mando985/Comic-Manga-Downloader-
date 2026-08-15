import shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import img2pdf


class utils:
    @staticmethod
    def convert_issue(args):
        comic_name, issue_dir = args
        images = sorted(
            issue_dir.glob("*.png"),
            key=lambda p: int(
                p.stem.split("-")[-1]
            ),  # cleans up the image name and sorts it asc order
        )
        Path(f"Books/{comic_name}").mkdir(parents=True, exist_ok=True)
        out_path = Path("Books") / comic_name / f"{comic_name}-{issue_dir.name}.pdf"
        valid = []
        for img in images:
            try:
                img2pdf.convert([str(img)])
            except (img2pdf.PdfTooLargeError, ValueError) as e:
                print(
                    f"Skipping oversized page {img}: {e}"
                )  # these kind of paes tend not to have any content in it
            else:
                valid.append(str(img))
        if valid:
            with open(out_path, "wb") as f:
                f.write(img2pdf.convert(valid))

    @staticmethod
    def convert2pdf():
        # jobs is a list of directory paths in the format [(comic name,issue name), ...]
        jobs = [
            (comic_dir.name, issue_dir)
            for comic_dir in Path("Cache").iterdir()
            if comic_dir.is_dir()
            for issue_dir in comic_dir.iterdir()
            if issue_dir.is_dir()
        ]
        # parallelly converts the images into pdfs
        with ProcessPoolExecutor() as pool:
            list(pool.map(utils.convert_issue, jobs))
        shutil.rmtree("Cache")
