import streamlit as st
import pandas as pd
import pymysql
from sshtunnel import SSHTunnelForwarder
from datetime import datetime, time
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, AgGridTheme
#from st_aggrid import AgGrid
#from st_aggrid.grid_options_builder import GridOptionsBuilder 

def conecta_ssh():
    if st.secrets["ssh_host"] != 'localhost':
        try:
            server = SSHTunnelForwarder(
                st.secrets["ssh_host"],
                ssh_username=st.secrets["ssh_username"],
                ssh_password=st.secrets["ssh_password"],
                remote_bind_address=('127.0.0.1', 3306)
            )
            
            server.start()
            return server
        except Exception as e:
            st.error(f"Não foi possível conectar via SSH: {e}")
            return None, None
    else:
        return 'localhost'


def conecta_bd(server):
    if st.secrets["ssh_host"] != 'localhost':
        Port = server.local_bind_port
    else:
        Port = 3306
    try:
        db = pymysql.connect(
            host= st.secrets["db_host"],
            database=st.secrets["db_database"],
            port=Port,
            user= st.secrets["db_username"],
            password=st.secrets["db_password"] 
            )
        cursor = db.cursor(pymysql.cursors.DictCursor)
        return db, cursor
    except Exception as e:
        st.error(f"Não foi possível conectar ao banco de dados: {e}")
        return None, None

def fecha_bd(db):
    try:
        db.close()
        print ('fechando db...')
    except Exception as e:
        st.warning(f"Erro ao fechar conexão com o banco de dados: {e}")

def desconecta_ssh(server):
    if st.secrets["ssh_host"] != 'localhost':
        try:
            server.stop()
            print ('fechando ssh...')
        except Exception as e:
            st.warning(f"Erro ao desconectar do servidor SSH: {e}")
    
#######################################

def intro():

    st.write("# EAT Curitiba")
    st.sidebar.success("Selecione uma opção acima")

    st.markdown(
        """
        
        **👈 Clique no menu lateral para as opções

        ### Cadastro de datas de desligamentos programados :department_store: :wrench: 

        Finalidade: informar as datas de desligamentos programados na rede Man Curitiba.

        Causas banco:  manutenção de nossa rede.

        Causas operadora: intervenções da operadora (troca de equipamentos, cabeamento, fibra, etc)
    """
    )
    return None


def inclui():
    # Página web com o formulário para inclusão dos dados
    st.write('# Inclusão')

    str_hi = '08:00'
    str_hf = '18:00'
    hora_inicio_padrao = time.fromisoformat(str_hi)
    hora_fim_padrao = time.fromisoformat(str_hf)

    # Recebe os dados do formulário
    causa_banco = st.selectbox('Causa Banco:', [False, True])
    operadora = st.selectbox('Operadora:', ['0', '1', '2'])
    predio = st.selectbox('Prédio:', ['Selecione','CTA01', 'CTA03', 'CTA05', 'CTA06', 'CTA09','SJP01'])
    data_inicio = st.date_input('Data de início:')
    hora_inicio = st.time_input('Hora de início:', value=hora_inicio_padrao)
    data_fim = st.date_input('Data de fim:')
    hora_fim = st.time_input('Hora de fim:', value=hora_fim_padrao)
    justificativa = st.text_area('Justificativa:')
    funci = st.text_input('Funcionário:', max_chars=8)

    # Concatena data_inicio e hora_inicio
    inicio = datetime.combine(data_inicio, hora_inicio)

    # Concatena data_fim e hora_fim
    fim = datetime.combine(data_fim, hora_fim)

    # Botão de confirmação para gravar os dados
    if st.button('Gravar'):
        # Insere os dados na tabela
        log_gravado = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        server = conecta_ssh()
        if server:
            db, cursor = conecta_bd(server)
            try:
                cursor.execute("""
                    INSERT INTO manut_prog (causa_banco, operadora, predio, inicio, fim, justificativa, funci, log_gravado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (causa_banco, operadora, predio, inicio, fim, justificativa, funci, log_gravado))
                db.commit()
                st.success("Inclusão realizada com sucesso")
                
            except Exception as e:
                db.rollback()
                st.error(f'Erro ao gravar os dados: {e}')
        fecha_bd(db)
        desconecta_ssh(server)
        return None


def exclui():
    st.title("Exclusão")
    server = conecta_ssh()
    if server:
        db, cursor = conecta_bd(server)
        query = "SELECT * FROM manut_prog ORDER BY log_gravado DESC"
        df = pd.read_sql(query, db)
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_pagination (enabled=True)
        gd.configure_default_column(editable=False, groupable=True)
        gd.configure_selection (selection_mode='single', use_checkbox=True)
        gridoptions = gd.build()

        grid_table = AgGrid (df, 
                             gridOptions=gridoptions,
                             theme = AgGridTheme.BALHAM, # Only choices: AgGridTheme.STREAMLIT, AgGridTheme.ALPINE, AgGridTheme.BALHAM, AgGridTheme.MATERIAL
                             columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
                             )
        
        sel_row = grid_table['selected_rows']

        if sel_row:
            str_id = (sel_row[0]['id'])
            id_sel = int(str_id)

        # Botão de exclusão
        if st.button('Excluir'):
            if id_sel > 0:
                delete_query = f"DELETE FROM manut_prog WHERE id = {id_sel}"
                cursor.execute(delete_query)
                db.commit()
                st.success("Linha excluída com sucesso")
            else:
                st.warning("Nenhuma linha selecionada")

    fecha_bd(db)
    desconecta_ssh(server)
    return None


itens_menu = {
    "Selecione": intro,
    "Incluir": inclui,
    "Excluir": exclui
}

escolha = st.sidebar.selectbox("Escolha uma opção", itens_menu.keys())
itens_menu[escolha]()