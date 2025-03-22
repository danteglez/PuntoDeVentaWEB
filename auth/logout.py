import streamlit as st

def logout():
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""
    st.rerun()