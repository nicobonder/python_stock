import yfinance as yf
import streamlit as st
import pandas as pd


def app():
    st.write("This is the `Multi tickers` page")

    # Panel de Inputs
    st.header("Choose your tickers")

    # Obtener los tickers seleccionados
    ticker1 = st.text_input(
        "Enter the first ticker for correlation analysis:", "APP").strip().upper()
    ticker2 = st.text_input(
        "Enter the second ticker for correlation analysis:", "GOOG").strip().upper()
    ticker3 = st.text_input(
        "Enter the first ticker for correlation analysis:", "NVDA").strip().upper()
    ticker4 = st.text_input(
        "Enter the second ticker for correlation analysis:", "BRK-B").strip().upper()
    ticker5 = st.text_input(
        "Enter the first ticker for correlation analysis:", "AAPL").strip().upper()

    # Función para obtener los indicadores relevantes de un ticker

    def get_ticker_data(ticker):
        dat = yf.Ticker(ticker)
        return {
            "Trailing P/E": dat.info.get("trailingPE"),
            "Forward P/E": dat.info.get("forwardPE"),
            "Trailing PEG Ratio": dat.info.get("trailingPegRatio"),
            "Price to Sales (TTM)": dat.info.get("priceToSalesTrailing12Months"),
            "Price to Book": dat.info.get("priceToBook"),
            "Operating Margins": dat.info.get("operatingMargins"),
            "Return on Assets": dat.info.get("returnOnAssets"),
            "Earnings Quarterly Growth": dat.info.get("earningsQuarterlyGrowth"),
            "Revenue Growth": dat.info.get("revenueGrowth"),
            "Debt to Equity": dat.info.get("debtToEquity"),
            "Current Ratio": dat.info.get("currentRatio"),
            "Beta": dat.info.get("beta"),
            "Held by Insiders": dat.info.get("heldPercentInsiders"),
            "Held by Institutions": dat.info.get("heldPercentInstitutions"),
            "Short Ratio": dat.info.get("shortRatio"),
            "Short % of Float": dat.info.get("shortPercentOfFloat"),
        }

    # Botón para actualizar los gráficos
    if st.button("Submit"):
        # Descargar datos para los tickers seleccionados

        # Crear un DataFrame para mostrar en la tabla
        # Obtener datos de los tickers
        st.subheader("Ticker Comparison")
        data1 = get_ticker_data(ticker1)
        data2 = get_ticker_data(ticker2)
        data3 = get_ticker_data(ticker3)
        data4 = get_ticker_data(ticker4)
        data5 = get_ticker_data(ticker5)

        comparison_data = pd.DataFrame({
            "Indicator": data1.keys(),
            ticker1: data1.values(),
            ticker2: data2.values(),
            ticker3: data3.values(),
            ticker4: data4.values(),
            ticker5: data5.values(),
        })

        # Mostrar tabla
        st.table(comparison_data)
