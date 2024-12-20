import streamlit as st
from mainView import MainView
from views import stock, multi_tickers, two_stocks, correlation_analysis
app = MainView()

st.markdown(
    """
    # Stock Analysis App
    
    Choose analyze one stock, the relation between 2 tickers or compare multiple tickers.
    """
)

# Agrego todas las paginas
app.add_app("Stock analysis", stock.app)
app.add_app("Two Tickers relation", two_stocks.app)
app.add_app("Multi tickers analysis", multi_tickers.app)
app.add_app("Correlation analysis", correlation_analysis.app)

# La app principal:
app.run()
