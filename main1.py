import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
#import seaborn as sns
import base64


#header= st.container()
st.title('Contaminantes del aire en Lima Metropolitana')

#features=st.container()
st.markdown("""
	Esta app exploratoria permite visualizar los datos de contaminantes del aire en Lima Metropolitana
	* **Librerías Python:** base64, pandas, streamlit
	* **Base de datos:** [Servicio Nacional de Meteorología e Hidrología del Perú - SENAMHI] (https://www.datosabiertos.gob.pe/dataset/datos-horarios-de-contanimantes-del-aire-en-lima-metropolitana-servicio-nacional-de).
	""")

from PIL import Image
image = Image.open('contaminacion.jpeg')
st.image(image, caption='La contaminación por el parque automotor antiguo es un problema en Lima Metropolitana', use_column_width=True)

st.sidebar.header("Entradas del usuario")
selected_year=st.sidebar.selectbox('Año', list(reversed(range(2010,2021))))

#dataset=st.container()
st.header("Dataset SENAMHI")

def load_data(year):
	df=pd.read_csv('datos_horarios_contaminacion_lima.csv')
	#df_n=df.replace(r'^\s*$', np.nan, regex=True)
	df=df.astype({'ANO':'str'})
	df['PM 10'] = pd.to_numeric(df['PM 10'])
	df['PM 2.5'] = pd.to_numeric(df['PM 2.5'])
	df['SO2'] = pd.to_numeric(df['SO2'])
	df['NO2'] = pd.to_numeric(df['NO2'])
	df['O3'] = pd.to_numeric(df['O3'])
	df['CO'] = pd.to_numeric(df['CO'])
	grouped = df.groupby(df.ANO)
	df_year = grouped.get_group(year)
	return df_year


#visualization=st.container()
data_by_year=load_data(str(selected_year))


sorted_unique_district = sorted(data_by_year.ESTACION.unique())
selected_district=st.sidebar.multiselect('Distrito', sorted_unique_district, sorted_unique_district)

unique_contaminant=['PM 10', 'PM 2.5', 'SO2', 'NO2', 'O3', 'CO']
selected_contaminant=st.sidebar.multiselect('Contaminante', unique_contaminant, unique_contaminant)

df_selected=data_by_year[(data_by_year.ESTACION.isin(selected_district))]

def remove_columns(dataset, cols):
	return dataset.drop(cols, axis=1)

#if selected_contaminant.isin(unique_contaminant):
	#remove_columns(df_selected, selected_contaminant)

#~selected_contaminant.isin(unique_contaminant)


st.header('Mostrar data de distrito(s) y contaminante(s) seleccionado(s)')
st.write('Dimensiones: ' + str(df_selected.shape[0]) + ' filas y ' + str(df_selected.shape[1]) + ' columnas')
st.dataframe(df_selected)


def filedownload(df):
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()
	href = f'<a href="data:file/csv;base64,{b64}">Descargar archivo CSV</a> (botón derecho y guardar como ".csv")'
	return href

st.markdown(filedownload(df_selected), unsafe_allow_html=True)


if st.button('Gráfico interactivo'):
	st.header('Gráfico de barras')



