import datetime
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
import plost


def eps_correlation():
    ticker_graph = st.text_input(
        "Enter the ticker for the price evolution graph:", "AAPL"
    ).strip().upper()

    # Date selection
    today = datetime.date.today()

    # Choose start date
    startDate = st.date_input(
        "Start date: ", datetime.date(2023, 1, 1)
    )

    # Choose end date
    endDate = st.date_input(
        "End date: ", today
    )

    # Adjust end date if needed
    if endDate <= today:
        endDate_adjusted = endDate + datetime.timedelta(days=1)
    else:
        endDate_adjusted = endDate

    # Submit Button
    if st.button("Submit"):
        if not ticker_graph:
            st.error("Please enter a valid ticker.")
        else:
            try:

                # Descargar datos de precios
                stock_data = yf.download(
                    ticker_graph, start=startDate, end=endDate_adjusted, progress=False
                )

                ticker = yf.Ticker(ticker_graph)
                print(ticker.info)

                # We analyze the information provided in the Earnings History section at Analysis tab.

                earnings_history = ticker.earnings_history  # Es una lista de diccionarios
                print("earnings_history: ", earnings_history)

                # Convertir a DataFrame y asegurarse de incluir el índice como columna
                earnings_dates = pd.DataFrame(earnings_history).reset_index()
                if not earnings_history.empty:
                    earnings_dates = earnings_dates.rename(columns={"index": "Date"})[
                        ["Date", "epsActual"]]
                    earnings_dates.columns = ["Date", "EPS"]

                    # Convertir las fechas a formato datetime
                    earnings_dates["Date"] = pd.to_datetime(
                        earnings_dates["Date"])
                    print("earnings_dates", earnings_dates)

                    # Alinear precios con fechas de EPS
                    prices_on_earnings_dates = stock_data['Adj Close'].reindex(
                        earnings_dates["Date"], method="nearest"
                    )
                    # Asegurarse de que prices_on_earnings_dates sea una Serie unidimensional
                    prices_on_earnings_dates = prices_on_earnings_dates.squeeze()
                    print("prices_on_earnings_dates", prices_on_earnings_dates)

                    # Calcular variaciones porcentuales
                    eps_change = earnings_dates["EPS"].pct_change(
                    ).dropna() * 100
                    price_change = prices_on_earnings_dates.pct_change().dropna() * 100
                    # Crear DataFrame para mostrar cambios con índices consistentes
                    changes_df = pd.DataFrame({
                        "EPS Change (%)": eps_change.values,
                        "Price Change (%)": price_change.values
                    }, index=earnings_dates["Date"].iloc[1:])

                    st.write("Percentage changes:")
                    st.write(changes_df)

                    # Calcular correlación
                    correlation = changes_df["EPS Change (%)"].corr(
                        changes_df["Price Change (%)"])
                    st.write(f"Correlation between price change and EPS: **{
                        correlation:.2f}**")

                    # Gráfico de dispersión
                    fig = px.scatter(
                        changes_df,
                        x="EPS Change (%)",
                        y="Price Change (%)",
                        title="Correlation between EPS changes and Price",
                        labels={
                            "EPS Change (%)": "EPS Change (%)", "Price Change (%)": "Price Change (%)"},
                        trendline="ols"
                    )
                    st.plotly_chart(fig)
                else:
                    st.error("No results were found for the requested dates.")
            except Exception as e:
                st.error(f"An error occurred: {e}")
