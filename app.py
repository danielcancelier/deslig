import streamlit as st
import pandas as pd
import pymysql
from sshtunnel import SSHTunnelForwarder
from datetime import datetime, time
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode, AgGridTheme
import csv
import time as pause

def outras():
    st.title("Outras opções")

    # Verifica se o botão "Baixar CSV" foi clicado
    if st.button('Baixar arquivo de próximos desligamentos'):
        server = conecta_ssh()
        if server:
            db, cursor = conecta_bd(server)

            # Seleciona registros com data de início maior ou igual à data de hoje
            query = f"""
                SELECT causa_banco, operadora, predio, inicio, fim
                FROM manut_prog
                WHERE inicio >= CURDATE()
                ORDER BY inicio
            """
            cursor.execute(query)
            result = cursor.fetchall()

            fecha_bd(db)
            desconecta_ssh(server)

            # Cria o DataFrame do pandas com os resultados da consulta
            df = pd.DataFrame(result)

            # Converte o DataFrame para um CSV delimitado por ponto e vírgula
            csv_data = df.to_csv(sep=';', index=False)

            # Envia o arquivo CSV para download
            st.download_button(
                label="Clique para baixar o arquivo",
                data=csv_data,
                file_name="manut_prog.csv",
                mime="text/csv"
            )



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

    # Carrega variáveis
    Ok = True
    str_hi = '08:00'
    str_hf = '18:00'
    hora_inicio_padrao = time.fromisoformat(str_hi)
    hora_fim_padrao = time.fromisoformat(str_hf)

    # Recebe os dados do formulário
    causa_banco = st.selectbox('Causa Banco:', ['Não', 'Sim'])
    if causa_banco == 'Sim':
        nao_pede_operadora = True
    else:
        nao_pede_operadora = False 
    operadora = st.selectbox('Operadora:', ['Selecione','Embratel', 'Br-Digital'], disabled=nao_pede_operadora)
    predio = st.selectbox('Prédio:', ['Selecione','CTA01', 'CTA03', 'CTA05', 'CTA06', 'CTA09','SJP01'])
    data_inicio = st.date_input('Data de início:')
    hora_inicio = st.time_input('Hora de início:', value=hora_inicio_padrao)
    data_fim = st.date_input('Data de fim:')
    hora_fim = st.time_input('Hora de fim:', value=hora_fim_padrao)
    justificativa = st.text_area('Justificativa:')
    funci = st.text_input('Matrícula funci:', max_chars=8).upper()

    # Trata váriaveis de entrada
    if causa_banco == 'Sim':
        causa_banco = True
        operadora = 0
    else:
        causa_banco = False
        if operadora == 'Embratel':
            operadora = 1
        elif operadora == 'Br-Digital':
            operadora = 2
        else:
            st.error('Selecione uma operadora')
            Ok = False

    inicio = datetime.combine(data_inicio, hora_inicio)
    fim = datetime.combine(data_fim, hora_fim)


    # Botão de confirmação para gravar os dados
    if st.button('Gravar') and Ok==True:
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
        query = "SELECT log_gravado, funci, predio, inicio, fim, justificativa, id FROM manut_prog ORDER BY log_gravado DESC"
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
        else:
            id_sel = 0

        # Botão de exclusão
        if st.button('Excluir'):
            if id_sel > 0:
                delete_query = f"DELETE FROM manut_prog WHERE id = {id_sel}"
                cursor.execute(delete_query)
                db.commit()
                st.success("Linha excluída com sucesso")
                pause.sleep(2)
                st.experimental_rerun()
            else:
                st.warning("Nenhuma linha selecionada")

    fecha_bd(db)
    desconecta_ssh(server)
    return None


itens_menu = {
    "Selecione": intro,
    "Incluir": inclui,
    "Excluir": exclui,
    "Outras opções": outras
}
escolha = st.sidebar.selectbox("Escolha uma opção", itens_menu.keys())
itens_menu[escolha]()