from utils import Utils
import shutil

if __name__ == "__main__":
    input_link = input("Enter the comic issue link:\n>>")
    Utils.validate_url(input_link)
    Utils.convert2pdf()
    shutil.rmtree("Cache")
    print("\nDone! All comics have been downloaded and converted to PDF. Check the 'Books' folder.\n")
    