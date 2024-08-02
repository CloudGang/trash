import logging
import os
import psycopg2
import streamlit as st
from streamlit_js_eval import get_geolocation
import plot_migration
import data_munging

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Database connection details (directly use the DB_URL)
DB_URL = "postgresql://supreme:Z0lGvbB_Hs7Lvt104K2ZFw@stoic-duke-15588.7tt.aws-us-east-1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"

def get_db_connection():
    """Establishes a database connection."""
    try:
        conn = psycopg2.connect(DB_URL, application_name="$ docs_quickstart_python")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        raise

def create_table_if_not_exists():
    """Create the users table if it doesn't exist."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    username TEXT UNIQUE,
                    password TEXT,
                    email TEXT,
                    phone TEXT,
                    city TEXT
                )
            """)
            conn.commit()

def insert_user(username, password, email, phone, city):
    """Insert a new user into the users table."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (username, password, email, phone, city)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, password, email, phone, city))
            conn.commit()

def retrieve_users():
    """Retrieve all users from the users table."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username, city FROM users")
            rows = cur.fetchall()
            return rows

# Ensure the table is created
create_table_if_not_exists()

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

TABLE_PAGE_LEN = 10

state_coordinates = data_munging.get_coordinates()
state_migration = pd.read_csv("data/state_migration.csv")
state_summary = pd.read_csv("data/state_migration_summary.csv")

st.title("Rent")

loc = get_geolocation()

state_choices = list(state_coordinates["name"])
state_choices.insert(0, "All States")  # Assume ALL_STATES_TITLE is "All States"

with st.sidebar.form(key="my_form"):
    selectbox_state = st.selectbox("Choose a state", state_choices)
    selectbox_direction = st.selectbox("Renter or Lender", ["Renting", "Lending"])
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
    state="All States",  # Assume ALL_STATES_TITLE is "All States"
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
        # Insert data into the database
        insert_user(username, password, email, phone, city)
        st.success("Data successfully added to the database")

    # Show user input city on the map
    if city:
        city_coordinates = state_coordinates[state_coordinates["name"] == city]
        if not city_coordinates.empty:
            st.map(city_coordinates[["latitude", "longitude"]])
        else:
            st.warning("City not found on the map.")

# Add buttons to retrieve and display username and city
if st.button("Retrieve and Display User Information"):
    users = retrieve_users()
    if users:
        st.write("User Information:")
        for username, city in users:
            st.write(f"Username: {username}, City: {city}")
    else:
        st.write("No users found in the database.")
