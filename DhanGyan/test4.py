import yfinance as yf

# Explicitly set auto_adjust=False to retain 'Adj Close'
data = yf.download("INFY", start="2024-04-15", end="2024-04-20", auto_adjust=False)
print(data[['Open', 'High', 'Low', 'Close', 'Adj Close']])
