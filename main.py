from logzero import logger
import pandas as pd
import streamlit as st
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
import json
import plot_migration
import data_munging
from data_munging import ALL_STATES_TITLE

# Ensure the 'data/db.csv' file exists and has appropriate headers
import os
if not os.path.isfile("data/db.csv"):
    df = pd.DataFrame(columns=["Username", "Password", "City", "Email", "Phone"])
    df.to_csv("data/db.csv", index=False)

loc = get_geolocation()

st.set_page_config(page_title="Rentable", layout="wide", page_icon="📍")

st.markdown(
    """
    <style>
    .small-font {
        font-size:12px;
        font-style: italic;
        color: #b1a7a6;
    }

    #audio{autoplay:true;}
    #MainMenu{visibility: hidden;}
    footer{visibility: hidden;}
    .css-14xtw13 e8zbici0{visibility: hidden;}
    .css-m70y {display:none}
    .st-emotion-cache-zq5wmm.ezrtsby0{visibility: hidden;}
    .st-emotion-cache-zq5wmm.ezrtsby0{display:none}
    .styles_terminalButton__JBj5T{visibility: hidden;}
    .styles_terminalButton__JBj5T{display:none}
    .viewerBadge_container__r5tak.styles_viewerBadge__CvC9N{visibility: hidden;}
    .viewerBadge_container__r5tak.styles_viewerBadge__CvC9N{display:none}
    [data-testid='stSidebarNav'] > ul {min-height: 50vh;}
    [data-testid='stSidebarNav'] > ul {color: red;}
    .language-java {color: black;}
    .css-nps9tx, .e1m3hlzs0, .css-1p0bytv, .e1m3hlzs1 {
    visibility: collapse;
    height: 0px;
    }
    .stException {
        display: none;
    </style>
    """,
    unsafe_allow_html=True,
)

TABLE_PAGE_LEN = 10

state_coordinates = data_munging.get_coordinates()
state_migration = pd.read_csv("data/state_migration.csv")
state_summary = pd.read_csv("data/state_migration_summary.csv")

st.title("Rent")
#location = get_geolocation()
#location_json = get_page_location()

state_choices = list(state_coordinates["name"])
state_choices.insert(0, ALL_STATES_TITLE)

with st.sidebar.form(key="my_form"):
    selectbox_state = st.selectbox("Choose a state", state_choices)
    selectbox_direction = st.selectbox("Renter or Lender", ["Renting", "Lending"])
    
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

network_place, _, descriptor = st.columns([6, 1, 3])
network_loc = network_place.empty()

descriptor.subheader(data_munging.display_state(selectbox_state))
descriptor.write(data_munging.display_state_summary(selectbox_state, state_summary))

edges = data_munging.compute_edges(
    state_migration,
    threshold=numberinput_threshold,
    state=ALL_STATES_TITLE,
    direction=selectbox_direction,
)

nodes = data_munging.compute_nodes(
    state_coordinates, edges, direction=selectbox_direction
)
G = data_munging.build_network(nodes, edges)
logger.info("Graph Created, doing app stuff")

migration_plot = plot_migration.build_migration_chart(G, selectbox_direction)
network_loc.plotly_chart(migration_plot)

st.write(
    """
    Hope you like the map!
    """
)

st.header("Migration Table")
table_loc = st.empty()
clean_edges = data_munging.table_edges(edges, selectbox_direction)
table_loc.table(clean_edges.head(20))

if pressed:
    if username and password and city and email and phone:
        # Append data to CSV
        df = pd.DataFrame([[username, password, city, email, phone]], columns=["Username", "Password", "City", "Email", "Phone"])
        df.to_csv("data/db.csv", mode="a", header=False, index=False)
        st.success("Data successfully added to CSV")

    # Show user input city on the map
    if city:
        city_coordinates = state_coordinates[state_coordinates["name"] == city]
        if not city_coordinates.empty:
            st.map(city_coordinates[["latitude", "longitude"]])
        else:
            st.warning("City not found on the map.")
