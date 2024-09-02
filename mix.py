import streamlit as st
from st_files_connection import FilesConnection
from streamlit_ws_localstorage import injectWebsocketCode, getOrCreateUID
import json
import os

# Initialize the FilesConnection for S3
# Ensure that your Streamlit secrets are properly set with the necessary AWS credentials
# The secrets should include:
# - S3_ACCESS_KEY_ID
# - S3_SECRET_ACCESS_KEY
# - S3_BUCKET
# - S3_REGION

conn_s3 = st.connection('s3', type=FilesConnection)

# Main call to the API, returns a communication object
conn = injectWebsocketCode(hostPort='linode.liquidco.in', uid=getOrCreateUID())

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
    """Load data from local storage."""
    users = conn.getLocalStorageVal('users')
    uploads = conn.getLocalStorageVal('uploads')

    if users and uploads:
        data['users'] = json.loads(users)
        data['uploads'] = json.loads(uploads)
    else:
        save_data_to_storage()

def save_data_to_storage():
    """Save data to local storage."""
    conn.setLocalStorageVal('users', json.dumps(data['users']))
    conn.setLocalStorageVal('uploads', json.dumps(data['uploads']))

def upload_to_s3(file_path, file_content):
    """
    Upload a file to Amazon S3 using FilesConnection.

    Args:
        file_path (str): The path within the S3 bucket where the file will be stored.
        file_content (bytes): The binary content of the file.

    Returns:
        str: The public URL of the uploaded file.
    """
    try:
        # Write the file to S3
        conn_s3.write(file_path, file_content)
        # Construct the public URL (ensure your S3 bucket allows public access or configure accordingly)
        return f"https://{st.secrets['S3_BUCKET']}.s3.{st.secrets['S3_REGION']}.amazonaws.com/{file_path}"
    except Exception as e:
        st.error(f"Failed to upload file: {e}")
        return None

def save_user(username, password, email, avatar_file=None):
    """Save user data to the in-memory data structure and local storage."""
    avatar_url = None
    if avatar_file:
        avatar_filename = f"avatars/{username}_avatar.png"
        avatar_url = upload_to_s3(avatar_filename, avatar_file.read())

    data['users'].append({
        'username': username,
        'password': password,
        'email': email,
        'avatar_url': avatar_url
    })
    save_data_to_storage()

def save_media(username, media_name, media_type, media_file):
    """Save media data to the in-memory data structure and local storage."""
    file_extension = media_file.name.split('.')[-1]
    sanitized_media_name = "_".join(media_name.split()).lower()
    media_filename = f"uploads/{username}_{sanitized_media_name}.{file_extension}"
    media_url = upload_to_s3(media_filename, media_file.read())

    data['uploads'].append({
        'username': username,
        'media_name': media_name,
        'media_type': media_type,
        'media_url': media_url
    })
    save_data_to_storage()

def search_media(search_by, search_term):
    """Search media in the in-memory data structure by username or media name."""
    search_term = search_term.lower()
    results = []
    for upload in data['uploads']:
        if search_by == 'username' and search_term in upload.get('username', '').lower():
            user_info = next((user for user in data['users'] if user['username'].lower() == upload['username'].lower()), {})
            results.append({**upload, **{'avatar_url': user_info.get('avatar_url')}})
        elif search_by == 'media_name' and search_term in upload.get('media_name', '').lower():
            user_info = next((user for user in data['users'] if user['username'].lower() == upload['username'].lower()), {})
            results.append({**upload, **{'avatar_url': user_info.get('avatar_url')}})
    return results

def authenticate_user(username, password):
    """Authenticate user login based on username and password."""
    for user in data['users']:
        if user['username'].lower() == username.lower() and user['password'] == password:
            return user
    return None

# Load data at the start
load_data()

# Streamlit App Configuration
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

# Display the last 3 recently uploaded media in a row with 3 columns
st.header("Recently Uploaded Media")
recent_media = get_recently_uploaded_media(3)

if recent_media:
    cols = st.columns(3)
    for index, media in enumerate(recent_media):
        with cols[index]:
            st.write(f"**Title:** {media['media_name']}")
            st.write(f"**Uploaded by:** {media['username']}")
            
            if media['media_type'].lower() == 'audio':
                st.audio(media['media_url'])
            elif media['media_type'].lower() == 'video':
                st.video(media['media_url'])
            else:
                st.warning(f"Unknown media type: {media['media_type']}")
            st.write("---")
else:
    st.write("No media uploaded yet.")
    st.empty()  # Placeholder for consistency with the design

# Sidebar for Registration, Login, or User Profile
with st.sidebar:
    user_logged_in = conn.getLocalStorageVal('user_logged_in') == 'True'
    current_user = json.loads(conn.getLocalStorageVal('current_user') or '{}')
    
    if not user_logged_in:
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
                        save_user(username, password, email, avatar)
                        # Retrieve the newly created user's avatar_url
                        new_user = next((user for user in data['users'] if user['username'] == username), {})
                        conn.setLocalStorageVal('user_logged_in', 'True')
                        conn.setLocalStorageVal('current_user', json.dumps(new_user))
                        st.success("Registration successful.")
                        st.experimental_rerun()
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
                    conn.setLocalStorageVal('user_logged_in', 'True')
                    conn.setLocalStorageVal('current_user', json.dumps(user))
                    st.success("Login successful.")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
                
    else:
        st.header("Profile")
        if current_user.get('avatar_url'):
            st.image(current_user['avatar_url'], width=150)
        st.write(f"**Username:** {current_user['username']}")
        st.write(f"**Email:** {current_user['email']}")
        logout_button = st.button("Logout")
        if logout_button:
            conn.setLocalStorageVal('user_logged_in', 'False')
            conn.setLocalStorageVal('current_user', '{}')
            st.experimental_rerun()

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
                    if result.get('avatar_url'):
                        st.image(result['avatar_url'], width=100)
                    else:
                        st.image("https://via.placeholder.com/100", width=100)
                    st.write(f"**Username:** {result['username']}")
                with col2:
                    st.write(f"**Media Name:** {result['media_name']}")
                    if result['media_type'].lower() == "audio":
                        st.audio(result['media_url'])
                    elif result['media_type'].lower() == "video":
                        st.video(result['media_url'])
                st.markdown("---")
        else:
            st.warning("No results found.")
    else:
        st.error("Please enter a search term.")

# Media Upload Section
st.subheader("Upload Media")
if user_logged_in:
    with st.form(key="upload_form"):
        media_name = st.text_input("Media Name")
        media_type = st.selectbox("Media Type", ["Audio", "Video"])
        media_file = st.file_uploader("Upload Media File", type=['mp3', 'mp4', 'wav', 'avi'])
        upload_button = st.form_submit_button("Upload")

        if upload_button:
            if media_name and media_file:
                save_media(current_user['username'], media_name, media_type, media_file)
                st.success(f"{media_type} uploaded successfully!")
                st.experimental_rerun()
            else:
                st.error("Please provide both media name and file.")
else:
    st.warning("Please log in to upload media.")
