from flask import Flask, render_template, session, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from config import ApplicationConfig
from scraper import Scraper
from logger import logger

# Initialize the app
app = Flask(__name__)

# Set the configurations from external object
app.config.from_object(ApplicationConfig)


"""
Forms
"""


class InfoForm(FlaskForm):
    item_url = StringField("The URL of Amazon item", validators=[DataRequired()])
    submit = SubmitField()


"""
Endpoints
"""


@app.route("/", methods=["GET", "POST"])
def index():
    # Fetch the url from the page
    item_url = None
    form = InfoForm()

    # If form is validated successfully
    if form.validate_on_submit():
        item_url = form.item_url.data
        form.item_url.data = ""

    # If we have item_url on our hand, then scrap the shit out of it
    if item_url is not None:
        # Get ready with the scrapper
        scrapper = Scraper(item_url)

        # If we couldn't scrap, then we have some error
        if not scrapper.is_active:
            return render_template("error.html", error="Couldn't parse the URL")

        # Else save the data we get, and show results
        data = scrapper.get()
        # Log that we successfully fetched the data
        logger.info(f"Data successfully fetched - data: {data['title'].strip()}")

        # Extract the image
        image = data["image"]
        del data["image"]

        # And extract the price
        price = data["price symbol"] + " " + data["price"]
        del data["price symbol"]
        del data["price"]

        # Convert all other info to text
        for field_name, field_value in data.items():
            data[field_name] = (
                isinstance(field_value, str) and field_value or field_value.text()
            )

        # Check if the item is unavailable
        availability = data["availability"]
        if "unavailable" in availability:
            data["availability"] = "Currently Unavailable"

        return render_template("results.html", data=data, image=image, price=price)

    # If we don't have any url, then just show the base index page
    return render_template("index.html", item_url=item_url, form=form)


@app.route("/scrap", methods=["POST"])
def scrap_page():
    return render_template("results.html")


"""
Error handlers
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
