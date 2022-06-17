import streamlit as st
import pandas as pd
import numpy as np
import urllib.request

#@st.experimental_memo
def download_data():
   url="http://server01.labs.org.pe:2005/datos_horarios_contaminacion_lima.csv"
   filename="datos_horarios.csv"
   urllib.request.urlretrieve(url,filename)
   df=pd.read_csv('datos_horarios.csv')
   return df
st.dataframe(download_data())
