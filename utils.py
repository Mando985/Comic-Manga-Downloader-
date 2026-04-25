
class Utils:

    @staticmethod
    def validate_url(url):
        if url.startswith("https://readcomiconline.li"):
            return True
        elif url.startswith("https://weebcentral.com"):
            return True
        else:
            print("Invalid link. Please provide a link from readcomiconline.li or weebcentral.com")
    
    @staticmethod
    def convert2pdf():
        pass