import requests
import time
import os
from flask import Flask, jsonify, request
from functools import wraps
from typing import Dict, Any, Tuple

# --- Configuration ---
app = Flask(__name__)
# API URL for fetching the base rates (using USD as the base)
EXCHANGE_RATE_API_URL = "https://v6.exchangerate-api.com/v6/YOUR_API_KEY_HERE/latest/USD"
# NOTE: While the free tier might work without a key, it's highly recommended
# to sign up for a free key (from ExchangeRate-API) and use it for stability.
# For now, we'll keep the placeholder, but you can replace 'YOUR_API_KEY_HERE'
# with 'latest' if you want to try the public endpoint without a key.

CACHE_DURATION = 60  # Cache duration in seconds

# Cache storage for the exchange rates
# Stores a dictionary: {'timestamp': 1678886400, 'rates': {'EUR': 0.92, 'JPY': 150.11, ...}}
rate_cache: Dict[str, Any] = {}

def get_exchange_rates() -> Tuple[Dict[str, float], str | None]:
    """
    Fetches the latest exchange rates from the external API or uses the cache.
    Returns the rates dictionary and an error message if the fetch fails.
    """
    current_time = time.time()
    
    # 1. Check if the cache is valid
    if rate_cache and current_time < rate_cache.get('timestamp', 0) + CACHE_DURATION:
        app.logger.info("Serving rates from cache.")
        return rate_cache['rates'], None

    # 2. Cache is expired or empty, fetch new rates
    app.logger.info("Cache expired or empty. Fetching new rates...")
    try:
        response = requests.get(EXCHANGE_RATE_API_URL, timeout=5)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        
        if data.get('result') != 'success':
            error_msg = f"API returned non-success result: {data.get('error-type', 'Unknown Error')}"
            app.logger.error(error_msg)
            return {}, error_msg

        new_rates = data.get('conversion_rates', {})
        base_code = data.get('base_code', 'USD') # Should be USD in this setup

        if not new_rates:
            error_msg = "API response did not contain conversion rates."
            app.logger.error(error_msg)
            return {}, error_msg

        # Ensure the base rate (USD) is included for consistency (it should be 1.0)
        new_rates[base_code] = 1.0

        # Update the cache
        rate_cache.clear()
        rate_cache['timestamp'] = current_time
        rate_cache['rates'] = new_rates
        
        app.logger.info(f"Successfully fetched and cached {len(new_rates)} exchange rates.")
        return new_rates, None

    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching exchange rates from API: {e}"
        app.logger.error(error_msg)
        
        # 3. Use expired cache as a fallback if fetch failed
        if rate_cache:
            app.logger.warning("API fetch failed. Falling back to expired cache.")
            return rate_cache['rates'], None
        
        return {}, error_msg

def error_response(message: str, status_code: int):
    """Generates a standard error JSON response."""
    return jsonify({
        "status": "error",
        "message": message
    }), status_code

# --- API Endpoints ---

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({"status": "ok", "service": "Currency Conversion API"})

@app.route('/rates', methods=['GET'])
def get_rates():
    """Returns the currently cached exchange rates (relative to USD)."""
    rates, error = get_exchange_rates()
    
    if error and not rates:
        return error_response(f"Could not retrieve any exchange rates. {error}", 503)

    return jsonify({
        "status": "success",
        "timestamp_cached": rate_cache.get('timestamp'),
        "base_currency": "USD",
        "rates": rates
    })


@app.route('/convert', methods=['GET'])
def convert_currency():
    """
    Performs a currency conversion based on query parameters.
    Expected params: from, to, amount
    """
    try:
        # 1. Validate and Parse Input Parameters
        from_currency = request.args.get('from', '').upper()
        to_currency = request.args.get('to', '').upper()
        amount_str = request.args.get('amount')
        
        if not all([from_currency, to_currency, amount_str]):
            return error_response("Missing required query parameters: 'from', 'to', and 'amount'.", 400)
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                 return error_response("Amount must be a positive number.", 400)
        except ValueError:
            return error_response("'amount' parameter must be a valid number.", 400)

        # 2. Get Exchange Rates (with caching logic)
        rates, error = get_exchange_rates()
        
        if error and not rates:
            return error_response(f"Could not retrieve exchange rates needed for conversion. {error}", 503)

        # 3. Validate Currencies
        if from_currency not in rates:
            return error_response(f"Source currency '{from_currency}' is not supported.", 400)
        if to_currency not in rates:
            return error_response(f"Target currency '{to_currency}' is not supported.", 400)

        # 4. Perform Conversion Calculation (using USD as the base)
        
        # Step A: Convert source amount to the base currency (USD)
        rate_from_usd = rates.get(from_currency, 1.0)
        amount_in_usd = amount / rate_from_usd
        
        # Step B: Convert amount in USD to the target currency
        rate_to_target = rates.get(to_currency, 1.0)
        converted_amount = amount_in_usd * rate_to_target
        
        # 5. Return Result
        return jsonify({
            "status": "success",
            "from_currency": from_currency,
            "to_currency": to_currency,
            "original_amount": amount,
            "converted_amount": round(converted_amount, 4), # Round to 4 decimal places
            "rate_used": round(rate_to_target / rate_from_usd, 6), # The direct conversion rate
            "timestamp_cached": rate_cache.get('timestamp')
        })

    except Exception as e:
        app.logger.exception("An unexpected internal server error occurred.")
        return error_response(f"Internal Server Error: {e}", 500)

# --- Server Startup ---

if __name__ == '__main__':
    # When running locally, Flask runs on 5000. In Docker, it runs on 80 (default).
    # The Dockerfile/Gunicorn configuration will determine the host and port in production.
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))