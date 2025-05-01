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
file_paths = ["current.jpg", "GeneratedVideo.mp4", "J2_CN.wav"]
file_names = ["J2_CN", "current", "GeneratedVideo", ]
for file_path, file_name in zip(file_paths, file_names):
    upload_result = cloudinary.uploader.upload(file_path,
                                               resource_type="auto",
                                           public_id=file_name)
    print(upload_result["secure_url"])

#delete the files
# cloudinary.uploader.destroy(file_names[0])
# cloudinary.uploader.destroy(file_names[1])
# cloudinary.uploader.destroy(file_names[2])