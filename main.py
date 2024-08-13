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
    'renters': [],
    'lenders': []
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

def save_renter(username, zipcode):
    """Save renter data to the in-memory data structure and file."""
    data['renters'].append({
        'username': username,
        'zipcode': zipcode
    })
    save_data_to_file()

def save_lender(username, zipcode, item, image_path):
    """Save lender data and item to the in-memory data structure and file."""
    lender = next((l for l in data['lenders'] if l['username'] == username), None)
    if lender:
        if len(lender['items']) >= 5:
            st.error("You can only register up to 5 items.")
            return
        lender['items'].append({
            'zipcode': zipcode,
            'item': item,
            'image_path': image_path
        })
    else:
        data['lenders'].append({
            'username': username,
            'items': [{
                'zipcode': zipcode,
                'item': item,
                'image_path': image_path
            }]
        })
    save_data_to_file()

def search_items(search_by, search_term):
    """Search items in the in-memory data structure by item or zipcode."""
    search_term = search_term.lower()
    results = []
    if search_by == 'item':
        for lender in data['lenders']:
            for item in lender['items']:
                if search_term in item['item'].lower():
                    results.append({
                        'username': lender['username'],
                        'zipcode': item['zipcode'],
                        'item': item['item'],
                        'image_path': item['image_path']
                    })
    elif search_by == 'zipcode':
        for lender in data['lenders']:
            for item in lender['items']:
                if search_term in item['zipcode']:
                    results.append({
                        'username': lender['username'],
                        'zipcode': item['zipcode'],
                        'item': item['item'],
                        'image_path': item['image_path']
                    })
    return results

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
if st.button("Refresh"):
    st.rerun()
with st.sidebar.form(key="my_form"):
    # Radio button for role selection
    role = st.radio("I am a", ["Renter :open_hands:", "Lender :hammer_and_pick:"])

    # User input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city = st.text_input("City")
    state = st.text_input("State")
    zipcode = st.text_input("Zipcode (County FIPS)", max_chars=5)

    # Conditional fields based on role
#    if role == "Lender :hammer_and_pick:":
#        item = st.text_input("Item to Register")
#        image_file = st.file_uploader("Upload Item Image", type=['jpg', 'jpeg', 'png'])
#    else:
#        item = None
#        image_file = None

    # Conditional fields based on role
    if role == "Renter :open_hands:":
        item = None
        image_file = None
    else:
        item = st.text_input("Item to Register")
        image_file = st.file_uploader("Upload Item Image", type=['jpg', 'jpeg', 'png'])

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
    if username and zipcode:
        if role == "Lender :hammer_and_pick:":
            if item and image_file:
                # Save image file
                image_path = f"images/{username}_{item.replace(' ', '_')}.png"
                if not os.path.exists('images'):
                    os.makedirs('images')
                with open(image_path, "wb") as f:
                    f.write(image_file.read())
                
                save_lender(username, zipcode, item, image_path)
                st.success("Item successfully registered.")
            else:
                st.error("Please fill in all fields and upload an image.")
        else:
            # Renters cannot register items
            save_renter(username, zipcode)
            st.success("Renter successfully registered.")
    else:
        st.error("Please fill in all required fields.")

st.header("Search for Items")
search_option = st.selectbox("Search by", ("Item", "Zipcode"))
search_term = st.text_input(f"Search {search_option}")

if st.button("Search"):
    search_by = search_option.lower()
    results = search_items(search_by, search_term)
    if results:
        for result in results:
            st.image(result['image_path'], use_column_width=True)
            st.write(f"**Username:** {result['username']}")
            st.write(f"**Zipcode:** {result['zipcode']}")
            st.write(f"**Item:** {result['item']}")
            st.write("---")
    else:
        st.write("No results found.")
