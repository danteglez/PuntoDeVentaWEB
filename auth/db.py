import psycopg2
import streamlit as st

DB_URL = "postgresql://postgres.mbidkiuthyjlvwqnsdpl:Dokiringuillas1@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

def connect_db():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None