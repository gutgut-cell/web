import os
import random
import requests
import io
from flask import Flask, render_template
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google import genai
from google.genai import types
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Google Drive API Credentials (Embedded JSON Key)
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "website-451921",
  "private_key_id": "4a095ddb921485a6401dfb1df55c86e386e55120",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCj4zByq+Nzj+96\ncTyeW7NNzxm+GwlxK96iwTxgeocl02HZWNsOWiGlSTMutkP6W0viCajpHVOBn/eu\nwweUIN22O6doHBr/GXiwe+25iq1rlWxMt4KAbdtrQCOBWokbP5iTiNKAaDsmUZpn\nt4Dtxb3ZBJsBMqnoOrzMgFOWlbDjl9yyX6MLejCX419Rk/9kDxd0Mcqqe29PsGlg\nvr7iQGOF/i4+JP/47lNpsrX9JmPKcI07K5s/iZezm296w8PgNh0kkQkpiB0G2fZn\n/s88UmL4EG/MehzzPmoDJk6dz1Eq8x92THqhesAkoOczRMVrqKekH3yB4BhuZAXZ\n7VyhpXTFAgMBAAECggEAC0FFOL7SvEM4hk9kAxkXl4KfSTW4oIfLfqBoKdUIVoHt\nkJxgUNxCPsRn6i+UvAsMi02wBrBfpYGLpDobGWJnb4YpwUXa2cWRSwd7xDgAoGiO\n2zboFLNWtAcf2RiTXWZw70Lgd/aQh1ln0fMhfNLNbqu5DGxDDGKKSD4Q34DQuNR/\nAV124gnk7izxNM8RLsLlSqWw5R9NZVi64OARd+FGt+nmCApHWL/o5y7+hlMcdFkq\n5IcvDyQrax68AkYCbQXwTNtJlB+N50Y1MEcHrYfZA7oBlS8+lDCDq2PnmggkloDi\npVw/AmwwkKFRGAJVxElhpiWbRfw0rm9wy5Rr20uf0QKBgQDlG2BF4br4FP2nELv9\n5sRGs0RS9CdUyyztXbiJAmsDaVCB96TyVdlcfdN+CxMQCLwI8E8Xt/wUVP1/iDuj\n6+EhSuW+RihIxxIC/7TL1dpeV1/JQzI+1EMwjBvP4/M2L0QYD4rZo9W51o1weoFj\nYIftIrjrnIHKysqHilxkhSEVMQKBgQC3H/qknh7kx+Y5YjsMLaR0UngCXcx5Peem\nhe9sx7eJXgMQ+DsQosTIyW/zWFnmDYS5b2NI2qehssLmzbcqvtSTCH13M8tUZNww\nEfKtcBR5/n9KQLZiMuJDLr44XqsN6CIH1Acg8hY3Icm09SxWlu3TO3BMAoGLeSHV\nnpolBQND1QKBgA6rJgrTXQktLuBXbfHfqIluSN2WzD3dlE7ORVZgVUGuqHzpwiHR\n5UzKsZPMWbgZFxDrceTu3rDekCxuKINiQtPC29rG2yVtuXV/sa+rTYPkzDkymDD1\nniepkM5KpfO+KvnvZNBycOipF/0vmsEmGQ3Rv002hAjb2wO6lBfLfkbBAoGBAI0V\nQyoudAi4hYOyTWGtjGTd4H2aPF0wN1dRGsvI9nsLhfs982t2q3sxzmFBsUkPIzEm\nQuyvILTwHz5oQPTavrVkthzvN3iWmBkkyr2aevwd+X2Aa8MuBqnRylVtggWd0RIM\n5U0Zlcn16wvSU82GTEYQJg05ZQrKUSneHk3lFcXdAoGBALhA7HliN+WfEYZixGDs\nX3VnEjOmyS0eTJLCZFQ5asV3RgulcENDZ1Yz5Lv+Qd1iauoYL46AbG6MRCAgdhZP\nNyco3fu+pXwJY5lfZvziR2WwqFAODCcIAMkh1lDkRO15saSInbpzbiQljBvVsgCt\n9jCkWSQS2VA1yWBruxOrNdHd\n-----END PRIVATE KEY-----\n",
  "client_email": "anshu-887@website-451921.iam.gserviceaccount.com",
  "client_id": "114418492390381250767",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/anshu-887%40website-451921.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Set up Google API Credentials
