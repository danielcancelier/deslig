import streamlit as st
import pandas as pd
import pymysql
from sshtunnel import SSHTunnelForwarder
from datetime import datetime, time

def conecta_ssh():
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

def conecta_bd(server):    
    try:
        db = pymysql.connect(
            host= st.secrets["db_host"],
            user= st.secrets["db_username"],
            password=st.secrets["db_password"],
            database=st.secrets["db_database"],
            # port=server.local_bind_port
            ssl_ca='.streamlit/DigiCertGlobalRootG2.crt.pem',
            # ssl_ca='DigiCertGlobalRootG2.crt.pem',
            ssl_disabled=False
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
        if st.secrets["ssh_host"]=='azure':
            server = True
        else:
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
        # desconecta_ssh(server)

        
        
def exclui():
    st.title("Exclusão")

    if st.secrets["ssh_host"]=='azure':
        server = True
    else:
        server = conecta_ssh()
    if server:
        
        db, cursor = conecta_bd(server)
        if cursor:
            query = "SELECT * FROM manut_prog ORDER BY log_gravado DESC"
            df = pd.read_sql(query, db)
                
            # Exibe o DataFrame pandas na tela usando o Streamlit
            st.dataframe(df)

            # Adiciona um componente Selectbox para permitir ao usuário selecionar qual linha deseja excluir
            row_to_delete = st.selectbox("Selecione a linha que deseja excluir:", options=df.index.tolist())

            # Adiciona um botão para executar a exclusão da linha selecionada
            if st.button("Excluir linha"):
                # Executa a exclusão da linha selecionada
                id_to_delete = df.loc[row_to_delete]['id']
                delete_query = f"DELETE FROM manut_prog WHERE id = {id_to_delete}"
                cursor.execute(delete_query)
                db.commit()                        
                st.success("Linha excluída com sucesso")

    fecha_bd(db)
    # desconecta_ssh(server)
            
    return None

def data_frame_demo():
    import altair as alt

    from urllib.error import URLError

    st.markdown(f"# {list(page_names_to_funcs.keys())[3]}")
    st.write(
        """
        This demo shows how to use `st.write` to visualize Pandas DataFrames.

(Data courtesy of the [UN Data Explorer](http://data.un.org/Explorer.aspx).)
"""
    )

    @st.cache_data
    def get_UN_data():
        AWS_BUCKET_URL = "http://streamlit-demo-data.s3-us-west-2.amazonaws.com"
        df = pd.read_csv(AWS_BUCKET_URL + "/agri.csv.gz")
        return df.set_index("Region")

    try:
        df = get_UN_data()
        countries = st.multiselect(
            "Choose countries", list(df.index), ["China", "United States of America"]
        )
        if not countries:
            st.error("Please select at least one country.")
        else:
            data = df.loc[countries]
            data /= 1000000.0
            st.write("### Gross Agricultural Production ($B)", data.sort_index())

            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(
                columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
            )
            chart = (
                alt.Chart(data)
                .mark_area(opacity=0.3)
                .encode(
                    x="year:T",
                    y=alt.Y("Gross Agricultural Product ($B):Q", stack=None),
                    color="Region:N",
                )
            )
            st.altair_chart(chart, use_container_width=True)
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**

            Connection error: %s
        """
            % e.reason
        )

itens_menu = {
    "Selecione": intro,
    "Incluir": inclui,
    "Excluir": exclui,
    "DataFrame Demo": data_frame_demo
}

escolha = st.sidebar.selectbox("Escolha uma opção", itens_menu.keys())
itens_menu[escolha]()