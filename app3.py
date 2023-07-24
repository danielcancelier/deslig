import streamlit as st
import pandas as pd
st.info(st.__version__)

#df = pd.DataFrame(
#    [
#       {"command": "st.selectbox", "rating": 4, "is_widget": True},
#       {"command": "st.balloons", "rating": 5, "is_widget": False},
#       {"command": "st.time_input", "rating": 3, "is_widget": True},
#   ]
#)

df = pd.read_csv('manut_prog.csv', sep=";")
# df = st.session_state.reset_index(drop=True, inplace=True)
edited_df = st.data_editor(df, key="demo_df", num_rows="dynamic", hide_index=False)

#favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
#st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

#st.subheader("Edited df")
#st.write(edited_df)

#st.subheader("Edited rows")
#edited_rows = st.session_state["demo_df"].get("edited_rows")
#st.write(edited_rows)

edited_df.to_csv('manut_prog.csv', sep=";", index=False)