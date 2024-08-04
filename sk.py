import streamlit as st
import pandas as pd
import psycopg2
from psycopg2 import sql

# Database connection parameters
connection_params = {
    'dbname': 'defaultdb',
    'user': 'supreme',
    'password': '3Do-4GKNMvmv8AUwUCKmXw',
    'host': 'connectordector-15608.7tt.aws-us-east-1.cockroachlabs.cloud',
    'port': '26257',
    'sslmode': 'verify-full'
}

def connect_db():
    return psycopg2.connect(**connection_params)

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS renters (
            id SERIAL PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            state TEXT,
            zipcode TEXT,
            item TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lenders (
            id SERIAL PRIMARY KEY,
            username TEXT,
            password TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            state TEXT,
            zipcode TEXT,
            item TEXT
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def save_data(role, username, password, email, phone, city, state, zipcode, item):
    table = 'renters' if role == 'renter' else 'lenders'
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(sql.SQL("INSERT INTO {} (username, password, email, phone, city, state, zipcode, item) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)").format(sql.Identifier(table)),
                   [username, password, email, phone, city, state, zipcode, item])
    conn.commit()
    cursor.close()
    conn.close()

def search_items(item):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM renters WHERE item ILIKE %s", (f"%{item}%",))
    renters = cursor.fetchall()
    cursor.execute("SELECT * FROM lenders WHERE item ILIKE %s", (f"%{item}%",))
    lenders = cursor.fetchall()
    cursor.close()
    conn.close()
    return renters, lenders

# Create the database tables
create_tables()

# Streamlit app layout
st.set_page_config(page_title="Rentable", layout="wide", page_icon="📍")

st.title("Rentable")

role = st.radio("I am a", ("Renter", "Lender"))
username = st.text_input("Username")
password = st.text_input("Password", type="password")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
city = st.text_input("City")
state = st.text_input("State")
zipcode = st.text_input("Zipcode (County FIPS)", max_chars=5)
item = st.text_input("Item to Rent/Lend")

if st.button("Submit"):
    if username and password and email and phone and city and state and zipcode and item:
        save_data(role.lower(), username, password, email, phone, city, state, zipcode, item)
        st.success("Data successfully added.")
    else:
        st.error("Please fill in all fields.")

st.header("Search for Items")
search_item = st.text_input("Search Item")
if st.button("Search"):
    renters, lenders = search_items(search_item)
    st.subheader("Renters")
    st.write(pd.DataFrame(renters, columns=["ID", "Username", "Password", "Email", "Phone", "City", "State", "Zipcode", "Item"]))
    st.subheader("Lenders")
    st.write(pd.DataFrame(lenders, columns=["ID", "Username", "Password", "Email", "Phone", "City", "State", "Zipcode", "Item"]))
