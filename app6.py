import streamlit as st

if st.session_state.get("but_a", False):
    st.session_state.disabled = False
elif st.session_state.get("but_b", False):
    st.session_state.disabled = True

button_a = st.button('a', key='but_a')
button_b = st.button('b', key='but_b')
button_c = st.button('c', key='but_c', disabled=st.session_state.get("disabled", True))