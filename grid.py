import streamlit as st
import pandas as pd

formato_colunas={
    "operadora": st.column_config.SelectboxColumn(
        "Operadora",
        help="Operadora: 0=Nenhuma  1=Claro  2=BR-Digital",
        required=True,
        default="0",
        options=[
            "0",
            "1",
            "2"
        ]
    ),
    "predio": st.column_config.SelectboxColumn(
        "Prédio",
        help="Selecione o prédio",
        width="small",
        options=[
            "CTA01",
            "CTA03",
            "CTA05",
            "CTA06",
            "CTA09"
        ]
    ),
    "inicio": st.column_config.DatetimeColumn(
        "Inicio",
        format="YYYY-MM-DD HH:mm:ss",
        step=1
    ),
    "fim": st.column_config.DatetimeColumn(
        "Fim",
        format="YYYY-MM-DD HH:mm:ss",
        step=1
    )
}

if 'df' not in st.session_state:
    st.session_state['df'] = pd.read_csv('manut_prog.csv', sep=";", parse_dates=['inicio','fim'])

df = st.data_editor(st.session_state['df'], column_config=formato_colunas, num_rows="dynamic", hide_index=True)

bt_salvar = st.button('Salvar alterações')
if bt_salvar:
    df.to_csv('manut_prog.csv', sep=";", index=False)




