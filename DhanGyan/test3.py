from flask import Flask, render_template, request
import yfinance as yf
from datetime import datetime
import plotly.express as px
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    table_data = None
    fig_html = None
    error = None

    if request.method == 'POST':
        ticker_input = request.form['ticker']
        ticker = ticker_input + '.NS'
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']

        try:
            if not ticker.upper().endswith('.NS'):
                raise ValueError("Only NSE stock symbols ending with '.NS' are allowed.")

            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info
            currency = info.get('currency', None)

            if currency != 'INR':
                raise ValueError("Ticker is not in INR. Please enter a valid NSE stock ticker.")

            # Convert dates (assuming input is YYYY/MM/DD)
            try:
                start_date = datetime.strptime(start_date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
                end_date = datetime.strptime(end_date_str, '%Y/%m/%d').strftime('%Y-%m-%d')
            except ValueError:
                raise ValueError("Invalid date format. Please use YYYY/MM/DD.")

            data = yf.download(ticker, start=start_date, end=end_date)

            if not data.empty:
                data.reset_index(inplace=True)
                data['Date'] = pd.to_datetime(data['Date'])
                table_data = data.to_html(classes='table table-striped', index=False)

                # Handle potential MultiIndex for 'High' column
                high_column = ('High', ticker.replace('.NS', ''))
                high_prices = None

                if high_column in data.columns:
                    high_prices = data[high_column]
                elif 'High' in data.columns:
                    high_prices = data['High']

                if high_prices is not None:
                    fig = px.line(data, x='Date', y=high_prices, title=f'{ticker} High Prices Over Time')
                    fig_html = fig.to_html(full_html=False)
                else:
                    error = f"Error: 'High' price data not found for {ticker}. Available columns: {data.columns}"
                    print(error)

            else:
                error = "No data found for the given date range."

        except ValueError as ve:
            error = f"Validation Error: {ve}"
        except Exception as e:
            error = f"Error fetching data: {e}"

    return render_template('graph.html', table_data=table_data, fig_html=fig_html, error=error)

if __name__ == '__main__':
    app.run(debug=True)