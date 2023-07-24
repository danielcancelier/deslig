# Importação das bibliotecas
import streamlit as st
import pandas as pd


df = pd.read_csv('manut_prog.csv', sep=";")
edited_df = st.data_editor(df, num_rows="dynamic") # hide_index=True
if st.button('Salvar alterações'):
    df.to_csv('manut_prog2.csv', sep=";")
 