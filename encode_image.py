import base64
from PIL import Image

def encode_image(image_path):
    image = Image.open(image_path)
    with open("encoded_current.txt", "w") as f:
        f.write(base64.b64encode(image.tobytes()).decode('utf-8'))

if __name__ == "__main__":
    encode_image("current.jpg")
    print("Encoded image and saved to encoded_current.txt")