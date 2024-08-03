from logzero import logger
import pandas as pd
import streamlit as st
from streamlit_js_eval import get_geolocation
import os

# Ensure the 'data/db.csv' file exists and has appropriate headers
if not os.path.isfile("data/db.csv"):
    df = pd.DataFrame(columns=["Username", "Password", "City", "State", "Email", "Phone", "Zipcode"])
    df.to_csv("data/db.csv", index=False)

st.set_page_config(page_title="Rentable", layout="wide", page_icon="📍")
st.markdown(
    """
    <style>
    .small-font {
        font-size:12px;
        font-style: italic;
        color: #b1a7a6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Rent")

# Load Florida cities data
florida_cities = pd.read_csv("data/Florida.csv")

loc = get_geolocation()

with st.sidebar.form(key="my_form"):
    # User input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city = st.text_input("City")
    state = st.text_input("State")
    zipcode = st.text_input("Zipcode")
    
    st.markdown(
        '<p class="small-font">Results Limited to 15 miles</p>',
        unsafe_allow_html=True,
    )
    
    pressed = st.form_submit_button("Submit")
    if st.checkbox("Refresh location"):
        loc = get_geolocation()
        st.write(f"Your coordinates are {loc}")

expander = st.sidebar.expander("Insurance")
expander.write(
    """
To be updated
"""
)

if pressed:
    if username and password and city and state and email and phone and zipcode:
        # Append data to CSV
        df = pd.DataFrame([[username, password, city, state, email, phone, zipcode]], columns=["Username", "Password", "City", "State", "Email", "Phone", "Zipcode"])
        df.to_csv("data/db.csv", mode="a", header=False, index=False)
        st.success("Data successfully added to CSV")

    # Show user input city on the map
    if zipcode:
        city_data = florida_cities[florida_cities["county_fips"] == int(zipcode)]
        if not city_data.empty:
            st.map(city_data[["lat", "lng"]])
        else:
            st.warning("City not found for the given zipcode.")

st.write(
    """
    Hope you like the map!
    """
)
