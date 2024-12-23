import datetime
import yfinance as yf
import plotly.express as px
import streamlit as st
import pandas as pd

import os
from dotenv import load_dotenv
import finnhub


# VER SI ESTÁ BIEN QUE TODO ESTO ESTE AFUERA DE LA FUNCION O SI TIENE QUE IR DENTRO
# Cargar variables del archivo .env
load_dotenv()

# Obtener la API Key desde el entorno
api_key = os.getenv("FINNHUB_API_KEY")

# Usar la API Key con Finnhub
finnhub_client = finnhub.Client(api_key=api_key)


def revenue_growth_correlation():
    ticker_graph = st.text_input(
        "Enter the ticker for the price evolution graph:", "AAPL"
    ).strip().upper()

    # Date selection
    today = datetime.date.today()

    # Choose start date
    start_date = st.date_input(
        "Start date: ", datetime.date(2023, 1, 1)
    )

    # Choose end date
    end_date = st.date_input(
        "End date: ", today
    )

    # Adjust end date if needed
    if end_date <= today:
        end_date_adjusted = end_date + datetime.timedelta(days=1)
    else:
        end_date_adjusted = end_date

    # Submit Button
    if st.button("Submit"):
        if not ticker_graph:
            st.error("Please enter a valid ticker.")
        else:
            try:
                # Obtener datos de precios desde Yahoo
                stock_data = yf.download(
                    ticker_graph, start=start_date, end=end_date_adjusted)

                # Obtener información trimestral desde Yahoo Financials
                stock = yf.Ticker(ticker_graph)
                financials = stock.quarterly_financials.T

                # Verificar que la columna "Total Revenue" esté disponible
                if "Total Revenue" not in financials.columns:
                    st.error(
                        "The 'Total Revenue' data is not available for this ticker.")
                    return

                # Crear DataFrame de ingresos
                df_earnings = financials[["Total Revenue"]].rename(
                    columns={"Total Revenue": "revenue"}
                )
                df_earnings.index = pd.to_datetime(df_earnings.index)
                df_earnings = df_earnings.sort_index()

                # Calcular el crecimiento de ingresos (%)
                df_earnings["revenue_growth"] = df_earnings["revenue"].pct_change(
                ).dropna() * 100

                # Reindexar precios para que coincidan con las fechas de ingresos
                aligned_prices = stock_data['Adj Close'].reindex(
                    df_earnings.index, method="nearest").squeeze()
                price_changes = aligned_prices.pct_change() * 100

                # Crear un DataFrame para correlación
                correlation_data = pd.DataFrame({
                    "Price Change (%)": price_changes,
                    "Revenue Growth (%)": df_earnings["revenue_growth"]
                }).dropna()

                st.write("Percentage changes:")
                st.write(correlation_data)

                # Calcular la correlación
                correlation = correlation_data.corr(
                ).loc["Price Change (%)", "Revenue Growth (%)"]
                st.write(
                    f"Correlation between Price Change and Revenue Growth: **{
                        correlation:.2f}**"
                )

                # Crear el gráfico
                fig = px.scatter(
                    correlation_data,
                    x="Price Change (%)",
                    y="Revenue Growth (%)",
                    labels={
                        "Price Change (%)": "Price Change (%)",
                        "Revenue Growth (%)": "Revenue Growth (%)"
                    },
                    title="Price Change vs Revenue Growth Correlation"
                )
                fig.update_traces(marker=dict(size=10, opacity=0.7))
                fig.update_layout(
                    xaxis_title="Price Change (%)",
                    yaxis_title="Revenue Growth (%)",
                    template="plotly_white"
                )

                # Mostrar el gráfico en Streamlit
                st.plotly_chart(fig)

            except Exception as e:
                st.error(f"An error occurred: {e}")
