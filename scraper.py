import time, random
import requests
from bs4 import BeautifulSoup
from logger import logger

AMAZON_ITEMS = {
    "title": "span#productTitle",
    "price": "span.a-price-whole",
    "price symbol": "span.a-price-symbol",
    "availability": "div#availability",
    "image": "img#landingImage",
}


class Scraper:
    # Headers for the request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246",
        "Cookie": "session-id=260-7242982-5061968; session-id-time=2082787201l; i18n-prefs=INR; ubid-acbin=258-6130774-6861324; session-token=qKWQQoYFXt0Utzldk9NTuV0gZz+XmB70/mcHrIz/UQweVKqPR2yIqX0wjNQwd2Jsn9EaH5TsuFpFSNrvrBipLgdYVQxcm81URgZaj/NH5wfcaX6g1sf/ML31KWmu3gfr/d808xu4IkBm3w4rE8yWjdUobh3c3CsjB27q0FVbfLfg1DltV6nUQF0mhkgc9N+Q8vhVuWcEGjmXCyvIWOl2d/AF4Yf0SMudtw+MqSTd6j1JBUsDHEZvMIBVR6JPwC60RCAaDhQGnbkgB0oRmgrdmci1Zvov1QmHAbm+tPNq/iV2SqiMg+6R8acF2K+kQW2f37vhyeS1vgfa021+lSFRhs/o0La48HnH; csm-hit={}",
        "Sec-Ch-Ua": '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
        "Sec-Ch-Ua-Mobile":  "?0",
        "Sec-Ch-Ua-Platform": "Windows",
        "Sec-Ch-Ua-Platform-Version": "10.0.0",
        "Sec-Ch-Viewport-Width": "1000",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1"
    }

    # Initialize the beautiful soup
    soup = None

    # Check if we've successfully initialized the object
    is_active = False

    def __init__(self, url: str):
        self.url = url
        # Fetch using request

        # Before making a request, we will update the headers
        self.HEADERS['Cookie'] = self.HEADERS['Cookie'].format(f"tb:s-TXQXCC2MDXE6HT{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}E8Z2J|{int(time.time())}&t:{int(time.time()+10)}&adb:adblk_no")

        request_object = requests.get(url=url, headers=self.HEADERS)
        # Get the content
        self.content = request_object.content

        # Make a soup object
        self.soup = BeautifulSoup(self.content, "html5lib")

        # Log the header
        logger.info(f"HEADERS={str(request_object.headers)}")

        # The scrapper is active
        self.is_active = True

    def get(self, items: dict = AMAZON_ITEMS):
        results = {}
        for field_name, html_element in items.items():
            # First occurrence of ID specifier '#'
            id_specifier_index = html_element.find("#")
            # First occurrence of Class specifier '.'
            class_specifier_index = html_element.find(".")
            
            # Get the class of the element
            element_classes = None
            if class_specifier_index > 0:
                element_classes = html_element[class_specifier_index + 1 :].replace(
                    ".", " "
                )

            # Get the id the of the element
            element_id = None
            if id_specifier_index > 0:
                element_id = html_element[
                    id_specifier_index + 1 : (class_specifier_index == -1)
                    and len(html_element)
                    or class_specifier_index
                ]
            # Get the type of html element
            element_type = None
            if id_specifier_index != -1:
                element_type = html_element[:id_specifier_index]
            elif class_specifier_index != -1:
                element_type = html_element[:class_specifier_index]
            else:
                element_type = html_element[:]

            # Get ready with the attributes
            attrs = {"id": element_id, "class": element_classes}

            # If we don't have any ID for the element, then don't search with ID
            if attrs["id"] is None:
                del attrs["id"]
            # Same with the classes
            if attrs["class"] is None:
                del attrs["class"]

            # Log the details
            logger.info(f"Searching for: 'field': {field_name} | 'attrs': {str(attrs)}")

            # Search for this element and return the result to results
            result_object = self.soup.find(element_type, attrs=attrs)

            # Check if the element is None
            if result_object is None:
                results[field_name] = ""
                continue

            if element_type == "img":
                results[field_name] = result_object['src']
            else:
                results[field_name] = result_object.text

        return results



if __name__ == '__main__':

    from utils import format_data

    # Test scenario
    url = "https://www.amazon.in/Redmi-Black-256GB-Indias-Snapdragon/dp/B0C9JDHZTB/?_encoding=UTF8&_ref=dlx_gate_sd_dcl_tlt_bcfee803_dt&pd_rd_w=yWs7d&content-id=amzn1.sym.664f7b11-e5a2-4dd5-8d0d-db35e8ab3481&pf_rd_p=664f7b11-e5a2-4dd5-8d0d-db35e8ab3481&pf_rd_r=0QPBNNNFCJ1GEQW4C4Q4&pd_rd_wg=pwb4U&pd_rd_r=ee8ffb39-7e26-49ae-997b-1b5547e5d0ec&ref_=pd_gw_unk&th=1"

    for i in range(0, 10):
        
        scraper = Scraper(url)


        data = scraper.get()
        data, image, price = format_data(data)

        print(data)

        break
        time.sleep(2)

    

