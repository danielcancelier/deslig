import streamlit as st
import time

area = st.empty()

# Replace the area with some text:
area.text("Olá")

time.sleep(4)

# Replace the text with a chart:
area.empty()
area.text('Como vai ?')

time.sleep(4)

# Clear all those elements:
if st.button('aperte'):
    area.empty()
    st.write('o locooooooo')
    st.