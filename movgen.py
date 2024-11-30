import streamlit as st
from PIL import Image
import requests
import replicate
import os
from io import BytesIO
import random  # For generating unique seeds
from gtts import gTTS  # Import gTTS for text-to-speech

# PART 1: SETUP REPLICATE CREDENTIALS
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")  # Use your Replicate API token
if REPLICATE_API_TOKEN is None:
    st.error("Replicate API token not found. Please set it in your environment.")
    st.stop()

# Authenticate with Replicate
replicate.Client(api_token=REPLICATE_API_TOKEN)

# PART 2: AI STORY GENERATION FUNCTION
def generate_story(story_type):
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
def generate_images(prompt, num_images=5, output_quality=80):
    generated_image_urls = []
    for _ in range(num_images):
        try:
            # Generate a unique random seed for each image
            unique_seed = random.randint(0, 10000)

            input_data = {
                "prompt": prompt,
                "aspect_ratio": '3:2',  # Set the aspect ratio
                "quality": output_quality,
                "seed": unique_seed  # Use the unique seed for diversity
            }

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
st.title("AI Story and Image Generator with Audio")
st.subheader("Choose or enter a type of story for AI to generate, along with images and audio.")

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

# Generate story and images when the button is clicked
if st.button("Generate Story, Images, and Audio"):
    with st.spinner("Generating your story, images, and audio..."):
        try:
            # Generate the story
            story = generate_story(story_type_to_use)
            st.success("Story generated successfully!")
            st.text_area("Your AI-Generated Story:", value=story, height=300)

            # Convert the story to audio using gTTS
            tts = gTTS(text=story, lang='en')
            audio_file = BytesIO()
            tts.save(audio_file)
            #audio_file.seek(0)

            # Play the audio in Streamlit
            st.audio(audio_file, format="audio/mp3")

            # Generate images
            st.subheader("Generated Images")
            image_urls = generate_images(story, num_images=num_images, output_quality=output_quality)
            
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
