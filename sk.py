import streamlit as st
import os

# Everything is accessible via the st.secrets dict:
st.write("DB username:", st.secrets["DB_HOST"])
