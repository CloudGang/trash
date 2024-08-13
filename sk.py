import streamlit as st
import pandas as pd
import json
import os

# In-memory data storage
data = {
    'renters': [],
    'lenders': []
}

# File path for storing data
data_file_path = 'data.json'

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
    # Check if the lender already has 5 items
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

# Load data at the start
load_data()

# Streamlit app layout
st.set_page_config(page_title="Rentable", layout="wide", page_icon="📍")

st.title("Rentable")

role = st.radio("I am a", ["Lender :hammer_and_pick:", "Renter :open_hands:"])
username = st.text_input("Username")
zipcode = st.text_input("Zipcode (County FIPS)", max_chars=5)

if role == "Lender :hammer_and_pick:":
    item = st.text_input("Item to Register")
    image_file = st.file_uploader("Upload Item Image", type=['jpg', 'jpeg', 'png'])
else:
    item = None
    image_file = None

if st.button("Submit"):
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
