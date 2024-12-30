import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime


def fetch_pe_data():
    ticker = st.text_input("Enter the ticker symbol:", "AAPL").strip().upper()
    if st.button("Submit"):
        if not ticker:
            st.error("Please enter a ticker symbol to proceed.")
            return

        try:
            # Scraping de la página de estadísticas de Yahoo Finance usando BeautifulSoup
            url = f"https://finance.yahoo.com/quote/{
                ticker}/key-statistics?p={ticker}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            # convierte el contenido HTML de una página web en un objeto BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            pe_data = []
            pe_dates = []

            for table in tables:
                rows = table.find_all("tr")
                # i es el indice de la fila y row es el contenido de la fila
                for i, row in enumerate(rows):
                    # Extraer las fechas (primera fila)
                    if i == 0:
                        # th es celda de encabezado (header), td es celda de datos (data)
                        header_cols = row.find_all(["th", "td"])
                        # Ignorar la primera columna vacía y la columna "Current". Empiezo a extraer en la 3ra columna
                        for col in header_cols[2:]:
                            date_text = col.text.strip()
                            try:
                                # Convierto a formato de fecha "YYYY-MM-DD" y agrego a la lista pe_dates
                                pe_dates.append(pd.to_datetime(
                                    date_text).strftime('%Y-%m-%d'))

                            except ValueError:
                                continue

                    # Extraer los valores de "Trailing P/E"
                    cols = row.find_all("td")
                    if len(cols) > 1 and "Trailing P/E" in cols[0].text:
                        # Ignorar las primeras dos columnas (nombre y "Current")
                        for col in cols[2:]:
                            pe_text = col.text.strip()
                            try:
                                pe_data.append(float(pe_text))
                            except ValueError:
                                continue
                        print("Valores de Trailing P/E:", pe_data)

            # Verificar si las listas tienen la misma longitud
            if not pe_data or not pe_dates or len(pe_data) != len(pe_dates):
                st.error("Mismatch between P/E data and dates.")
                return

            # Crear el DataFrame
            pe_df = pd.DataFrame({
                # Invertir para mantener el orden cronológico
                # [start:end:step] por lo que [::-1] significa que los steps se hacen en sentido inverso
                "Date": pe_dates[::-1],
                "Trailing P/E": pe_data[::-1]
            })

            # Obtener precios históricos
            stock = yf.Ticker(ticker)
            price_data = stock.history(start=min(pe_dates), end=max(pe_dates))
            # Usar reset_index asegura que el índice vuelva a empezar desde 0 y que la columna de fechas sea una columna normal
            price_data.reset_index(inplace=True)
            price_data["Date"] = pd.to_datetime(
                price_data["Date"]).dt.strftime('%Y-%m-%d')

            # Buscar precios más cercanos a las fechas de los trimestres
            price_on_dates = []
            # Voy a iterar sobre la columna de fechas del dataframe pe_df
            for date in pe_df["Date"]:
                #  Se calula la diferencia entre la fecha de la fila actual y todas las fechas de price_data
                # con .iloc eso se convierte en un índice y se selecciona la fila con la diferencia más pequeña
                closest_date = price_data.iloc[
                    (pd.to_datetime(price_data["Date"]) -
                     pd.to_datetime(date)).abs().argmin()
                ]
                # Tengo un diccionario con la fecha y el precio más cercano
                price_on_dates.append({
                    "Date": date,
                    "Price": closest_date["Close"]
                })

            # Transformo la lista de diccionarios en un DataFrame
            price_df = pd.DataFrame(price_on_dates)

            # Combinar datos de P/E y precios
            combined_df = pd.merge(pe_df, price_df, on="Date")

            # Calcular cambios porcentuales
            combined_df["PE_Change(%)"] = combined_df["Trailing P/E"].pct_change() * 100
            combined_df["Price_Change(%)"] = combined_df["Price"].pct_change(
            ) * 100
            combined_df.dropna(inplace=True)  # Eliminar filas con NaN

            st.write("DataFrame:", combined_df)

            # Calcular correlación
            correlation = combined_df["PE_Change(%)"].corr(
                combined_df["Price_Change(%)"])
            st.write(f"Correlation between PE changes and Price changes: {
                     correlation:.2f}")

            # Gráfico de dispersión
            fig = px.scatter(
                combined_df,
                x="PE_Change(%)",
                y="Price_Change(%)",
                title=f"Correlation between P/E Changes and Price Changes ({
                    ticker})",
                labels={"PE_Change(%)": "P/E Change (%)",
                        "Price_Change(%)": "Price Change (%)"},
                trendline="ols"  # Agregar línea de tendencia
            )
            st.plotly_chart(fig)

        except Exception as e:
            st.error(f"An error occurred: {e}")
