import streamlit as st

# Debugging secrets access
st.title("Secrets Debug")

# Attempt to access and display secrets
secrets = st.secrets.get("connections.postgresql", None)
if secrets:
    st.write("Secrets available:")
    st.write(secrets)
else:
    st.write("Secrets section 'connections.postgresql' not found or is empty.")
