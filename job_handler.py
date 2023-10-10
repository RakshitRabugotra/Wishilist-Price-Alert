from models import db, Products, PriceHistory
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


def fetch_routine(engine):
    # Get all the unique products and fetch their latest prices
    products = Products.query.all()
    
    for product in products:
        # Get ready with the scrapper
        scrapper = Scraper(product.url)

        # If we couldn't scrap, then we have some error
        if not scrapper.is_active:
            logger.error("Couldn't initialize the scrapper successfully")
            return 

        # Else save the data we get, and show results
        data = scrapper.get()

        # Format the data
        data, image, price = format_data(data)

        # Log that we successfully fetched the data
        logger.info(f"(routine) Data successfully fetched - data: {data['title'].strip()}")

        # Save the data to the database
        # engine.execute()
        # if write_to_database(data=data, price=price, image=image):
            # logger.info("(routine) Data updated successfully")
        
    return


if __name__ == "__main__":
    pass

    # from SQLAlchemy import create_engine
    # db_uri = r"sqlite:///./db.sqlite"
    # eng = create_engine(db_uri)

    # # Fetch and update all the records
    # fetch_routine(eng)
