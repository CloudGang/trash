import streamlit as st
import streamlit.components.v1 as components
from g4f.client import Client  # Ensure the `g4f.client` library is properly installed and available
import base64
import re

# Function to handle AI story generation
def generate_story(story_type):
    client = Client()  # Initialize client
    prompt = f"Write a 1 to 2 minute story based on the theme: {story_type}."
    
    # AI generation request
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }],
    )
    
    # Extract the generated story
    ai_generated_story = response.choices[0].message.content.strip()
    return ai_generated_story

# Streamlit app layout
st.title("AI Story Generator")
st.subheader("Choose or enter a type of story for AI to generate.")

# Predefined story types
story_types = [
    "Overcoming the Monster",
    "Rags to Riches",
    "The Quest",
    "Voyage and Return",
    "Rebirth",
    "Comedy",
    "Tragedy"
]

# Dropdown menu for predefined types
selected_type = st.selectbox("Select a predefined story type:", story_types)

# Optional manual input for custom story type
custom_type = st.text_input("Or enter your own story type:")

# Determine the story type to use
story_type_to_use = custom_type if custom_type.strip() else selected_type

# Generate the story when the button is clicked
if st.button("Generate Story"):
    with st.spinner("Generating your story..."):
        try:
            story = generate_story(story_type_to_use)
            st.success("Story generated successfully!")
            st.text_area("Your AI-Generated Story:", value=story, height=300)
        except Exception as e:
            st.error(f"An error occurred while generating the story: {e}")
