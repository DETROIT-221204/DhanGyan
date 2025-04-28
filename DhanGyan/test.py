import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

try:
    data = pd.read_csv('NSE Symbols.CSV')
    # print(data)
    name_company = [{'company': row['Company Name'], 'code': row['Scrip']} for index, row in data.iterrows()]
    # print(name_company)
except FileNotFoundError:
    print("Error: NSE Symbols.CSV file not found.")
    name_company = []  # Initialize to empty list to prevent errors later

def get_stock_price(ticker):
    url = f'https://www.google.com/finance/quote/{ticker}:NSE'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.text, 'html.parser')
        price_tag = soup.find(class_='YMlKec fxKbKc')
        return price_tag.text.strip() if price_tag else "Price not available"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching stock price for {ticker}: {e}")
        return "Price not available"
    except AttributeError:
        print(f"Error parsing stock price for {ticker}: Price element not found.")
        return "Price not available"

stock_elements = []
most_active = []
india_page = 'https://www.google.com/finance/markets/most-active?hl=en&gl=IN'
headers = {"User-Agent": "Mozilla/5.0"}

try:
    ipr = requests.get(india_page, headers=headers, timeout=10)
    ipr.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    ipsoup = BeautifulSoup(ipr.text, 'html.parser')
    mac = []
    stock_elements = [stock.text.strip() for stock in ipsoup.find_all("div", class_="ZvmM7")]
    for stock in stock_elements:
        code = None
        for item in name_company:
            if item['company'].lower() in stock.lower():
                code = item['code']
                break
        most_active_stock = {'Company': stock, 'Code': code}
        mac.append(most_active_stock)
    print(mac)  # Print the list of dictionaries
except requests.exceptions.RequestException as e:
    print(f"Error fetching most active stocks: {e}")
except AttributeError:
    print(f"Error parsing most active stocks: Element not found.")

if __name__ == '__main__':
    app.run(debug=True)