import datetime
import streamlit as st
import yfinance as yf
import plotly.express as px
import pandas as pd


def app():
    st.write("This is the `Two Tickers relation` page")

    # Panel de Inputs
    st.header("Choose your tickers")

    ticker1 = st.text_input(
        "Enter the first ticker for correlation analysis:", "APP").strip().upper()
    ticker2 = st.text_input(
        "Enter the second ticker for correlation analysis:", "GOOG").strip().upper()

    today = datetime.date.today()

    # Choose start date
    startDate = st.date_input("Start date: ", datetime.date(2023, 1, 1))

    # Choose end date
    endDate = st.date_input("End date: ", today)  # Por defecto, hoy

    # Ajustar la fecha de finalización si es menor que hoy
    if endDate <= today:
        endDate_adjusted = endDate + datetime.timedelta(days=1)
    else:
        endDate_adjusted = endDate

    # Botón para actualizar los gráficos
    if st.button("Submit"):
        tickers = [ticker1, ticker2]
        tickersInfo = yf.download(
            tickers, start=startDate, end=endDate_adjusted)

        # Seleccionar la columna 'Adj Close'
        df_adj_close = tickersInfo['Adj Close']

        # Resetear el índice para convertir el índice datetime en una columna
        df_adj_close = df_adj_close.reset_index()

        # Asegurarse de que la columna de fechas esté en formato datetime (parsear)
        df_adj_close['Date'] = pd.to_datetime(df_adj_close['Date'])

        # Feature: Calcular correlación entre 2 tickers
        df_changes = df_adj_close.select_dtypes(
            include=['float64', 'int']).set_index(df_adj_close['Date']).pct_change()

        if ticker1 in df_changes.columns and ticker2 in df_changes.columns:
            df_correlation = df_changes[[ticker1, ticker2]].dropna()

            # Calculamos la correlación entre los dos tickers
            correlation = df_correlation[ticker1].corr(df_correlation[ticker2])
            st.subheader("Correlation graph")

            # Crear el gráfico de dispersión para mostrar la relación
            fig_corr = px.scatter(
                df_correlation,
                x=ticker1,
                y=ticker2,
                title=f"Correlation Between {ticker1} and {
                    ticker2}: {correlation:.2f}",
                labels={ticker1: f"Percentage Change in {ticker1}",
                        ticker2: f"Percentage Change in {ticker2}"},
                trendline="ols"  # Ajusta una línea de tendencia
            )
            st.plotly_chart(fig_corr)
        else:
            st.warning(f"One or both tickers ('{ticker1}', '{
                ticker2}') not found in the data.")
