import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import base64
import urllib.request

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

'''
@st.experimental_memo
def download_data():
	url='http://server01.labs.org.pe:2005/datos_horarios_contaminacion_lima.csv'
	filename='datos_horarios_contaminacion_lima.csv'
	urllib.request.urlretrieve(url, filename)
	df=pd.read_csv('datos_horarios_contaminacion_lima.csv')
	return df

df=download_data()
st.dataframe(df)
df=df.astype({'ANO':'str'})
df['PM 10'] = pd.to_numeric(df['PM 10'])
df['PM 2.5'] = pd.to_numeric(df['PM 2.5'])
df['SO2'] = pd.to_numeric(df['SO2'])
df['NO2'] = pd.to_numeric(df['NO2'])
df['O3'] = pd.to_numeric(df['O3'])
df['CO'] = pd.to_numeric(df['CO'])


	
def retrieve_data(df, year):
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

data_by_year=retrieve_data(dataframe, selected_year)
'''

def load_data(year):
	df=pd.read_csv('datos_horarios_contaminacion_lima.csv')
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

cols=np.setdiff1d(unique_contaminant, selected_contaminant)

st.subheader('Mostrar data de distrito(s) y contaminante(s) seleccionado(s)')
data=remove_columns(df_selected, cols)
st.write('Dimensiones: ' + str(data.shape[0]) + ' filas y ' + str(data.shape[1]) + ' columnas')
st.dataframe(data)

#st.text(str(selected_contaminant))

def filedownload(df):
	csv = df.to_csv(index=False)
	b64 = base64.b64encode(csv.encode()).decode()
	href = f'<a href="data:file/csv;base64,{b64}">Descargar archivo CSV</a> (botón derecho y guardar como ".csv")'
	return href

st.markdown(filedownload(df_selected), unsafe_allow_html=True)

if st.sidebar.button("CSV completo"):
	st.subheader('Dataset completo')
	df=pd.read_csv('datos_horarios_contaminacion_lima.csv')
	st.write('Dimensiones: ' + str(df.shape[0]) + ' filas y ' + str(df.shape[1]) + ' columnas')
	st.dataframe(df)

if st.button('Gráfico interactivo'):
	st.header('Gráfico de líneas')
	datos=df_selected.groupby(['MES']).agg({"PM 10": 'mean', "PM 2.5": 'mean', "SO2": 'mean', "NO2": 'mean', "O3": 'mean', "CO": 'mean'})
	#datos.reset_index(inplace=True)
	#c=alt.Chart(datos, title='DISTRITO:'+" "+' '.join(selected_district)).mark_line().encode(x='MES', y='ppm:Q')
	data = datos.reset_index().melt('MES')
	data.rename(columns={'variable':'contaminante', 'value':'ppm'}, inplace=True)
	c=alt.Chart(data, title='DISTRITO:'+" "+' '.join(selected_district)).mark_line().encode(
		x='MES',
		y='ppm',
    color='contaminante')
	st.altair_chart(c, use_container_width=True)

	st.dataframe(data)

	contaminantes=['PM 10', 'PM 2.5', 'SO2', 'NO2', 'O3', 'CO']
	def getBaseChart():
		#base=alt.Chart(data).mark_line().encode(x='MES',y='ppm',color='contaminante').properties(width=500, height=400)
		base = (alt.Chart(data).encode(x=alt.X("MES:T",axis=alt.Axis(title="Mes")),y=alt.Y("ppm:Q", axis=alt.Axis(title="Concentración (ppm)")),).properties(width=500, height=400))
		return base

	def getSelection():
		cont_select = alt.selection_multi(fields=["contaminante"], name="Contaminante")
		cont_color_condition = alt.condition(cont_select, alt.Color("contaminante:N", legend=None), alt.value("lightgrey"))
		return cont_select, cont_color_condition

	def createChart():
		cont_select, cont_color_condition = getSelection()
		make_selector = (alt.Chart(data).mark_circle(size=200).encode(y=alt.Y("contaminante:N", axis=alt.Axis(title="Elija contaminante", titleFontSize=15)),color=cont_color_condition,).add_selection(cont_select))
		base = getBaseChart()
		highlight_cont = (base.mark_line(strokeWidth=2).add_selection(cont_select).encode(color=cont_color_condition)).properties(title='DISTRITO:'+" "+' '.join(selected_district))
		return base, make_selector, highlight_cont, cont_select

	def createTooltip(base, cont_select):
		nearest = alt.selection(type="single", nearest=True, on="mouseover", fields=["MES"], empty="none")
		selectors = (alt.Chart(data).mark_point().encode(x="MES:T",opacity=alt.value(0)).add_selection(nearest))
		points = base.mark_point(size=5, dy=-10).encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0))).transform_filter(cont_select)

		tooltip_text = base.mark_text(align="left",dx=-60,dy=-15,fontSize=15,fontWeight="bold",lineBreak = "\n",).encode(text=alt.condition(nearest, alt.Text("ppm:Q", format=".2f"), alt.value(" "),),).transform_filter(cont_select)
		rules = (alt.Chart(data).mark_rule(color="white", strokeWidth=1).encode(x="MES:T",).transform_filter(nearest))
		return selectors, rules, points, tooltip_text

	base, make_selector, highlight_cont, cont_select  = createChart()
	selectors, rules, points, tooltip_text  = createTooltip(base, cont_select)

	make_selector | alt.layer(highlight_cont, selectors, points,rules, tooltip_text)





