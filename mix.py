import streamlit as st
import json
import os

# File path for storing data
data_file_path = 'data.json'

# In-memory data storage
data = {
    'users': [],
    'uploads': []
}

def load_data():
    """Load data from a file."""
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r') as f:
            global data
            data = json.load(f)
        # Ensure 'uploads' key exists
        if 'uploads' not in data:
            data['uploads'] = []
    else:
        save_data_to_file()

def save_data_to_file():
    """Save data to a file."""
    with open(data_file_path, 'w') as f:
        json.dump(data, f, indent=4)

def save_user(username, email, phone, city, state, zipcode):
    """Save user data to the in-memory data structure and file."""
    data['users'].append({
        'username': username,
        'email': email,
        'phone': phone,
        'city': city,
        'state': state,
        'zipcode': zipcode
    })
    save_data_to_file()

def save_upload(username, title, media_type, file_path, description):
    """Save uploaded media to the in-memory data structure and file."""
    data['uploads'].append({
        'username': username,
        'title': title,
        'media_type': media_type,
        'file_path': file_path,
        'description': description
    })
    save_data_to_file()

def search_uploads(search_by, search_term):
    """Search uploads in the in-memory data structure by title or username."""
    search_term = search_term.lower()
    results = []
    if search_by == 'title':
        for upload in data['uploads']:
            if search_term in upload.get('title', '').lower():
                results.append(upload)
    elif search_by == 'username':
        for upload in data['uploads']:
            if search_term == upload.get('username', '').lower():
                results.append(upload)
    return results

# Load data at the start
load_data()

st.set_page_config(page_title="Music Sharing", layout="wide", page_icon="🎵")
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

st.title("Music Sharing")

with st.sidebar.form(key="user_form"):
    # User input fields
    username = st.text_input("Username")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    city = st.text_input("City")
    state = st.text_input("State")
    zipcode = st.text_input("Zipcode (County FIPS)", max_chars=5)

    st.markdown(
        '<p class="small-font">Please provide your location details.</p>',
        unsafe_allow_html=True,
    )
    
    if st.form_submit_button("Register"):
        if username and zipcode:
            save_user(username, email, phone, city, state, zipcode)
            st.success("User successfully registered.")
        else:
            st.error("Please fill in all required fields.")

with st.sidebar.form(key="upload_form"):
    # Upload input fields
    username = st.text_input("Username")
    title = st.text_input("Title of the Audio/Video")
    media_type = st.selectbox("Media Type", ["Audio", "Video"])
    media_file = st.file_uploader(f"Upload {media_type} File", type=['mp3', 'mp4', 'wav', 'mkv'])
    description = st.text_area("Description")

    if st.form_submit_button("Upload"):
        if username and title and media_file:
            # Save media file
            file_path = f"uploads/{username}_{title.replace(' ', '_')}.{media_file.name.split('.')[-1]}"
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            with open(file_path, "wb") as f:
                f.write(media_file.read())
            
            save_upload(username, title, media_type, file_path, description)
            st.success(f"{media_type} successfully uploaded.")
        else:
            st.error("Please fill in all fields and upload a file.")

st.header("Search for Music")
search_option = st.selectbox("Search by", ["Title", "Username"])

search_term = st.text_input(f"Search {search_option}")

if st.button("Search"):
    search_by = search_option.lower()
    results = search_uploads(search_by, search_term)
    if results:
        for result in results:
            st.write(f"**Title:** {result['title']}")
            st.write(f"**Uploaded by:** {result['username']}")
            st.write(f"**Description:** {result['description']}")
            st.write(f"**Media Type:** {result['media_type']}")
            if result['media_type'] == "Audio":
                st.audio(result['file_path'])
            else:
                st.video(result['file_path'])
            st.write("---")
    else:
        st.write("No results found.")

st.write("----------------------------------------------------------------------")

# Display the list of uploaded media
st.write("Uploaded Media:")
if 'uploads' in data:
    for upload in data['uploads']:
        st.write(f"**Title:** {upload['title']}")
        st.write(f"**Uploaded by:** {upload['username']}")
        st.write(f"**Description:** {upload['description']}")
        st.write(f"**Media Type:** {upload['media_type']}")
        if upload['media_type'] == "Audio":
            st.audio(upload['file_path'])
        else:
            st.video(upload['file_path'])
        st.write("----------------------------------------------------------------------")
else:
    st.write("No media files have been uploaded yet.")
