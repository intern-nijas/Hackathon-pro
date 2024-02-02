from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.media import UploadFile
from wordpress_xmlrpc.exceptions import ServerConnectionError
from dotenv import load_dotenv
import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import requests
import io

# Load environment variables
load_dotenv()

# Configure Google GenerativeAI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Unsplash API Key (replace with your own key)
unsplash_access_key = '4u2Bxms8ez7PzxZzzD04U0TAroF-ADLJfoHrwiSWFDE'

# Function to load OpenAI model and get responses
def get_gemini_response(question):
    model = genai.GenerativeModel('gemini-pro')
    #chat = model.start_chat(history=[])
    #response = chat.send_message(question, stream=True)
    response = model.generate_content(question)
    return response.text

# Function to fetch images from Unsplash
def fetch_images(prompt, count=1):
    url = f'https://api.unsplash.com/photos/random?query={prompt}&count={count}&client_id={unsplash_access_key}'
    response = requests.get(url)
    data = response.json()
    image_urls = [photo['urls']['regular'] for photo in data]
    return image_urls

# Function to publish content to WordPress
def publish_to_wordpress(title, content, images):
    try:
        # Replace these with your WordPress credentials and settings
        wordpress_url = 'http://127.0.0.3:8080/xmlrpc.php'
        wordpress_username = 'bumblebee'
        wordpress_password = 'BMVHMHpQBA1Iy27TKz'

        # Create a WordPress client
        wp = Client(wordpress_url, wordpress_username, wordpress_password)

        # Create a new post
        post = WordPressPost()
        post.title = title


        # Assume 'content' contains text and 'images' is a list of image URLs
        post.content = ""

        # Add images to the post
        for i, image_url in enumerate(images):
            # Add image HTML tag directly to the content
            post.content += f'<img src="{image_url}" alt="Image {i+1}">'

        # Add text content after the images
        post.content += f"<p>{content}</p>"

        post.post_status = 'publish'

        # Publish the post
        post_id = wp.call(NewPost(post))
        return post_id

    except ServerConnectionError as e:
        st.error(f"Error connecting to the WordPress server: {e}")
        st.stop()

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.stop()

# Initialize Streamlit app
st.set_page_config(page_title="Gemini Q&A Demo")
st.header("Gemini Application")

# User input for Q&A
qa_input = st.text_input("Prompt for Text Generation: ", key="qa_input")
qa_generate = st.button("Generate Text")


# If the Generate Text button is clicked for Q&A
if qa_generate:
    # Get Gemini response for Q&A
    qa_response = get_gemini_response(qa_input)

    # Display Q&A response
    st.subheader("Gemini Text Generation:")
    st.write(qa_response)
    """for chunk in qa_response:
        st.write(chunk.text)
        st.markdown("---")"""

# User input for image generation
input_image = st.text_input("Prompt for Image Generation: ", key="input_image")

# Buttons to trigger image generation and WordPress publishing
submit_images = st.button("Fetch Images")

# If the Fetch Images button is clicked
if submit_images:
    qa_response = get_gemini_response(qa_input)

    # Fetch images related to the prompt from Unsplash
    prompt_images = fetch_images(input_image)

    # Display fetched images
    for i, image_url in enumerate(prompt_images):
        st.image(image_url, caption=f"Image {i+1}", use_column_width=True)

    # Publish to WordPress with the provided input prompt as the title
    #post_title_images = input_image if input_image else "Gemini Image Demo Post"
    post_title = qa_input if qa_input else "Gemini Image Demo Post"
    post_id_images = publish_to_wordpress(post_title, qa_response, prompt_images)

    # Display success message for image generation
    st.subheader("WordPress Image Post Published Successfully!")
    st.write(f"Post ID: {post_id_images}")
