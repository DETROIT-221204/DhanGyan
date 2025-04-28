import streamlit as st
import yfinance as yf
import plotly.express as px

st.title('📈 Stock Dashboard')

ticker = st.sidebar.text_input('Ticker (e.g., AAPL, INFY.NS)', 'AAPL')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')
data=yf.download(ticker,start=start_date,end=end_date )
fig=px.line(data,x=data.index,y=data['Adj Close'],title=ticker)
st.plotly_chart(fig)
# if ticker and start_date and end_date:
#     data = yf.download(ticker, start=start_date, end=end_date)
#
#     if not data.empty:
#         st.subheader(f'Closing Price of {ticker}')
#         # Access the 'Close' column using the ticker
#         fig = px.line(data, x=data.index, y=('Close', ticker), title=f'{ticker} Stock Price')
#         st.plotly_chart(fig)
#     else:
#         st.warning('No data found. Please check the ticker symbol and date range.')