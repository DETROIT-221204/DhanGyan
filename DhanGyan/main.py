import requests
import time
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, url_for
import yfinance as yf
import plotly.express as px
from datetime import datetime, timedelta # Corrected: Only import datetime class and timedelta

from selenium import webdriver
from selenium.webdriver.common.by import By


app = Flask(__name__)

# Read data from CSV
try:
    data_df = pd.read_csv('NSE Symbols.CSV') # Renamed to data_df to avoid conflict with 'data' variable in index function
    name_company = [{'company': data_df['Company Name'][_], 'code': data_df['Scrip'][_]} for _ in range(len(data_df))]
except FileNotFoundError:
    print("Error: CSV file 'NSE Symbols.CSV' not found.")
    name_company = []

def get_stock_price(ticker):
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

    # Fetch most active stocks
    most_active = []
    try:
        india_page = 'https://www.google.com/finance/markets/most-active?hl=en&gl=IN'
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(india_page, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        stock_elements = [stock.text.strip() for stock in soup.find_all("div", class_="ZvmM7")]
        most_active = stock_elements[:10]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching most active stocks: {e}")

    # Fetch financial news
    headlines = []
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # Ensure that the path to chromedriver is correctly set up
        # If chromedriver is not in your PATH, you might need to specify it:
        # driver = webdriver.Chrome(executable_path='/path/to/chromedriver', options=chrome_options)
        driver = webdriver.Chrome(options=chrome_options)


        url = 'https://www.google.com/finance'
        driver.get(url)
        time.sleep(3)

        anchor_elements = driver.find_elements(By.CSS_SELECTOR, "div.z4rs2b > a")
        for a in anchor_elements[:10]:
            text = a.text.strip()
            link = a.get_attribute("href")
            if text and link:
                headlines.append((text, link))
        driver.quit()
    except Exception as e:
        print(f"Error fetching financial news: {e}")
        headlines = []

    return render_template('search.html', name_company=name_company, price=price,
                           most_active=most_active, headlines=headlines)

data_df = pd.read_csv('NSE Symbols.CSV') # Renamed to data_df to avoid conflict with 'data' variable in index function
name_company1 = [{'company': data_df['Company Name'][_], 'code': data_df['Scrip'][_]} for _ in range(len(data_df))]
@app.route('/<string:company>', methods=['GET', 'POST'])
def index(company):

    table_data = None
    fig_html = None
    error = None
    scrip_code = None

    # Default date values
    end_date_obj = datetime.now()
    start_date_obj = end_date_obj - timedelta(days=365)

    # Formatted strings to display in form
    start_date_str_display = start_date_obj.strftime('%Y/%m/%d')
    end_date_str_display = end_date_obj.strftime('%Y/%m/%d')

    # Get first word of company
    first_word = company.strip().lower().split()[0]

    for entry in name_company1:
        company_first_word = entry['company'].strip().lower().split()[0]
        if company_first_word == first_word:
            scrip_code = entry['code']
            break

    if request.method == 'POST':
        ticker_input = request.form['ticker']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']
        ticker = ticker_input + '.NS'

        try:
            start_date = datetime.strptime(start_date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y/%m/%d').strftime('%Y-%m-%d')

            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            currency = info.get('currency', None)

            if currency != 'INR':
                raise ValueError("Ticker is not in INR. Please enter a valid NSE stock ticker.")

            data = yf.download(ticker, start=start_date, end=end_date)

            if not data.empty:
                data.reset_index(inplace=True)
                data['Date'] = pd.to_datetime(data['Date'])
                table_data = data.to_html(classes='table table-striped', index=False)

                if 'High' in data.columns:
                    fig = px.line(data, x='Date', y='High', title=f'{ticker} High Prices Over Time')
                    fig_html = fig.to_html(full_html=False)
                else:
                    error = f"Error: 'High' price data not found for {ticker}."
            else:
                error = "No data found for the given date range."

        except ValueError as ve:
            error = f"Validation Error: {ve}"
        except Exception as e:
            error = f"Error fetching data: {e}"
    price=get_stock_price(scrip_code)
    return render_template(
        'graph.html',
        company=company,
        scrip_code=scrip_code,
        table_data=table_data,
        fig_html=fig_html,
        error=error,
        start_date_display=start_date_str_display,
        end_date_display=end_date_str_display,
        price=price  # ✅ Added comma here
    )

if __name__ == '__main__':
    app.run(debug=True)
