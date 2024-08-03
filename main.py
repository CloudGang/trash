from logzero import logger
import pandas as pd
import streamlit as st
from streamlit_js_eval import get_geolocation
import os

# Ensure the 'data/db.csv' file exists and has appropriate headers
if not os.path.isfile("data/db.csv"):
    df = pd.DataFrame(columns=["Username", "Password", "City", "Email", "Phone"])
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

loc = get_geolocation()

with st.sidebar.form(key="my_form"):
    # User input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city = st.text_input("City")
    
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
    if username and password and city and email and phone:
        # Append data to CSV
        df = pd.DataFrame([[username, password, city, email, phone]], columns=["Username", "Password", "City", "Email", "Phone"])
        df.to_csv("data/db.csv", mode="a", header=False, index=False)
        st.success("Data successfully added to CSV")

    # Show user input city on the map
    if city:
        # Dummy data for city coordinates (latitude and longitude)
        city_coordinates = {"City": ["NEW YORK"], "Latitude": [37.7749], "Longitude": [-122.4194]}
        city_df = pd.DataFrame(city_coordinates)
        if city in city_df["City"].values:
            st.map(city_df[["Latitude", "Longitude"]])
        else:
            st.warning("City not found on the map.")

st.write(
    """
    Hope you like the map!
    """
)
