import streamlit as st
import pandas as pd

def form_callback(data1, data2):    
    with open('notes.csv', 'a+') as f:    #Append & read mode
        f.write(f"{data1},{data2}\n")

with st.form(key="my_form",clear_on_submit=True):
    
    st.write("Enter Note")
    
    stock_ticker_input = st.text_input('Stock', key='ticker')
    note_input = st.text_input('Note', key='note')
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Note", note_input, "stock_ticker", stock_ticker_input)
        form_callback(stock_ticker_input,note_input)

st.info(" #### Show contents of the CSV file :point_down:")
st.dataframe(pd.read_csv("notes.csv",names=["Stock","Note"]),height=300)
