import streamlit as st


if 'a' not in st.session_state:
    st.session_state['a'] = 3

botao1 = st.button('Aumenta a')
botao2 = st.button('Atualiza')

if botao1:
    st.session_state['a'] += 1

st.write(st.session_state['a'])