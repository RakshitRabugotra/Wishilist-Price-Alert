from flask import Flask, render_template, session, redirect, jsonify, flash, url_for
from flask_wtf import FlaskForm
from flask_bcrypt import Bcrypt
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField
from wtforms.validators import DataRequired, Email, NumberRange
from job_handler import write_to_database
from models import db, User
from config import ApplicationConfig
from flask_migrate import Migrate
from scraper import Scraper
from logger import logger
from utils import format_data

# Initialize the app
app = Flask(__name__)

# Set the configurations from external object
app.config.from_object(ApplicationConfig)

# Initialize the password hash object
bcrypt = Bcrypt(app)

# Initialize the Database
db.init_app(app)
with app.app_context():
    db.create_all()
# Initialize the migrator
migrate = Migrate(app, db)


# The URL of the item to get info of
URL = ""

"""
Forms
"""
class InfoForm(FlaskForm):
    item_url = StringField("The URL of Amazon item", validators=[DataRequired()])
    submit = SubmitField()


class LoginForm(FlaskForm):
    usermail = EmailField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField()


class RegisterForm(FlaskForm):
    usermail = EmailField("Email Address", validators=[DataRequired(), Email()])
    username = StringField("Your name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField()


class TargetPriceForm(FlaskForm):
    target_price = IntegerField("Set a Target Price", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField()

"""
Endpoints
"""
@app.route("/", methods=["GET", "POST"])
def index():
    # Access the global URL
    global URL

    if session.get("user_id") is None:
        return redirect("/login")

    # Fetch the url from the page
    item_url = None
    form = InfoForm()

    # If form is validated successfully
    if form.validate_on_submit():
        item_url = form.item_url.data
        URL = item_url
        form.item_url.data = ""

    # If we have item_url on our hand, then scrap the shit out of it
    if item_url is not None and len(URL) != 0:
        return redirect("/results")

    # If we don't have any url, then just show the base index page
    return render_template("index.html", item_url=item_url, form=form)


"""
Endpoint for results
"""
@app.route("/results", methods=["GET", "POST"])
def get_results():
    # Access the global URL
    global URL

    # Target price form
    target_price = None
    targetPriceForm = TargetPriceForm()

    # If form is validated successfully
    if targetPriceForm.validate_on_submit():
        target_price = targetPriceForm.target_price.data
        targetPriceForm.target_price.data = ""
    
    # If the URL is empty then, alert the user
    if len(URL) == 0:
        return render_template("error.html", title="Invalid Routed Page", heading="No Item's URL was found", error="The URL couldn't be parsed — Try again")

    # Get ready with the scrapper
    scrapper = Scraper(URL)

    # If we couldn't scrap, then we have some error
    if not scrapper.is_active:
        return render_template("error.html", title="Scraper Error", heading="Scraper not working", error="Couldn't parse the URL")

    # Else save the data we get, and show results
    data = scrapper.get()

    # Format the data
    data, image, price = format_data(data)
    # Log that we successfully fetched the data
    logger.info(f"Data successfully fetched - data: {data['title'].strip()}")

    # Add the url of the product to the data
    data['url'] = URL

    # Save the data to the database
    if target_price is not None:
        data['target_price'] = target_price
        if write_to_database(data=data, user_id=session["user_id"], price=price, image=image):
            logger.info("Data saved to database successfully")

        if data['target_price'] is not None:
            # Alert the user that they've successfully subscribed to the item
            return render_template("confirm.html", title="Action Successful!", heading="Item is now being tracked!", message=f"The requested item ({data['title']}) is now being tracked")

    # Remove the url attribute
    del data['url']

    return render_template("results.html", data=data, image=image, price=price, form=targetPriceForm)



"""
Login and Sign-up endpoints
"""


@app.route("/register", methods=["GET", "POST"])
def register_user():
    email = None
    username = None
    password = None

    form = RegisterForm()

    if form.validate_on_submit():
        email = form.usermail.data
        username = form.username.data
        password = form.password.data

    # Check if the user already exists?
    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        logger.error(f"User already exists, Email: {email}, Username: {username}")
        # User already exists
        return jsonify({"error": "User already exists"}), 409

    # Else create a new user
    if email is not None and username is not None and password is not None:
        hashed_passwd = bcrypt.generate_password_hash(password)
        # Create a new user and add to the Database
        new_user = User(email=email, password=hashed_passwd, username=username)
        db.session.add(new_user)
        # Save the changes permanently
        db.session.commit()

        # Log the user in on new registration
        session["user_id"] = new_user.id

        logger.info(f"User logged in, Email: {email}, Username: {username}")

        # Redirect to homepage
        return redirect("/")

    return render_template("/user/register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_user():
    usermail = None
    passwd = None

    # Initialize the form
    form = LoginForm()

    # If the form is validated successfully
    if form.validate_on_submit():
        usermail = form.usermail.data
        passwd = form.password.data

        # Reset these fields
        form.password.data = ""

    # If we have user-mail and password, then check if this user exists?
    user = User.query.filter_by(email=usermail).first()

    if user is None and (usermail is not None and passwd is not None):
        # Then return an unauthorized response
        logger.error(f"User not found for email={usermail}")
        return render_template("user/login.html", form=form, error="User not found!")

    if user is not None:
        if not bcrypt.check_password_hash(user.password, passwd):
            # Unauthorized access
            logger.error(f"Password is wrong for email={usermail}")
            return render_template(
                "user/login.html", form=form, error="Password is wrong!"
            )

        # Set the session
        session["user_id"] = user.id
        # Redirect to the home page
        return redirect("/")

    # Redirect to home page
    return render_template("user/login.html", form=form)


@app.route("/logout", methods=["GET", "POST"])
def logout_user():
    # Logout the user
    session.pop("user_id", None)
    # Redirect to the home page
    return redirect("/")


"""
Scrap endpoint to fetch the product
"""


@app.route("/scrap", methods=["POST"])
def scrap_page():
    return render_template("results.html")


"""
Error handlers
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", title="404 Not Found", heading="Error - Page not found!", error="Page you're looking for is not available"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", title="500 Internal Server Error", heading="Error - Internal Server Error", error="There is some issue with the server"), 500


if __name__ == "__main__":
    app.run(debug=True)
