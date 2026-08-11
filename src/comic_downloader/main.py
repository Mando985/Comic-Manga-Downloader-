from comic_downloader.weebcentral import weebcentral
from comic_downloader.utils import utils
def main():
    manga=weebcentral("01J76XYCERXE60T7FKXVCCAQ0H")
    manga.manga_downloader()
    utils.convert2pdf()
    
    

if __name__ == "__main__":
    main()