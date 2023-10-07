import requests
from bs4 import BeautifulSoup

AMAZON_ITEMS = {
    "title": "span#productTitle",
    "price": "span.a-price-whole",
    "price symbol": "span.a-price-symbol",
    "availability": "div#availability",
    "image": "img#landingImage",
}


class Scrapper:
    # Headers for the request
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"
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
        # The scrapper is active
        self.is_active = True

    def get(self, items: dict = AMAZON_ITEMS):
        results = {}
        for field_name, html_element in items.items():
            # First occurrence of ID specifier '#'
            id_specifier_index = html_element.find("#")
            # First occurrence of Class specifier '.'
            class_specifier_index = html_element.find(".")
            print("CLASS-SPEC:", class_specifier_index)
            # Get the class of the element
            element_classes = None
            if class_specifier_index > 0:
                element_classes = html_element[class_specifier_index + 1 :].replace(
                    ".", " "
                )

            print("ELEMENT-CLASS: ", element_classes)
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

            print("Searching for: ", {"field": field_name, "attrs": attrs})

            # Search for this element and return the result to results
            result_object = self.soup.find(element_type, attrs=attrs)

            if element_type == "img":
                results[field_name] = result_object['src']
            else:
                results[field_name] = result_object.text

        return results
