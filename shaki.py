import streamlit as st

hide_menu_style = """
        <style>
        .st-emotion-cache-15ecox0.ezrtsby0 {visibility: hidden;}
        .viewerBadge_container__r5tak.styles_viewerBadge__CvC9N {visibility: hidden;}
        .viewerBadge_link__qRIco {visibility: hidden;}
        .css-15zrgzn {display: none}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
.stButton {
  width: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0;
}

.stButton button {
  width: 100%;
  height: 100%;
  padding: 0;
}

.stButton button p {
  margin: 0;
  font-size: 12px; /* Adjust font size as needed */
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# State management using session state
def set_page(page):
    st.session_state.page = page

def show_page(page_name, title, content_function):
    #st.sidebar.markdown(f"### {page_name}")
    if st.session_state.page == page_name:
        st.title(title)
        content_function()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "About"

# Sidebar for navigation
st.sidebar.title("R&S Property Care LLC")
st.sidebar.image("images/R_S.png", key="img1")
st.sidebar.button("About", on_click=set_page, args=("About",))
st.sidebar.button("Services", on_click=set_page, args=("Services",))
st.sidebar.button("Booking", on_click=set_page, args=("Booking",))
st.sidebar.button("Contact", on_click=set_page, args=("Contact",))

# About Page
def about_page():
    st.write("""
    ### Welcome to R&S Property Care LLC
    R&S Property Care LLC is a leading provider of housing solutions. We specialize in 
    affordable housing options and ensure that our clients have access to the best services 
    tailored to their needs.
    """)

# Services Page
def services_page():
    st.write("""
    ### Our Services
    - **Property Management:** Comprehensive management services for residential properties.
    - **Leasing Services:** Assistance in leasing your property with ease.
    - **Maintenance and Repairs:** Prompt and reliable maintenance services for tenants.
    """)

# Booking Page
def booking_page():
    st.write("### Book an Appointment")
    name = st.text_input("Name")
    email = st.text_input("Email")
    date = st.date_input("Preferred Date")
    time = st.time_input("Preferred Time")
    if st.button("Book"):
        st.write(f"Thank you, {name}! Your appointment is booked for {date} at {time}.")

# Contact Page
def contact_page():
    st.write("### Contact Us")
    name = st.text_input("Name", key="contact_name")
    email = st.text_input("Email", key="contact_email")
    message = st.text_area("Message", key="contact_message")
    if st.button("Send"):
        st.write(f"Thank you, {name}! Your message has been sent.")
#################################################################

st.image("images/R_S.png", caption="R&S Property Care LLC")

#_container = st.container()
#col1, col2, col3, col4 = _container.columns(4)
#with col1:
#    st.button("About", key="123", on_click=set_page, args=("About",))
#with col2:
#    st.button("Services", key="1234", on_click=set_page, args=("Services",))
#with col3:
#    st.button("Booking", key="12345", on_click=set_page, args=("Booking",))
#with col4:
#    st.button("Contact", key="123456", on_click=set_page, args=("Contact",))

show_page("About", "About Us", about_page)
show_page("Services", "Our Services", services_page)
show_page("Booking", "Book an Appointment", booking_page)
show_page("Contact", "Contact Us", contact_page)
