from logzero import logger
import pandas as pd
import streamlit as st
from streamlit_js_eval import get_geolocation
from opencage.geocoder import OpenCageGeocode
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

# Replace with your OpenCage API key
OPENCAGE_API_KEY = "your_opencage_api_key"
geocoder = OpenCageGeocode(OPENCAGE_API_KEY)

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
    zipcode = st.text_input("Zipcode (County FIPS)", max_chars=5)
    
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
        st.success("Data successfully added.")

    # Show user input city on the map
    if zipcode:
        city_data = florida_cities[florida_cities["county_fips"] == int(zipcode)]
        if not city_data.empty:
            latitude = city_data.iloc[0]['lat']
            longitude = city_data.iloc[0]['lng']
            st.map(pd.DataFrame([[latitude, longitude]], columns=['lat', 'lon']))
        else:
            st.warning("City not found in.")

st.write(
    """
    Hope you like the map!
    """
)
