import streamlit as st
import pandas as pd
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
    else:
        save_data_to_file()

def save_data_to_file():
    """Save data to a file."""
    with open(data_file_path, 'w') as f:
        json.dump(data, f, indent=4)

def save_user(username, password, email, avatar_path=None):
    """Save user data to the in-memory data structure and file."""
    data['users'].append({
        'username': username,
        'password': password,
        'email': email,
        'avatar_path': avatar_path
    })
    save_data_to_file()

def save_media(username, media_name, media_type, media_path):
    """Save media data to the in-memory data structure and file."""
    data['uploads'].append({
        'username': username,
        'media_name': media_name,
        'media_type': media_type,
        'media_path': media_path
    })
    save_data_to_file()

def search_media(search_by, search_term):
    """Search media in the in-memory data structure by username or media name."""
    search_term = search_term.lower()
    results = []
    if search_by == 'username':
        for upload in data['uploads']:
            if search_term in upload.get('username', '').lower():
                user_info = next((user for user in data['users'] if user['username'] == upload['username']), None)
                results.append({
                    'username': upload['username'],
                    'media_name': upload['media_name'],
                    'media_type': upload['media_type'],
                    'media_path': upload['media_path'],
                    'avatar_path': user_info.get('avatar_path', '') if user_info else ''
                })
    elif search_by == 'media_name':
        for upload in data['uploads']:
            if search_term in upload.get('media_name', '').lower():
                user_info = next((user for user in data['users'] if user['username'] == upload['username']), None)
                results.append({
                    'username': upload['username'],
                    'media_name': upload['media_name'],
                    'media_type': upload['media_type'],
                    'media_path': upload['media_path'],
                    'avatar_path': user_info.get('avatar_path', '') if user_info else ''
                })
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

st.title("Music Sharing Platform")

with st.sidebar.form(key="registration_form"):
    st.header("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    avatar = st.file_uploader("Upload Avatar", type=['jpg', 'jpeg', 'png'])
    
    if st.form_submit_button("Register"):
        if username and password and email:
            avatar_path = None
            if avatar:
                avatar_path = f"avatars/{username}_avatar.png"
                if not os.path.exists('avatars'):
                    os.makedirs('avatars')
                with open(avatar_path, "wb") as f:
                    f.write(avatar.read())
            save_user(username, password, email, avatar_path)
            st.success("Registration successful.")
        else:
            st.error("Please fill in all required fields.")

with st.sidebar.form(key="upload_form"):
    st.header("Upload Media")
    username = st.text_input("Username (for Upload)")
    media_name = st.text_input("Media Name")
    media_type = st.selectbox("Media Type", ["Audio", "Video"])
    media_file = st.file_uploader("Upload Media", type=['mp3', 'mp4', 'wav'])
    
    if st.form_submit_button("Upload"):
        if username and media_name and media_type and media_file:
            media_path = f"uploads/{username}_{media_name.replace(' ', '_')}.{media_file.name.split('.')[-1]}"
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            with open(media_path, "wb") as f:
                f.write(media_file.read())
            save_media(username, media_name, media_type, media_path)
            st.success("Media successfully uploaded.")
        else:
            st.error("Please fill in all required fields.")

st.header("Search Media")
search_option = st.selectbox("Search by", ["Username", "Media Name"])
search_term = st.text_input(f"Search {search_option}")

if st.button("Search"):
    search_by = search_option.lower().replace(' ', '_')
    results = search_media(search_by, search_term)
    if results:
        for result in results:
            if result['avatar_path']:
                st.image(result['avatar_path'], width=100)
            st.write(f"**Username:** {result['username']}")
            st.write(f"**Media Name:** {result['media_name']}")
            if result['media_type'] == "Audio":
                st.audio(result['media_path'])
            elif result['media_type'] == "Video":
                st.video(result['media_path'])
            st.write("---")
    else:
        st.write("No results found.")
