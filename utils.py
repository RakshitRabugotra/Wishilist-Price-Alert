"""
Utility functions
"""
def format_price(price: str) -> int:
    # Format the item price
    price = price.replace(',', '') # Removing the commas
    price = price[:price.find('.')] # Removing the decimals

    try:
        price = int(price)
    except ValueError:
        # We need to remove the currency symbol
        price = price.split(" ")[-1]

    return price

def format_data(data: dict) -> tuple:
    # Extract the image
    image = data["image"]

    # And extract the price
    price = data["price symbol"] + " " + data["price"]
    del data["price symbol"]

    # Convert all other info to text
    for field_name, field_value in data.items():
        if isinstance(field_value, str):
            data[field_name] = field_value.strip()
        else:
            data[field_name] = field_value.text.strip()

    # Check if the item is unavailable
    availability = data["availability"]
    if "unavailable" in availability:
        data["availability"] = "Currently Unavailable"
        data["price"] = None
        price = "0"

    # Delete the [price, image] from the dictionary and pass it separately
    del data["price"]
    del data["image"]

    return (data, image, price)
