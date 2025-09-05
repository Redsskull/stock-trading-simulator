from functools import total_ordering
import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from datetime import datetime
from requests.exceptions import RequestsDependencyWarning
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables from .env file
load_dotenv()
print(f"Working from: {os.getcwd()}")

from database import db
from helpers import apology, login_required, lookup, usd
from models import User, Buy

# Configure application
app = Flask(__name__)

# PRODUCTION-READY CONFIGURATION
# Configure SECRET_KEY (essential for sessions and security)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")

# Configure database with better error handling
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Render provides postgres:// but SQLAlchemy 2.0+ requires postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print(f"Using PostgreSQL (Render)")
    print(f"Database URL configured: {database_url[:20]}...")  # Print first 20 chars for debugging
else:
    # Local development fallback
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///finance.db"
    print("WARNING: DATABASE_URL not found. Using SQLite (local development)")

    # If on Render but no DATABASE_URL, that's a problem
    if os.environ.get("RENDER"):
        print("ERROR: Running on Render but DATABASE_URL is not set!")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database and migrations
db.init_app(app)
migrate = Migrate(app, db)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Function to create tables in production
def create_tables():
    """Create database tables using migrations"""
    with app.app_context():
        try:
            upgrade()  # This applies all pending migrations
            print("Database upgraded successfully!")


        except Exception as e:
            print(f"Error creating tables: {e}")
            # Don't exit the app, let it try to run anyway
            # Some migrations might fail but the app could still work

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = User.query.get(session["user_id"])
    if not user:
        return render_template("login.html")

    buys = Buy.query.filter_by(user_id=user.id).all()
    stocks = {}

    for buy in buys:
        if buy.symbol in stocks:
            stocks[buy.symbol]['shares'] += buy.shares
        else:
            try:
                price_info = lookup(buy.symbol)
                if price_info and 'price' in price_info:
                    current_price = price_info['price']
                else:
                    current_price = buy.price
            except Exception:
                current_price = buy.price

            stocks[buy.symbol] = {
                'symbol': buy.symbol,
                'shares': buy.shares,
                'price': current_price
            }

    cash = user.cash

    # This is..a  bit silly but withouit this filter I was displaying stocks that are 0
    stocks_under_or_zero = [stock for stock in stocks.values() if stock['shares'] > 0]

    total_value = sum(stock['shares'] * stock['price'] for stock in stocks_under_or_zero)
    total_value += cash

    # This is a little fun I added a greeting based on time a day
    current_time = datetime.now().hour

    return render_template("index.html", user=user, stocks=stocks_under_or_zero, cash = cash, total_value=total_value, current_time=current_time)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    stock = request.form.get("symbol")
    shares = request.form.get("shares")
    if not stock:
        return apology("Invalid stock symbol")
    if not shares:
        return apology("Number of shares must be provided")
    if not shares.isdigit():
        return apology("Number of shares must be a number")

    stock_data = lookup(stock)
    # The lookup function returns an error that evaluates as truthy, I had to check heavily here.
    if not stock_data or "error" in stock_data or "price" not in stock_data:
        return apology("Invalid stock symbol or quote not found")

    try:
        shares = int(shares)
        if shares <= 0:
            return apology("Number of shares must be a positive integer")
    except ValueError:
        return apology("Number of shares must be a valid integer")

    user = User.query.filter_by(id=session["user_id"]).first()
    if not user:
        return apology("User not found")

    price = stock_data["price"]
    total_price = price * shares
    if user.cash < total_price:
        return apology("Insufficient funds")

    try:
        user.cash -= total_price

        purchase = Buy(
            user_id=user.id,
            symbol=stock.upper(),
            shares=shares,
            price=price
        )
        db.session.add(purchase)
        db.session.commit()

        flash(f"Successfully bought {shares} shares of {stock.upper()} at ${price:.2f} each.")
        return redirect("/")

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error during purchase: {e}")
        return apology("An error occurred while processing your purchase. Please try again.")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = Buy.query.filter_by(user_id=session["user_id"]).order_by(Buy.timestamp.desc()).all()
    return render_template("history.html", transactions=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username using SQLAlchemy
        user = User.query.filter_by(username=request.form.get("username")).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(
            user.hash, request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")

    symbol = request.form.get("symbol")
    if not symbol:
        return apology("missing symbol", 400)

    quote_data = lookup(symbol)

    # Check if lookup returned an error
    if not quote_data or "error" in quote_data:
        return apology("invalid symbol or quote not found", 400)

    return render_template("quoted.html", quote=quote_data)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confirmation:
            return apology("must provide password confirmation", 400)
        elif password != confirmation:
            return apology("passwords do not match", 400)

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return apology("username already exists", 400)

        try:
            new_user = User(
                username=username,
                hash=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()

            session["user_id"] = new_user.id

            flash("Registration successful! Welcome!", "success")
            return redirect("/")

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            flash("Registration failed. Please try again.", "error")
            return redirect("/register")
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user = User.query.get(session["user_id"])
    if not user:
        return apology("user not found", 400)

    if request.method == "GET":
        owned_shares = Buy.query.filter_by(user_id=user.id).all()
        holdings = {}
        for share in owned_shares:
            symbol = share.symbol
            if symbol in holdings:
                holdings[symbol] += share.shares
            else:
                holdings[symbol] = share.shares
        holdings = {symbol: shares for symbol, shares in holdings.items() if shares > 0}
        return render_template("sell.html", holdings=holdings)

    stock = request.form.get("symbol")
    shares = request.form.get("shares")

    if not stock:
        return apology("must provide symbol", 400)
    if not shares:
        return apology("must provide shares", 400)
    try:
        shares = int(shares)
        if shares <= 0:
            return apology("shares must be positive", 400)
    except ValueError:
        return apology("shares number invalid, try again", 400)

    user = User.query.get(session["user_id"])
    if not user:
        return apology("user not found", 40)

    stock_info = lookup(stock.upper())
    if not stock_info:
        return apology("stock not found", 404)

    current_price = stock_info["price"]

    transactions = Buy.query.filter_by(user_id=user.id, symbol=stock.upper()).all()
    owned_shares = sum(transaction.shares for transaction in transactions)

    if shares > owned_shares:
        return apology("not enough shares", 400)

    try:
        purchase = Buy(
            user_id=user.id,
            symbol=stock.upper(),
            shares=-shares,
            price=current_price
        )
        user.cash += shares * current_price
        db.session.add(purchase)
        db.session.commit()

        flash(f"Successfully sold {shares} shares of {stock.upper()} at ${current_price:.2f} each.")
        return redirect("/")

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error during sale: {e}")
        return apology("An error occurred while processing your sale. Please try again.")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """
    Change user's password.
    """
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        if not old_password or not new_password or not confirm_password:
            return apology("All fields are required", 400)
        if new_password != confirm_password:
            return apology("Passwords do not match", 400)
        user = User.query.get(session["user_id"])
        if not user:
            return apology("User not found", 404)
        if not check_password_hash(user.hash, old_password):
            return apology("Incorrect password", 403)
        try:
            user.hash = generate_password_hash(new_password)
            db.session.commit()
            flash("Password changed successfully!", "success")
            return redirect("/")

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()
            flash("Password change failed. Please try again.", "error")
            return redirect("/password")
    else:
        return render_template("password.html")

@app.route("/add_cash", methods=["POST"])
@login_required
def add_cash():
    """Add cash to user's account"""
    amount = request.form.get("amount")

    if not amount:
        flash("Amount is required", "error")
        return redirect("/")

    try:
        amount = float(amount)
        if amount <= 0:
            flash("Amount must be positive", "error")
            return redirect("/")
        if amount > 15000:
            flash("Maximum deposit is $15,000", "error")
            return redirect("/")
    except ValueError:
        flash("Invalid amount", "error")
        return redirect("/")

    try:
        user = User.query.get(session["user_id"])
        if not user:
            flash("User not found", "error")
            return redirect("/")

        user.cash += amount
        db.session.commit()

        flash(f"Successfully added {amount:,.2f} to your account!")
        return redirect("/")

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding cash: {e}")
        flash("An error occurred while adding cash", "error")
        return redirect("/")

if __name__ == '__main__':
    # Only run migrations in production
    if os.environ.get("DATABASE_URL"):
        create_tables()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
