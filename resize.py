import os
from PIL import Image

# Set input and output folders
input_folder = "/Users/mayankjangid/Desktop/Images"            # change to your image folder
output_folder = "/Users/mayankjangid/Desktop/resized_images"   # resized images will be saved here
target_height = 448

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process each image in the folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path)

        # Calculate new width while keeping aspect ratio
        width, height = img.size
        aspect_ratio = width / height
        new_width = int(target_height * aspect_ratio)

        # Resize image
        resized_img = img.resize((new_width, target_height), Image.LANCZOS)

        # Save resized image
        output_path = os.path.join(output_folder, filename)
        resized_img.save(output_path)

        print(f"Resized: {filename} → {new_width}x{target_height}")
