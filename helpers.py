import requests
import os

from flask import redirect, render_template, session
from functools import wraps


#This function is credited to my teacher. who themselves used this code found here - https://github.com/jacebrowning/memegen
def apology(message, code=400, redirect_to=None, delay=None):
    """Render message as an apology to user with optional timed redirect."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html",
                         top=code,
                         bottom=escape(message),
                         redirect_to=redirect_to,
                         delay=delay), code

#This function is credited to my teacher.
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def lookup(symbol):
    """Look up quote for symbol using Finnhub API."""
    api_key = os.environ.get("FINNHUB_API_KEY")
    if not api_key:
        return {"error": "API key not configured"}

    try:
        # Get stock price
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol.upper()}&token={api_key}"
        quote_response = requests.get(quote_url)
        quote_response.raise_for_status()
        quote_data = quote_response.json()

        # Get company name
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol.upper()}&token={api_key}"
        profile_response = requests.get(profile_url)
        profile_response.raise_for_status()
        profile_data = profile_response.json()

        current_price = quote_data.get("c")

        # Check if we got valid data
        if current_price is None or current_price == 0:
            return {"error": "Invalid symbol or no data available"}

        # Also check if we got a valid company name (additional validation)
        company_name = profile_data.get("name")
        if not company_name:
            return {"error": "Invalid symbol or no data available"}

        return {
            "name": profile_data.get("name", symbol.upper()),
            "price": float(quote_data.get("c", 0)),  # 'c' is current price
            "symbol": symbol.upper()
        }

    except Exception as e:
        return {"error": str(e)}

#This function is credited to my teacher.
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
