from models import now, get_uuid, db, Products, PriceHistory
from logger import logger
from scraper import Scraper
from utils import format_data, format_price

def write_to_database(data: dict, user_id: str, price: str, image: str):
    """
    Writes the given data to the database of products table and product history
    """
    product = Products.query.filter_by(url=data["url"]).first()

    price = format_price(price)

    # Success flag
    success = False

    # Check if the product is already listed in the table
    if product is not None:
        # If the item becomes unavailable, then set the price to 0
        if "unavailable" in data['availability'].lower():
            product.latest_price = 0
        else:
            product.latest_price = price
            product.image = image
        
        # If we also have a target price, then update it
        if data.get("target_price") is not None:
            product.target_price = data["target_price"]

        try:
            db.session.commit()
            logger.info(
                f"Data updated successfully for product-title: {data['title']}, price={data['price']}"
            )
            success = True

        except Exception as e:
            logger.error(
                f"Couldn't update record, title={data['title']}, new_price={data['price']}, error={str(e)}"
            )
            success = False

        finally:
            # Also, update the product price history table
            new_history = PriceHistory(
                product_id=product.id,
                price=product.latest_price
            )
            db.session.add(new_history)
            # Save the changes permanently
            db.session.commit()

            return success
        
    # If the product is new to the table, then add it
    # Create a new product and add to the Database
    new_product = Products(
        user_id=user_id,
        url=data["url"],
        title=data["title"],
        latest_price=price,
        target_price=data.get("target_price"),
        image=image,
    )
    db.session.add(new_product)
    # Save the changes permanently
    db.session.commit()

    # Also, update the product price history table
    new_history = PriceHistory(
        product_id=new_product.id,
        price=new_product.latest_price
    )
    db.session.add(new_history)
    # Save the changes permanently
    db.session.commit()
    
    return True


def fetch_routine():
    import sqlite3

    sqliteConnection = None
    cursor = None
    try:
        sqliteConnection = sqlite3.connect("./instance/db.sqlite")
        cursor = sqliteConnection.cursor()
        logger.info("Connection to database for fetch routine - Successful")

    except Exception as e:
        sqliteConnection = None
        cursor = None
        logger.error(f"Connection to database for fetch routine - Failed, error={str(e)}")


    # If we couldn't open the connection then return
    if sqliteConnection is None or cursor is None: return

    # Get all the unique products and fetch their latest prices
    cursor.execute("SELECT * FROM products")
    # Get all of the values in form of tuple of tuple
    products = cursor.fetchall()
    # Get all of the field values form the Products table
    fields = Products.get_fields()

    products = list(map(
        # Convert it to dict for easy access
        lambda product: dict(zip(fields, product)),
        products
    ))

    for product in products:
        # Get ready with the scrapper
        scrapper = Scraper(product['url'])

        # If we couldn't scrap, then we have some error
        if not scrapper.is_active:
            logger.error("Couldn't initialize the scrapper successfully")
            return 

        # Else save the data we get, and show results
        data = scrapper.get()

        # Format the data
        data, image, price = format_data(data)
        price = format_price(price)
        # Check if the price is not given, then make it 0
        price = int(price) if price else 0
     
        # Log that we successfully fetched the data
        logger.info(f"(routine) Data successfully fetched: data={str(data)}, price={price}")

        # Update the prices to the database
        cursor.execute(f"UPDATE products SET latest_price={price} WHERE id='{product['id']}'")
        logger.info(f"Updated price value for id={product['id']}, url={product['url']} updated latest_price={price}")

        # Update the history table
        command = f"INSERT INTO priceHistory (history_id, product_id, price, date) VALUES(?, ?, ?, ?)"
        cursor.execute(command, (get_uuid(), product['id'], price, now()))
        logger.info(f"Update history for product_id={product['id']}, price={price}")

        # Commit the changes
        sqliteConnection.commit()

    return


if __name__ == "__main__":
    # Fetch and update all the records
    fetch_routine()
