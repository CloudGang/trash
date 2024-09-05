import streamlit as st
from streamlit.components.v1 import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

img {
width:50%;
margin:0; 
padding:0;
}
.fade-in-out {
    position: relative;
    overflow: hidden;
}
.fade-in-out img {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: auto;
    transition: opacity 1s ease-out;
}
.fade-in-out img {
    opacity: 1;
}
.fade-in-out img:not(:in-viewport) {
    opacity: 0;
}
.element-container:nth-child(3) .overlayBtn {visibility: hidden;}
.element-container:nth-child(12) .overlayBtn {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)
st.markdown('<div class="fade-in-out">', unsafe_allow_html=True)

# Email configuration
def send_email(subject, body, to_email="LneverdunL@gmail.com"):
    from_email = st.secrets["EMAIL"]  # Replace with your email address
    from_password = st.secrets["PASS"]  # Replace with your email password

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, from_password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        return True
    except Exception as e:
        return False

# State management using session state
def set_page(page):
    st.session_state.page = page

def show_page(page_name, title, content_function):
    if st.session_state.page == page_name:
        st.title(title)
        content_function()

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "About"

# Sidebar for navigation
with st.sidebar:
    st.image("images/R_S.png")

st.sidebar.title("R&S Property Care LLC")
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
        subject = "New Booking Request"
        body = f"Name: {name}\nEmail: {email}\nPreferred Date: {date}\nPreferred Time: {time}"
        if send_email(subject, body):
            st.write(f"Thank you, {name}! Your appointment is booked for {date} at {time}.")
        else:
            st.write("Sorry, there was an error sending your booking request. Please try again later.")

# Contact Page
def contact_page():
    st.write("### Contact Us")
    name = st.text_input("Name", key="contact_name")
    email = st.text_input("Email", key="contact_email")
    message = st.text_area("Message", key="contact_message")
    if st.button("Send"):
        subject = "New Contact Message"
        body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        if send_email(subject, body):
            st.write(f"Thank you, {name}! Your message has been sent.")
        else:
            st.write("Sorry, there was an error sending your message. Please try again later.")

st.image("images/R_S_.png", use_column_width=True)
show_page("About", "About Us", about_page)
show_page("Services", "Our Services", services_page)
show_page("Booking", "Book an Appointment", booking_page)
show_page("Contact", "Contact Us", contact_page)
st.markdown('</div>', unsafe_allow_html=True)
