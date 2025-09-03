import requests
import os

from flask import redirect, render_template, session
from functools import wraps


#This function is credited to my teacher.
def apology(message, code=400):
    """Render message as an apology to user."""

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

    return render_template("apology.html", top=code, bottom=escape(message)), code

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
    """Look up quote for symbol using Alpha Vantage API."""

    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:

        return {"error": "API key not configured"}

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol.upper()}&apikey={api_key}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()




        if "Global Quote" in data:
            quote = data["Global Quote"]

            return {
                "name": quote.get("01. symbol", symbol.upper()),
                "price": float(quote.get("05. price", 0)),
                "symbol": symbol.upper()
            }
        else:

            return {"error": "Symbol not found"}

    except requests.RequestException as e:
        print(f"Request error: {e}")
        return {"error": "Network error"}
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
        return {"error": "Data parsing error"}

#This function is credited to my teacher.
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
