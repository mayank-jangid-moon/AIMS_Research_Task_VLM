import os
import shutil

# Paths (change these according to your setup)
source_dir = '/home/mayank/work_space/AIMS_Research/data_scraping/recipes_output'  # Folder containing subfolders named after recipe titles
output_dir = '/home/mayank/work_space/AIMS_Research/recipes_images'      # Where renamed images will be saved

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Image filenames from your list
image_filenames = [
    'Asparagus Casserole with Hard-Boiled Eggs Recipe.jpg',
    'Bang Bang Chicken Casserole Recipe.jpg',
    'California Club Chicken Wraps Recipe.jpg',
    'Campfire Pepperoni Pizza Recipe.jpg',
    'Chef Johns Nashville Hot Chicken Recipe.jpg',
    'Chicago-Style Hot Dog Recipe.jpg',
    'Chicken Primavera Pasta Bake Recipe.jpg',
    'Classic Macaroni Salad Recipe with Video.jpg',
    'Crescent Pizza Pockets Recipe.jpg',
    'Dads Creamy Cucumber Salad Recipe.jpg',
    'Judys Strawberry Pretzel Salad Recipe.jpg',
    'Pulled Chicken Shawarma Sandwich Recipe.jpg',
    'Real Nawlins Muffuletta Recipe.jpg',
    'Sour Cream Banana Cake Recipe.jpg',
    'Spicy Grilled Shrimp Recipe.jpg',
    'Strawberry Rhubarb Crumble Recipe.jpg',
    'Swedish Princess Cake Prinsesstrta Recipe.jpg',
    'Tex-Mex Burger with Cajun Mayo Recipe.jpg',
    'Veggie Pizza Recipe.jpg',
]

for filename in image_filenames:
    folder_name = filename.replace('.jpg', '')  # Get subfolder name
    folder_path = os.path.join(source_dir, folder_name)
    source_image_path = os.path.join(folder_path, 'main_image.jpg')
    output_image_path = os.path.join(output_dir, filename)

    if os.path.exists(source_image_path):
        shutil.copy(source_image_path, output_image_path)
        print(f"Copied and renamed: {filename}")
    else:
        print(f"Image not found: {source_image_path}")

