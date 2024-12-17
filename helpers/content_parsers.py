import urllib
import urllib.request
import bs4

class BaseParser:
    
    def __init__(self):
        self.price_identifier = None
        self.price_element = None
        
    
    def get_price(self, url)-> str:
        
        if not all([self.price_element, self.price_identifier]):
            return "N/A"

        source = urllib.request.urlopen(url)
        soup = bs4.BeautifulSoup(source, "html.parser")
        print("content", soup.prettify())
        price: str = soup.find(self.price_element, class_=self.price_identifier).get_text()
        print("price is", price)
        return price

class AmazonParser(BaseParser):
    
    def __init__(self):
        self.price_element = "span"
        self.price_identifier = "a-price-whole"
        
