import streamlit as st
from g4f.client import Client
from PIL import Image
from io import BytesIO
import requests

# Function to convert images to PIL Image format
def to_image(image_url: str) -> Image:
    """
    Converts an image from a URL to a PIL Image object.

    Args:
        image_url (str): The URL of the image.

    Returns:
        Image: The converted PIL Image object.
    """
    response = requests.get(image_url)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    else:
        raise ValueError(f"Unable to fetch image from URL: {image_url}")

# Function to handle AI story generation
def generate_story(story_type):
    client = Client()  # Initialize client
    prompt = f"Write a 1 to 2 minute story based on the theme: {story_type}."
    
    # AI generation request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt
        }],
    )
    
    # Extract the generated story
    ai_generated_story = response.choices[0].message.content.strip()
    return ai_generated_story

# Function to handle AI image generation
def generate_images(story, num_images=5):
    client = Client()  # Initialize client
    images = []
    for i in range(num_images):
        # Use the story content as a prompt for image generation
        response = client.images.generate(
            model="flux",
            prompt=story,
        )
        # Extract the generated image URL
        if response.data:
            images.append(response.data[0].url)
    return images

# Streamlit app layout
st.title("AI Story and Image Generator")
st.subheader("Choose or enter a type of story for AI to generate, along with images.")

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

# Generate the story and images when the button is clicked
if st.button("Generate Story and Images"):
    with st.spinner("Generating your story and images..."):
        try:
            # Generate the story
            story = generate_story(story_type_to_use)
            st.success("Story generated successfully!")
            st.text_area("Your AI-Generated Story:", value=story, height=300)

            # Generate images
            st.subheader("Generated Images")
            num_images = st.slider("Number of images to generate:", 5, 10, 5)
            image_urls = generate_images(story, num_images=num_images)
            
            if image_urls:
                for idx, img_url in enumerate(image_urls, 1):
                    try:
                        pil_image = to_image(img_url)  # Convert to PIL Image
                        st.image(pil_image, caption=f"Generated Image {idx}", use_column_width=True)
                    except Exception as e:
                        st.warning(f"Failed to process image {idx}: {e}")
            else:
                st.warning("No images were generated. Please try again.")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
