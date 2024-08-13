import streamlit as st
import pandas as pd
import json
import os
from streamlit_js_eval import get_geolocation
from opencage.geocoder import OpenCageGeocode

# File path for storing data
data_file_path = 'data.json'

# In-memory data storage
data = {
    'users': []
}

def load_data():
    """Load data from a file."""
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r') as f:
            global data
            data = json.load(f)
    else:
        save_data_to_file()

def save_data_to_file():
    """Save data to a file."""
    with open(data_file_path, 'w') as f:
        json.dump(data, f, indent=4)

def save_user(username, password, city, state, email, phone, zipcode):
    """Save user data to the in-memory data structure and file."""
    data['users'].append({
        'username': username,
        'password': password,
        'city': city,
        'state': state,
        'email': email,
        'phone': phone,
        'zipcode': zipcode
    })
    save_data_to_file()

def get_city_data(zipcode):
    """Get city data based on zipcode."""
    florida_cities = pd.read_csv("data/Florida.csv")
    city_data = florida_cities[florida_cities["county_fips"] == int(zipcode)]
    return city_data

# Load data at the start
load_data()

st.set_page_config(page_title="Rent", layout="wide", page_icon="📍")
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
        # Save data
        save_user(username, password, city, state, email, phone, zipcode)
        st.success("Data successfully added.")

    # Show user input city on the map
    if zipcode:
        city_data = get_city_data(zipcode)
        if not city_data.empty:
            latitude = city_data.iloc[0]['lat']
            longitude = city_data.iloc[0]['lng']
            st.map(pd.DataFrame([[latitude, longitude]], columns=['lat', 'lon']))
        else:
            st.warning("City not found.")

st.write(
    """
    Hope you like the map!
    """
)
