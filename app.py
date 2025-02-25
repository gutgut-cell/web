import os
import random
import requests
import io
from flask import Flask, render_template, request
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# List of ImgBB images (use the same link for both display & processing)
IMGBB_IMAGES = [
    ("https://i.ibb.co/27vDSy6X/IMG-1674.jpg", "https://i.ibb.co/27vDSy6X/IMG-1674.jpg"),
    ("https://i.ibb.co/0RSfYfHS/IMG-5315.jpg", "https://i.ibb.co/0RSfYfHS/IMG-5315.jpg"),
    ("https://i.ibb.co/Z6sfv9sF/IMG-5297.jpg", "https://i.ibb.co/Z6sfv9sF/IMG-5297.jpg"),
    ("https://i.ibb.co/H3wYpvT/IMG-5182.jpg", "https://i.ibb.co/H3wYpvT/IMG-5182.jpg"),
    ("https://i.ibb.co/Swgc5kHF/IMG-5180.jpg", "https://i.ibb.co/Swgc5kHF/IMG-5180.jpg"),
    ("https://i.ibb.co/gM7fmRsy/IMG-4858.jpg", "https://i.ibb.co/gM7fmRsy/IMG-4858.jpg"),
    ("https://i.ibb.co/VYVxm5zB/IMG-5205.jpg", "https://i.ibb.co/VYVxm5zB/IMG-5205.jpg"),
    ("https://i.ibb.co/gbc8j9QY/IMG-3184.jpg", "https://i.ibb.co/gbc8j9QY/IMG-3184.jpg"),
    ("https://i.ibb.co/TX7VRvP/IMG-0717.jpg", "https://i.ibb.co/TX7VRvP/IMG-0717.jpg"),
    ("https://i.ibb.co/xKJ9CT7w/IMG-1441.jpg", "https://i.ibb.co/xKJ9CT7w/IMG-1441.jpg"),
    ("https://i.ibb.co/NRS7c8w/IMG-1008.jpg", "https://i.ibb.co/NRS7c8w/IMG-1008.jpg"),
    ("https://i.ibb.co/jPjjMv52/IMG-8567.jpg", "https://i.ibb.co/jPjjMv52/IMG-8567.jpg"),
    ("https://i.ibb.co/Rk6y4kd9/20221119-135425.jpg", "https://i.ibb.co/Rk6y4kd9/20221119-135425.jpg"),
    ("https://i.ibb.co/xKGczfyh/IMG-4463.jpg", "https://i.ibb.co/xKGczfyh/IMG-4463.jpg"),
    ("https://i.ibb.co/XZ1zXMDw/IMG-7430-2.jpg", "https://i.ibb.co/XZ1zXMDw/IMG-7430-2.jpg"),
    ("https://i.ibb.co/NnrtDqkZ/IMG-7428-4.jpg", "https://i.ibb.co/NnrtDqkZ/IMG-7428-4.jpg"),
    ("https://i.ibb.co/G3JJ36JK/IMG-7327-2.jpg", "https://i.ibb.co/G3JJ36JK/IMG-7327-2.jpg"),
    ("https://i.ibb.co/tpTsP5WM/8-E95-A0-A6-62-DF-4-BB7-8469-9-CA73-E99-A389-2.jpg", "https://i.ibb.co/tpTsP5WM/8-E95-A0-A6-62-DF-4-BB7-8469-9-CA73-E99-A389-2.jpg"),
    ("https://i.ibb.co/3mwy24rt/IMG-4188-2.jpg", "https://i.ibb.co/3mwy24rt/IMG-4188-2.jpg"),
]

def get_random_image():
    """Selects a random image from ImgBB."""
    if IMGBB_IMAGES:
        display_url, process_url = random.choice(IMGBB_IMAGES)
        print("Selected Image (Display):", display_url)  # Debugging
        print("Selected Image (Processing):", process_url)
        return display_url, process_url

    return "https://via.placeholder.com/500", None  # Default if no images

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_and_validate_image(image_url):
    """Fetches an image from ImgBB for AI processing."""
    try:
        print(f"🔍 Fetching Image: {image_url}")  # Debugging

        response = requests.get(image_url, stream=True)
        if response.status_code != 200:
            print(f"❌ Error fetching image: {response.status_code}")
            return None

        image = Image.open(io.BytesIO(response.content))
        image = image.convert("RGB")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        return img_byte_arr.getvalue()

    except Exception as e:
        print(f"❌ Exception in processing image: {e}")
        return None

def generate_poem(image_url):
    """Generates a poem inspired by the image using Gemini API."""
    image_bytes = fetch_and_validate_image(image_url)
    if not image_bytes:
        return "Could not process the image."

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                """Write a romantic or funny 4-line poem based on this image.
                Output should contain ONLY the poem and no other characters.
                If there is a girl in the image, her name is Tvisha Prasad and she is the poet's girlfriend.
                If there is a guy in the image, his name is Anshuman and he is the poet.
                Write it from the perspective of the poet.
                Try to implement context from the image.
                Optional background info (randomized for variety):
                - She loves Billie Eilish and Finneas.
                - She is a big fan of The Office (I introduced her to it) and Friends.
                - She loves reading books and watching horror movies.
                - She loves Disney princess movies.
                - I am from Vidya Niketan School, and she is from Vidya Shilp Academy.
                - We met in college at M.S. Ramaiah Institute of Technology and have been together since.
                """,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ]
        )
        return response.text
    except Exception as e:
        return f"Error generating poem: {e}"

@app.route("/", methods=["GET"])
def home():
    if request.method == "HEAD":
        print("🚀 Render Health Check - Skipping Image Fetch")
        return "", 200  # Respond with a simple 200 OK

    display_url, process_url = get_random_image()  # Get both URLs
    poem = generate_poem(process_url) if process_url else "No image available."
    return render_template("index.html", image_url=display_url, poem=poem)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    print(f"🔥 Starting Flask on 0.0.0.0:{port}")  # Debugging log
    app.run(host="0.0.0.0", port=port, debug=True)
