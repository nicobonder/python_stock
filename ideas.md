# \*\*\* IDEAS:

# 1. Correlacion entre crecimiento del precio de accion y alguna otra vble, tipo el crecimiento del EPS o de los revenue de los 3 trimestres anteriores.

# 2. Correlacion entre dia del mes y % de variacion. O sea grafico de 2 vbles mostrando los 31 dias del mes y el % de cambio promedio que tiene cada dia

# 3. Grafico de barras mostrando promedio de % de cambio para cada mes, asi se puede saber qué mes tiene más crecimiento o caida

# 4. Crear algun tipo de indicador como el de Zacks: elegir 3 o 4 medidas de crecimiento, ponderarlas y que el promedio de un puntaje, si está entre tal numero y tal numero, tiene una A, por ej.

# 5. Crear un screener: que sea posible aplicar varios filtros, es decir con multiples variables y valores para esas variables. Primero analizar que es lo que yo miro a la hora de elegir una accion y despues ver que mi app tenga todo eso acomodado de una forma que sea facil de encontrar.

# 6. Construir una tabla del tipo de la que tiene finviz. Para una sola accion tiene sales, dividend, sma20, sma50, eps surprise, eps next Y, etc, rsi. # Haciendo .info veo:

- trailingPE, forwardPE, trailingPegRatio, priceToSalesTrailing12Months, priceToBook, operatingMargins, returnOnAssets, earningsQuarterlyGrowth, revenueGrowth, debtToEquity, currentRatio, beta, heldPercentInsiders, heldPercentInstitutions, shortRatio, shortPercentOfFloat, buscar el resto de los datos que me interesa.

# 7. Heatmap con correlacion entre las 5 tickers que tengo en la comparacion

# 8. Heatmap mostrando correlacion entre diferentes variables. Ver si tiene sentido y se puede hacer una correlacion entre el precio, el eps, etc

# 9. Finviz tiene un heatmap con el puntaje de recomendacion de analistas. Podria hacer una lista, en el que 1 esté arriba y los 5 estén abajo. Habrá una forma de filtrar las empresas del sp 500? Tal vez con otra libreria que no sea la de yahoo?

# \*\*\* Mejoras pendientes:

# Data solo YY-MM-DD

# Debt to Equity en la tabla se ve: 291.6760 en lugar de 291,676%

# Operating Margins se ve: 0.1070 en lugar de 10.70%
