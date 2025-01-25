import datetime
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd


def app():
    # Título
    st.title("Stock Price and Correlation Analysis")

    # Panel de Inputs
    st.header("Choose your tickers")

    # Obtener los tickers seleccionados
    ticker_graph = st.text_input(
        "Enter the ticker for the price evolution graph:", "APP").strip().upper()

    today = datetime.date.today()

    # Choose start date
    startDate = st.date_input(
        "Start date: ", datetime.date(2023, 1, 1))

    # Choose end date
    endDate = st.date_input("End date: ", today)  # Por defecto, hoy

    # Ajustar la fecha de finalización si es menor que hoy
    if endDate <= today:
        endDate_adjusted = endDate + datetime.timedelta(days=1)
    else:
        endDate_adjusted = endDate

    def calculate_category_percentage(df):
        # Calcular % de cambio diario
        df['Pct_Change'] = df['Adj Close'].pct_change() * 100

        # Clasificar las categorías
        conditions = [
            df['Pct_Change'] > 2.5,
            (df['Pct_Change'] >= 0.1) & (df['Pct_Change'] <= 2.49),
            (df['Pct_Change'] >= -0.09) & (df['Pct_Change'] <= 0.09),
            (df['Pct_Change'] <= -0.1) & (df['Pct_Change'] >= -2.49),
            df['Pct_Change'] < -2.49
        ]
        categories = ['Bull', 'Positive', 'No change', 'Negative', 'Bear']
        df['Category'] = pd.cut(
            df['Pct_Change'], bins=len(conditions), labels=categories
        )

        # Contar días en cada categoría
        counts = df['Category'].value_counts().reindex(
            categories, fill_value=0)

        # Calcular porcentajes
        total_days = counts.sum()
        percentages = (counts / total_days * 100).round(1)

        # Crear el DataFrame con los resultados
        result = pd.DataFrame({
            'Category': categories,
            'Days': counts.values,
            'Percentage': percentages.values
        })

        return result

    # Botón para actualizar los gráficos
    if st.button("Submit"):
        # Descargar datos para los tickers seleccionados
        tickers = [ticker_graph]
        tickersInfo = yf.download(
            tickers, start=startDate, end=endDate_adjusted)

        dat = yf.Ticker(ticker_graph)
        print(dat.info)

        # Validar que los datos existen
        if tickersInfo.empty or 'Adj Close' not in tickersInfo:
            st.error(f"No data available for ticker {
                     ticker_graph} in the selected date range.")
            return

        # Seleccionar la columna 'Adj Close'
        df_adj_close = tickersInfo['Adj Close']

        # Resetear el índice para convertir el índice datetime en una columna
        df_adj_close = df_adj_close.reset_index()

        # Asegurarse de que la columna de fechas esté en formato datetime (parsear)
        df_adj_close['Date'] = pd.to_datetime(df_adj_close['Date'])

        # *** DEspues agregar esta linea para convertir de nuevo a formato YY-MM-DD
        # df_adj_close['Date'] = df_adj_close['Date'].dt.date

        # Mostrar el DataFrame en Streamlit
        st.write(df_adj_close)

        # Gráfico para el ticker seleccionado
        if ticker_graph in df_adj_close.columns:
            fig_graph = go.Figure()
            fig_graph.add_trace(go.Scatter(
                x=df_adj_close['Date'], y=df_adj_close[ticker_graph], mode='lines', name=ticker_graph))
            fig_graph.update_layout(title=f"Price Evolution of {ticker_graph}",
                                    xaxis_title='Date', yaxis_title='Price')
            st.plotly_chart(fig_graph)

            df_adj_close['Pct_Change'] = df_adj_close[ticker_graph].pct_change() * \
                100
            # Asegúrate de eliminar filas NaN creadas por `pct_change()`
            df_adj_close = df_adj_close.dropna(subset=['Pct_Change'])

            # Agregar el día de la semana
            df_adj_close['Day_of_Week'] = pd.Categorical(
                pd.to_datetime(df_adj_close['Date']).dt.day_name(),
                categories=['Monday', 'Tuesday',
                            'Wednesday', 'Thursday', 'Friday'],
                ordered=True
            )

        # Calcular el promedio de variación porcentual para cada día de la semana
        avg_pct_change = df_adj_close.groupby(
            'Day_of_Week')['Pct_Change'].mean()

        # Resetear el índice para convertir los días de la semana en una columna
        avg_pct_change = avg_pct_change.reset_index()

        # Crear una columna auxiliar para asignar "Positive" o "Negative" en lugar de los colores
        avg_pct_change['Change Type'] = avg_pct_change['Pct_Change'].apply(
            lambda x: 'Positive' if x > 0 else 'Negative'
        )

        # Crear el histograma con "Positive" y "Negative" como etiquetas de color
        fig_histogram = px.bar(
            avg_pct_change,
            x='Day_of_Week',
            y='Pct_Change',
            title=f"Average Percentage Change by Day of the Week for {
                ticker_graph}",
            labels={'Pct_Change': 'Average % Change',
                    'Day_of_Week': 'Day of the Week', 'Change Type': ''},
            color='Change Type',  # Usar la columna de cambio positivo/negativo
            color_discrete_map={'Positive': 'green',
                                'Negative': 'red'}  # Mapear colores
        )

        fig_histogram.update_layout(showlegend=False)
        # Mostrar el histograma en Streamlit
        st.plotly_chart(fig_histogram)

        # Feature Heatmap
        # Extrae el mes y el día para crear una columna `Month-Day`
        df_adj_close['Month-Day'] = df_adj_close['Date'].dt.strftime('%m-%d')

        # Extrae el mes y el día para crear una columna `Month-Day`
        df_adj_close['Month'] = df_adj_close['Date'].dt.month
        df_adj_close['Day'] = df_adj_close['Date'].dt.day

        # Agrupa por `Month` y `Day` y calcula el promedio de `Pct_Change`
        avg_pct_change_by_day = df_adj_close.groupby(
            ['Month', 'Day'])['Pct_Change'].mean().reset_index()

        # Usa pivot_table para manejar posibles duplicados
        heatmap_data = avg_pct_change_by_day.pivot_table(
            index='Month',
            columns='Day',
            values='Pct_Change',
            fill_value=0
        )

        st.subheader(f"Average Daily % Change Heatmap - {ticker_graph}")
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='RdYlGn',
                zmid=0,
                colorbar=dict(
                    title="% Change",
                    len=0.7,  # Control the colorbar height
                ),
                xgap=2,  # add gap between columns
                ygap=2  # add gap between rows
            )
        )

        # Ajusta el diseño del heatmap
        fig_heatmap.update_layout(
            xaxis_title="Day of Month",
            yaxis_title="Month",
            height=450,
            width=1400,
            margin=dict(l=0, r=0, t=0, b=0),
        )

        # Ajusta el tamaño de las celdas del heatmap
        fig_heatmap.update_xaxes(
            tickmode='array',
            tickvals=list(range(1, 32)),
            ticktext=[str(day) for day in range(1, 32)]
        )
        fig_heatmap.update_yaxes(
            tickmode='array',
            tickvals=list(range(1, 13)),
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            # scaleanchor="x",  # Vincula la escala de x y y
        )

        fig_heatmap.update_xaxes(fixedrange=True)  # Block the resize feature
        fig_heatmap.update_yaxes(fixedrange=True)  # Block the resize feature

        # Mostrar el heatmap en Streamlit
        st.plotly_chart(fig_heatmap)

        # Feature 2 columnas para mostrar % de dias bull y bear
        # Verificar si los datos fueron descargados correctamente
        def classify_day(change):
            if change > 2.5:
                return "Bullish"
            elif 0.1 < change < 2.49:
                return "Positive"
            elif -0.09 < change < 0.09:
                return "No change"
            elif -2.49 < change < -0.1:
                return "Negative"
            elif change < -2.5:
                return "Bearish"

        # Asignar categorías al DataFrame
        df_adj_close['Day_Type'] = df_adj_close['Pct_Change'].apply(
            classify_day)

        # Contar el número de días de cada tipo
        day_type_counts = df_adj_close['Day_Type'].value_counts().reset_index()
        day_type_counts.columns = ['Day_Type', 'Days']

        # Calcular los porcentajes
        total_days = day_type_counts['Days'].sum()
        day_type_counts['Days %'] = (
            day_type_counts['Days'] / total_days * 100).round(2)

        # Formatear la columna 'Days %' como porcentaje
        day_type_counts['Days %'] = day_type_counts['Days %'].apply(lambda x: f"{
                                                                    x:.2f}%")

        # Agregar fila total
        day_type_counts = pd.concat([
            day_type_counts,
            pd.DataFrame({'Day_Type': ['Total'], 'Days': [
                         total_days], 'Days %': [100]})
        ], ignore_index=True)

        st.markdown(
            f"<h3 style='text-align: center;'>{
                f'Bull and Bear days % - {ticker_graph}'}</h3>",
            unsafe_allow_html=True,
        )

        # Dividir en columnas
        c1, c2 = st.columns((5, 5), vertical_alignment="top")

        # Primera columna: Tabla
        with c1:
            st.table(day_type_counts)

        # Crear el donut chart con Plotly
        # Segunda columna: Donut chart
        with c2:
            fig = px.pie(
                day_type_counts[:-1],  # Excluir la fila "Total" del gráfico
                values='Days',
                names='Day_Type',
                hole=0.3,  # Donut chart
                color_discrete_sequence=[
                    "lightgreen", "orange", "green", "red", "gray"],

            )
            # Ajustar estilo del texto dentro del gráfico
            fig.update_traces(
                textinfo="percent",
                textfont=dict(size=12, color="black",
                              family="Arial", weight="bold"),
            )
            # Ajustar la posición de la leyenda
            fig.update_layout(
                legend=dict(
                    orientation="v",  # Leyenda en orientación vertical
                    y=0.5,  # Centrado verticalmente
                    x=1.2,  # Posición a la derecha del gráfico
                    xanchor="left",
                    yanchor="middle",

                ),
                height=240,
                margin=dict(t=0, b=0, l=0, r=0)
            )

            st.plotly_chart(fig)

        # Feature monthly performance

        # Filtrar las fechas seleccionadas para asegurarnos de que los datos sean correctos
        df_adj_close = df_adj_close[
            (df_adj_close['Date'] >= pd.to_datetime(startDate)) &
            (df_adj_close['Date'] <= pd.to_datetime(endDate_adjusted))
        ]
        # Agregar columna con el mes
        df_adj_close['Month'] = pd.Categorical(
            pd.to_datetime(df_adj_close['Date']).dt.month_name(),
            categories=['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'],
            ordered=True
        )

        # Calcular el promedio de variación porcentual para cada mes
        avg_pct_change_monthly = df_adj_close.groupby(
            'Month')['Pct_Change'].mean()

        # Resetear el índice para convertir los meses en una columna
        avg_pct_change_monthly = avg_pct_change_monthly.reset_index()

        avg_pct_change_monthly['Change Type'] = avg_pct_change_monthly['Pct_Change'].apply(
            lambda x: 'Positive' if x > 0 else 'Negative'
        )

        fig = px.bar(
            avg_pct_change_monthly,
            x='Month',
            y='Pct_Change',
            title="Average % Change per Month",
            labels={'Pct_Change': 'Average % Change',
                    'Month': 'Month', 'Change Type': ''},
            text='Pct_Change',
            color='Change Type',  # Usar la columna de cambio positivo/negativo
            color_discrete_map={'Positive': 'green',
                                'Negative': 'red'}  # Mapear colores
        )

        # Asegurar orden cronológico de los meses
        fig.update_layout(
            xaxis=dict(categoryorder='array', categoryarray=[
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December']
            )
        )

        # Ajustar formato del texto y layout
        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Average % Change",
            uniformtext_minsize=8,
            uniformtext_mode='hide'
        )

        # Mostrar gráfico en Streamlit
        st.plotly_chart(fig)

    else:
        st.warning(f"Ticker '{ticker_graph}' not found in the data.")
