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
        request_object = requests.get(url=url, headers=self.HEADERS)
        # Get the content
        self.content = request_object.content

        # Make a soup object
        self.soup = BeautifulSoup(self.content, "html5lib")

        # Log the content
        logger.info(f"CONTENT for url={url}: \n{self.soup.prettify('utf-8')}")

        # Log the header
        logger.info(f"HEADERS = {str(request_object.headers)}")

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
