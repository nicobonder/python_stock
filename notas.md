# Trabajo con el virtual enviroment. Para eso hago:

python -m venv .venv

- Y para activarlo:
  .\.venv\Scripts\activate

* Y hay que elegir el interprete:

- Selecciona Python: Select Interpreter y elige el intérprete dentro de .venv (debería ser algo como .venv\Scripts\python.exe

* Aunque tengo ambiente virtual, para instalar algo tengo que hacer:
  pip install yfinance
* E importo con:
  import yfinance as yf

# Para salir del ambiente virtual:

deactivate

# Para iniciar la app: streamlit run main.py

# Para crear una multipage app, tenemos que tener un archivo principal desde el que vamos a llamar como funciones a cada pagina.

- En el archivo principal tengo que importar cada pagina y despues agregarla a traves de una funcion.
- Necesito una vista principal para mostrar todas las paginas

* Voy a necesitar un metodo run() para la pagina principal
* Entonces necesito al menos 3 archivos:
  1. Archivo principal: app.py: llama a la pagina principal; agrega a las otras paginas usando un metodo y usa el metodo run para correr la app.
  2. La vista principal: multiapp.py. Es una class que ademas del metodo init tiene que tener el metodo para agregar las otras paginas (recibe como params el titulo de las paginas y la funcion para apgregarlas) y tiene el metodo run() que se ejecuta en app.py y que es donde puedo poner el selector tipo menu.
  3. Las paginas individuales.

# Para modificar los colores que trae por defecto streamlit hay que modificar el archivo config.toml (ejemplo en proyecto de dashboard)

- Puedo directamente cambiar el theme poniendo: base="dark" o light

# Streamlit tiene un componente que son columnas: col1.metric que tienen el metodo metric, que acepta: un string, 2 valores y el color de los valores.

- Puedo definir el % que ocupa cada columna: c1, c2 = st.columns((7, 3)) --> seria 70% y 30%
