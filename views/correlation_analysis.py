import datetime
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import plost

from correlations import eps, revenue_growth, trailing_pe


def app():
    # Título
    st.header("Correlation Analysis")

    variables = [
        "Revenue Growth",
        "Earnings per Share (EPS)",
        "Price-to-Earnings Ratio (P/E)",
        "Dividend Growth",
        "Trading Volume",
        "Interest Rate Changes",
        "Inflation",
        "GDP Growth",
        "Market Sentiment"
    ]

    # Create a dropdown menu
    selected_variable = st.selectbox(
        "Select a variable to analyze its correlation with price variation:",
        variables
    )

    # Display the selected variable
    st.write(f"You selected: **{selected_variable}**")
    if selected_variable == "Earnings per Share (EPS)":
        eps.eps_correlation()
    elif selected_variable == "Revenue Growth":
        revenue_growth.revenue_growth_correlation()
    elif selected_variable == "Price-to-Earnings Ratio (P/E)":
        trailing_pe.fetch_pe_data()
