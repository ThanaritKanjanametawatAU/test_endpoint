import cloudinary
import cloudinary.uploader
import dotenv
import os

dotenv.load_dotenv()

# Configuration       
cloudinary.config( 
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
    api_key = os.getenv("CLOUDINARY_API_KEY"), 
    api_secret = os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Upload an image
upload_result = cloudinary.uploader.upload("current.jpg",
                                           public_id="current")
print(upload_result["secure_url"])