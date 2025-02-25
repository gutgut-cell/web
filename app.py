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
    "private_key_id": "f977a46992850b5fe3ba33b6915ee4994bce9429",
    "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCzQYJZlL7XwOn3
2RJUJRRa7GaaWDfVcprVM7x3hQqCachMv2peqtP7iqBS0ZIplh4Wgxx4cLaDVmWO
QaomLLOBP9ngTudxdTG9X+WM65DVvq953h7xMYq6319W5xz8TfMuPXBWB2EkBwBS
Pph+ceO/oJnd1Tlbx2r9HkQ2/B0OrOzU7ftFR/tnPDrhxm5bbZQasjYx9rG91kCq
Rj42+/TVqr5Ss+G+Is0UMJkpbC+471cCK/RKVJ25i0KhKfBCXU6eH2E0z3qr1Kkg
axu48+L0GdL5AHHe8FLtctepWQv5V976pZ/cybSy21IgrGTAVbwXpMDRh5EO9UGg
+d+fEqZfAgMBAAECggEACIML1YUiqswWUBaWsDgyhz7CgIG/5PrUL1uNj39ZyGeN
g1dzjZs/BarHgidBcYgXVapUJ8PyZroriF3F3powy+pkRip5AwI1onBzTgXBkuTD
IF5TydA4bjc9J7tBvRlWetOgCfW/vx41/bHLO/XcgrT1mXsOhjUp92sAgjvmhVPM
UC2/xWAIRJ20bfLlOPTVd/IjD02P4C+5PhuNmkQcmvlcXY7+gwqVLhM6oRE2ktqu
LMZwTihJvkFT97MZWQrR2MgYFjF0ArZzvRDFPorC7XwjPmNQhhm1lhiSXu/RTg38
d+If6Bqg8cH55qYKYWTvKZ53o+Z9MDb6ZzBZGVFBwQKBgQDwdwZ9MHB1KhGMF6wZ
HZMj0YN8B60AkmnOyak5P+Afs+dJQfSuMsmhhGS9rIcnDLLhc7OSscoAnbm7aN98
L7ZYFeXlBvfGQCaIKc0+eeJfnKWL+HtGb4JYoOZ+XtOd0HOQ6vmVsIdyeQ1bnhd2
JoSnz+XYf3fHRAj1yqxDxUZtCwKBgQC+1iqfYyv0ar4CubS5nRu4SI6P7bEUukOG
dPLsy4iC8ePCJtiIRX/6zvCnJQ01Fr6tiiRiiLLEDmdkQZS7dv+RjANzG0oIUH7f
hbYGGt9gcTJoW3TOhu/6UKX56EjdjaOak2hF4F54fLC0ph+0vBgbo2qRQcNb/zpk
/uD/vp84fQKBgDQYNSmt8s8PPBnzju8p/xSFcUzPhOVY0t9fxO+ILQ/xM6wlQ9Lx
YclCG2kUFXuaPq6lGEQxjCeyA+jcAX6v/3r504JYjhk/EJnzJGnike5Qy3SVcm+B
/OUihozeEk5gOIkuvr91LQLZwtEUYNTR529LlOngQ5zB2ocVT1inRmidAoGAELhW
96wKt9l6WGbI7NJVEWpaA0ZCE5zWObuZZSHYDhD/cY1Rv27HbcQf1aUraRFbF31Y
/sEXWJIigOg2Dc65SZlI3Bbx/5R96Tuf3R0RoTOJxRbuPwIXmIjkYeb2K2MziGGN
60FjRY83NDyx3nX0bsd8mMl4QmE0TpD+San77UkCgYAqYZvXP/svZ1Zeq6AxSgGn
MkSxgTGYFUm//sNEyvH4kACP9DR2TxxNCFn7CFhYBvOfWlR+eD7Z7zhq0FtohnEZ
xpo7iU/TYgPfjG5qBXJERki8DF3/3eEKLhnfX5QXDSXnEcD69dOMBUuoAfeemT8N
ggM6i3qS7JnEQCffxdSV6g==
-----END PRIVATE KEY-----""",
    "client_email": "id-shoo@website-451921.iam.gserviceaccount.com",
    "client_id": "113352289973589150404",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/id-shoo%40website-451921.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

# Set up Google API Credentials
SCOPES = ["https://www.googleapis.com/auth/drive"]
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

