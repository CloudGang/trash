import streamlit as st
import json
import os

# File path for storing data
data_file_path = 'data.json'

# Initialize session state
if 'user_logged_in' not in st.session_state:
    st.session_state['user_logged_in'] = False
    st.session_state['current_user'] = {}

# In-memory data storage
data = {
    'users': [],
    'uploads': []
}

def get_recently_uploaded_media(n=3):
    """Get the last n recently uploaded media."""
    uploads = data.get('uploads', [])
    return uploads[-n:] if uploads else []

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
    for upload in data['uploads']:
        if search_by == 'username' and search_term in upload.get('username', '').lower():
            user_info = next((user for user in data['users'] if user['username'].lower() == upload['username'].lower()), {})
            results.append({**upload, **{'avatar_path': user_info.get('avatar_path')}})
        elif search_by == 'media_name' and search_term in upload.get('media_name', '').lower():
            user_info = next((user for user in data['users'] if user['username'].lower() == upload['username'].lower()), {})
            results.append({**upload, **{'avatar_path': user_info.get('avatar_path')}})
    return results

def authenticate_user(username, password):
    """Authenticate user login based on username and password."""
    for user in data['users']:
        if user['username'].lower() == username.lower() and user['password'] == password:
            return user
    return None

# Load data at the start
load_data()

st.set_page_config(page_title="Music Sharing Platform", layout="wide", page_icon="🎵")
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

st.title("🎵 Music Sharing Platform")

# Display the last 3 recently uploaded media
st.header("Recently Uploaded Media")
recent_media = get_recently_uploaded_media(3)

if recent_media:
    for media in recent_media:
        st.write(f"**Uploaded by:** {media['username']}")
        
        if 'media_type' in media and os.path.exists(media['media_path']):
            if media['media_type'] == 'audio':
                st.audio(media['media_path'])
            elif media['media_type'] == 'video':
                st.video(media['media_path'])
            else:
                st.warning(f"Unknown media type: {media['media_type']}")
        else:
            st.error("Media file is missing or not found.")
        
        st.write("---")
else:
    st.write("No media uploaded yet.")
    for _ in range(3):
        st.empty()  # Placeholder

# Sidebar for Registration, Login, or User Profile
with st.sidebar:
    if not st.session_state['user_logged_in']:
        st.header("Register")
        with st.form(key="registration_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            email = st.text_input("Email")
            avatar = st.file_uploader("Upload Avatar", type=['jpg', 'jpeg', 'png'])
            
            submit_button = st.form_submit_button("Register")
            
            if submit_button:
                if username and password and email:
                    # Check if username already exists
                    if any(user['username'].lower() == username.lower() for user in data['users']):
                        st.error("Username already exists. Please choose a different username.")
                    else:
                        avatar_path = None
                        if avatar:
                            avatar_dir = 'avatars'
                            os.makedirs(avatar_dir, exist_ok=True)
                            avatar_path = os.path.join(avatar_dir, f"{username}_avatar.png")
                            with open(avatar_path, "wb") as f:
                                f.write(avatar.read())
                        save_user(username, password, email, avatar_path)
                        st.session_state['user_logged_in'] = True
                        st.session_state['current_user'] = {
                            'username': username,
                            'email': email,
                            'avatar_path': avatar_path
                        }
                        st.success("Registration successful.")
                        st.rerun()
                else:
                    st.error("Please fill in all required fields.")
        
        st.header("Login")
        with st.form(key="login_form"):
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                user = authenticate_user(login_username, login_password)
                if user:
                    st.session_state['user_logged_in'] = True
                    st.session_state['current_user'] = user
                    st.success("Login successful.")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
                
    else:
        st.header("Profile")
        user_info = st.session_state['current_user']
        if user_info.get('avatar_path'):
            st.image(user_info['avatar_path'], width=150)
        st.write(f"**Username:** {user_info['username']}")
        st.write(f"**Email:** {user_info['email']}")
        logout_button = st.button("Logout")
        if logout_button:
            st.session_state['user_logged_in'] = False
            st.session_state['current_user'] = {}
            st.experimental_rerun()

# Media Upload Section
st.subheader("Upload Media")
if st.session_state['user_logged_in']:
    with st.form(key="upload_form"):
        media_name = st.text_input("Media Name")
        media_type = st.selectbox("Media Type", ["Audio", "Video"])
        media_file = st.file_uploader("Upload Media", type=['mp3', 'mp4', 'wav', 'mkv', 'mov'])
        
        upload_button = st.form_submit_button("Upload")
        
        if upload_button:
            if media_name and media_file:
                media_dir = 'uploads'
                os.makedirs(media_dir, exist_ok=True)
                file_extension = media_file.name.split('.')[-1]
                media_path = os.path.join(media_dir, f"{st.session_state['current_user']['username']}_{media_name.replace(' ', '_')}.{file_extension}")
                with open(media_path, "wb") as f:
                    f.write(media_file.read())
                save_media(st.session_state['current_user']['username'], media_name, media_type, media_path)
                st.success("Media successfully uploaded.")
            else:
                st.error("Please provide a media name and upload a file.")
else:
    st.info("Please register or log in to upload media.")

# Media Search Section
st.subheader("Search Media")
search_option = st.selectbox("Search by", ["Username", "Media Name"])
search_term = st.text_input(f"Enter {search_option}")

if st.button("Search"):
    if search_term:
        search_by = search_option.lower().replace(' ', '_')
        results = search_media(search_by, search_term)
        if results:
            for result in results:
                col1, col2 = st.columns([1, 3])
                with col1:
                    if result.get('avatar_path'):
                        st.image(result['avatar_path'], width=100)
                    else:
                        st.image("https://via.placeholder.com/100", width=100)
                    st.write(f"**Username:** {result['username']}")
                with col2:
                    st.write(f"**Media Name:** {result['media_name']}")
                    if result['media_type'] == "Audio":
                        st.audio(result['media_path'])
                    elif result['media_type'] == "Video":
                        st.video(result['media_path'])
                st.markdown("---")
        else:
            st.warning("No results found.")
    else:
        st.error("Please enter a search term.")