# Set up Google API Credentials
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Debugging: Print the service account info before initializing credentials
import json
print(json.dumps(SERVICE_ACCOUNT_INFO, indent=2))  # Debugging

credentials = service_account.Credentials.from_service_account_info(
    SERVICE_ACCOUNT_INFO, scopes=SCOPES
)

FOLDER_ID = "1GcQ6lADVSPWaHnPh8oIFV1zJ7i88mSp4"

def fetch_google_drive_images(folder_id):
    """Fetches both display and processing URLs from Google Drive."""
    service = build("drive", "v3", credentials=credentials)
    
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType contains 'image/'",
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    if not files:
        return [("https://via.placeholder.com/500", None)]  # Default placeholder

    # Generate both display (frontend) and processing (AI) URLs
    image_links = [
        (f"https://lh3.googleusercontent.com/d/{file['id']}",  # Display URL
         f"https://drive.google.com/uc?id={file['id']}&export=download")  # Processing URL
        for file in files
    ]

    return image_links

def get_random_image():
    """Selects a random image and provides both display and processing URLs."""
    images = fetch_google_drive_images(FOLDER_ID)
    if images:
        display_url, process_url = random.choice(images)
        print("Selected Image (Display):", display_url)  # Debugging
        print("Selected Image (Processing):", process_url)
        return display_url, process_url

    return "https://via.placeholder.com/500", None  # Default if no images

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

def fetch_and_validate_image(image_url):
    """Fetches an image from Google Drive for AI processing."""
    try:
        if "drive.google.com" in image_url:
            # Extract the file ID from the URL
            file_id = image_url.split("id=")[-1].split("&")[0]
            service = build("drive", "v3", credentials=credentials)

            # Download the image file
            request = service.files().get_media(fileId=file_id)
            file_data = io.BytesIO(request.execute())  # Fetch bytes
            file_data.seek(0)

            # Convert to a valid image format
            image = Image.open(file_data)
            image = image.convert("RGB")  # Ensure RGB format
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")  # Convert to JPEG
            return img_byte_arr.getvalue()  # Return raw bytes

        # If it's a normal image URL, fetch it normally
        response = requests.get(image_url, stream=True)
        if response.status_code != 200:
            print(f"Error fetching image: {response.status_code}")
            return None

        image = Image.open(io.BytesIO(response.content))
        image = image.convert("RGB")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format="JPEG")
        return img_byte_arr.getvalue()

    except Exception as e:
        print("Exception in processing image:", str(e))
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
                """Write a romantic or funny 4 line poem based on this image.
                Output should contain ONLY the poem and no other characters.
                If there is a girl in the image her name is tvisha prasad and she is the poet's girlfriend.
                If there is a guy in the image his name is anshuman and he is the poet.
                Write it from the perspective of the poet.
                Try to implement context from the image
                Optional background info. Only use this if you need more context. Try to keep it randomised dont use the same info for every image:
                she loves billie eilish and finneaas
                she is a big fan of the office(i introduced her to this) and friends
                she loves to read books and watch horror movies
                she loves disney princess movies
                I am from vidya niketan school and she is from vidya shilp academy.
                We both met in college at m s ramaiah institute of technology and have been together since.
                """,
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            ]
        )
        return response.text
    except Exception as e:
        return f"Error generating poem: {e}"

@app.route("/")
def home():
    display_url, process_url = get_random_image()  # Get both URLs
    poem = generate_poem(process_url) if process_url else "No image available."
    return render_template("index.html", image_url=display_url, poem=poem)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port)

