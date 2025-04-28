import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, url_for
import yfinance as yf
import plotly.express as px
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Read data from CSV
try:
    data = pd.read_csv('NSE Symbols.CSV')
    name_company = [{'company': data['Company Name'][_], 'code': data['Scrip'][_]} for _ in range(len(data))]
except FileNotFoundError:
    print("Error: CSV file 'NSE Symbols.CSV' not found.")
    name_company = []

def get_stock_price(ticker):
    """Fetch stock price from Google Finance."""
    url = f'https://www.google.com/finance/quote/{ticker}:NSE'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find(class_='YMlKec fxKbKc')
        return price_tag.text.strip() if price_tag else "Price not available"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock price: {e}")
        return "Error fetching price"

@app.route('/', methods=['GET'])
def search():
    selected_ticker = request.args.get('company')
    price = get_stock_price(selected_ticker) if selected_ticker else "Select a company"

    most_active = []
    india_page = 'https://www.google.com/finance/markets/most-active?hl=en&gl=IN'
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(india_page, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        stock_elements = [stock.text.strip() for stock in soup.find_all("div", class_="ZvmM7")]

        for company in stock_elements[:10]:
            code_row = data.loc[data['Company Name'].str.contains(company, case=False, na=False), 'Scrip']
            stock_code = code_row.iloc[0] if not code_row.empty else "N/A"
            stock_price = get_stock_price(stock_code) if stock_code != "N/A" else "N/A"
            most_active.append({'Company': company, 'Code': stock_code, 'Price': stock_price})
    except requests.exceptions.RequestException as e:
        print(f"Error fetching most active stocks: {e}")

    return render_template('search.html', name_company=name_company, price=price, most_active=most_active)
@app.route('/test')
def test():
    return render_template("test.html")
# @app.route('/<string:company>/<string:code>', methods=['GET', 'POST'])
# def index(company, code):
#
#   # Accept both company and code
#     table_data = None
#     fig_html = None
#     error = None
#
#     if request.method == 'POST':
#         ticker_input = code  # Use the 'code' here, not 'company'
#         ticker = ticker_input + '.NS'
#         start_date_str = request.form['start_date']
#         end_date_str = request.form['end_date']
#
#         try:
#             if not ticker.upper().endswith('.NS'):
#                 raise ValueError("Only NSE stock symbols ending with '.NS' are allowed.")
#
#             ticker_obj = yf.Ticker(ticker)
#             info = ticker_obj.info
#             currency = info.get('currency', None)
#
#             if currency != 'INR':
#                 raise ValueError("Ticker is not in INR. Please enter a valid NSE stock ticker.")
#
#             # Convert dates (assuming input is YYYY/MM/DD)
#             try:
#                 start_date = datetime.strptime(start_date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
#                 end_date = datetime.strptime(end_date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
#             except ValueError:
#                 raise ValueError("Invalid date format. Please use YYYY/MM/DD.")
#
#             data = yf.download(ticker, start=start_date, end=end_date)
#
#             if not data.empty:
#                 data.reset_index(inplace=True)
#                 data['Date'] = pd.to_datetime(data['Date'])
#                 table_data = data.to_html(classes='table table-striped', index=False)
#
#                 # Handle potential MultiIndex for 'High' column
#                 high_prices = None
#
#                 if ('High', ticker.replace('.NS', '')) in data.columns:
#                     high_prices = data[('High', ticker.replace('.NS', ''))]
#                 elif 'High' in data.columns:
#                     high_prices = data['High']
#
#                 if high_prices is not None:
#                     fig = px.line(data, x='Date', y=high_prices, title=f'{ticker} High Prices Over Time')
#                     fig_html = fig.to_html(full_html=False)
#                 else:
#                     error = f"Error: 'High' price data not found for {ticker}. Available columns: {data.columns}"
#
#             else:
#                 error = "No data found for the given date range."
#
#         except ValueError as ve:
#             error = f"Validation Error: {ve}"
#         except Exception as e:
#             error = f"Error fetching data: {e}"
#
#     return render_template('graph.html', company=company, table_data=table_data, fig_html=fig_html, error=error)


if __name__ == '__main__':
    app.run(debug=True)