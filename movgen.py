import streamlit as st
from PIL import Image
import requests
import replicate
import os
from io import BytesIO

# PART 1: SETUP REPLICATE CREDENTIALS
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")  # Use your Replicate API token
if REPLICATE_API_TOKEN is None:
    st.error("Replicate API token not found. Please set it in your environment.")
    st.stop()

# Authenticate with Replicate
replicate.Client(api_token=REPLICATE_API_TOKEN)

# PART 2: AI STORY GENERATION FUNCTION
def generate_story(story_type):
    # Replace this placeholder with the actual client code for story generation
    from g4f.client import Client  # Replace with your GPT client library
    client = Client()
    prompt = f"Write a 1 to 2 minute story based on the theme: {story_type}."
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": prompt
        }],
    )
    return response.choices[0].message.content.strip()

# PART 3: AI IMAGE GENERATION FUNCTION USING REPLICATE
def generate_images(prompt, num_images=5, output_quality=80, random_seed=None):
    generated_image_urls = []
    for _ in range(num_images):
        try:
            input_data = {
                "prompt": prompt,
                "aspect_ratio": '3:2',  # Set the aspect ratio
                "quality": output_quality
            }
            if random_seed is not None:
                input_data["seed"] = random_seed

            # Call the Replicate model to generate an image
            output = replicate.run(
                "black-forest-labs/flux-schnell",
                input=input_data
            )
            generated_image_urls.append(output[0])  # Assuming output is a list with the image URL
        except Exception as e:
            st.warning(f"Error generating an image: {e}")
    return generated_image_urls

# PART 4: STREAMLIT APP LAYOUT
st.title("Story and Image Generator")
st.subheader("Choose or enter a type of story to generate, along with images.")

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

# Dropdown for predefined types
selected_type = st.selectbox("Select a predefined story type:", story_types)

# Optional manual input for custom type
custom_type = st.text_input("Or enter your own story type:")

# Determine the type to use
story_type_to_use = custom_type if custom_type.strip() else selected_type

# PART 4A: IMAGE GENERATION OPTIONS
st.sidebar.title("Image Generation Options")
num_images = st.sidebar.slider("Number of images:", 1, 10, 5)
output_quality = st.sidebar.slider("Output Quality:", 50, 100, 80)
use_random_seed = st.sidebar.checkbox("Use Random Seed", value=True)
random_seed = st.sidebar.slider("Random Seed:", 0, 1000, 435) if use_random_seed else None

# Generate story and images when the button is clicked
if st.button("Generate Story and Images"):
    with st.spinner("Generating your story and images..."):
        try:
            # Generate the story
            story = generate_story(story_type_to_use)
            st.success("Story generated successfully!")
            st.text_area("Your AI-Generated Story:", value=story, height=300)

            # Generate images
            st.subheader("Generated Images")
            image_urls = generate_images(story, num_images=num_images, output_quality=output_quality, random_seed=random_seed)
            
            if image_urls:
                for idx, img_url in enumerate(image_urls, 1):
                    response = requests.get(img_url)
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption=f"Generated Image {idx}", use_column_width=True)

                    # Create a download button for each image
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    buffer.seek(0)
                    st.download_button(
                        label=f"Download Image {idx}",
                        data=buffer,
                        file_name=f"generated_image_{idx}.jpg",
                        mime="image/jpeg"
                    )
            else:
                st.warning("No images were generated. Please try again.")
        
        except Exception as e:
            st.error(f"An error occurred: {e}")
