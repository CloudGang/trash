from logzero import logger
import pandas as pd
import streamlit as st
import plot_migration
import data_munging
from data_munging import ALL_STATES_TITLE

# Ensure the 'data/db.csv' file exists and has appropriate headers
import os
if not os.path.isfile("data/db.csv"):
    df = pd.DataFrame(columns=["Username", "Password", "City", "Email", "Phone"])
    df.to_csv("data/db.csv", index=False)

st.set_page_config(page_title="Migration Network", layout="wide", page_icon="📍")

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

st.title("State Movement")
state_choices = list(state_coordinates["name"])
state_choices.insert(0, ALL_STATES_TITLE)

with st.sidebar.form(key="my_form"):
    selectbox_state = st.selectbox("Choose a state", state_choices)
    selectbox_direction = st.selectbox("Choose a direction", ["Incoming", "Outgoing"])
    numberinput_threshold = st.number_input(
        """Set top N Migration per state""",
        value=3,
        min_value=1,
        max_value=25,
        step=1,
        format="%i",
    )
    
    # User input fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city = st.text_input("City")
    
    st.markdown(
        '<p class="small-font">Results Limited to top 5 per State in overall US</p>',
        unsafe_allow_html=True,
    )
    
    pressed = st.form_submit_button("Build Migration Map")

expander = st.sidebar.expander("What is this?")
expander.write(
    """
This app allows users to view migration between states from 2018-2019.
Overall US plots all states with substantial migration-based relationships with other states.
Any other option plots only migration from or to a given state. This map will be updated
to show migration between 2019 and 2020 once new census data comes out.

Incoming: Shows for a given state, the percent of their **total inbound migration from** another state.

Outgoing: Shows for a given state, the percent of their **total outbound migration to** another state.
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

    edges = data_munging.compute_edges(
        state_migration,
        threshold=numberinput_threshold,
        state=selectbox_state,
        direction=selectbox_direction,
    )

    nodes = data_munging.compute_nodes(
        state_coordinates, edges, direction=selectbox_direction
    )
    G = data_munging.build_network(nodes, edges)
    migration_plot = plot_migration.build_migration_chart(G, selectbox_direction)
    network_loc.plotly_chart(migration_plot)

    clean_edges = data_munging.table_edges(edges, selectbox_direction)
    table_loc.table(clean_edges.head(20))

    # Show user input city on the map
    if city:
        city_coordinates = state_coordinates[state_coordinates["name"] == city]
        if not city_coordinates.empty:
            st.map(city_coordinates[["latitude", "longitude"]])
        else:
            st.warning("City not found on the map.")
