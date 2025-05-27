import os
import time
import json
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup


def sanitize_filename(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in (' ', '_', '-')).rstrip()


def download_image(url: str, dest_path: str):
    try:
        resp = requests.get(url, stream=True)
        resp.raise_for_status()
        with open(dest_path, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)
    except Exception as e:
        print(f"Failed downloading image {url}: {e}")


def scrape_allrecipes(url: str, output_dir: str) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; RecipeBot/1.0; +https://yourdomain.com/bot)'
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    title = soup.find('title').get_text(strip=True)
    safe_title = sanitize_filename(title)
    recipe_dir = os.path.join(output_dir, safe_title)
    os.makedirs(recipe_dir, exist_ok=True)

    main_image_url = None
    ld = soup.find('script', type='application/ld+json')
    if ld:
        try:
            data = json.loads(ld.string)
            if isinstance(data, list):
                data = next((x for x in data if x.get('@type') == 'Recipe'), data[0])
            img = data.get('image')
            if isinstance(img, list):
                main_image_url = img[0]
            elif isinstance(img, str):
                main_image_url = img
        except Exception:
            pass
    if not main_image_url:
        og = soup.find('meta', property='og:image')
        if og:
            main_image_url = og.get('content')

    main_image_path = None
    if main_image_url:
        ext = os.path.splitext(urlparse(main_image_url).path)[1] or '.jpg'
        main_image_path = os.path.join(recipe_dir, f"main_image{ext}")
        download_image(main_image_url, main_image_path)

    ingredients = [
        li.get_text(separator=' ', strip=True)
        for li in soup.select('li.mm-recipes-structured-ingredients__list-item p')
    ]

    step_texts = []
    for idx, li in enumerate(soup.select('div.mm-recipes-steps__content ol li'), start=1):
        text = li.get_text(strip=True)

        # Clean known credits
        credits_to_remove = [
            "Dotdash Meredith Food Studios",
            "Allrecipes Video",
            "Jason Donnelly / Food Styling: Holly Dreesman / Prop Styling: Lexi Juhl, Dera Burreson",
            "John Mitzewich",
            "Recipe TipYou can make the pastry cream a day in advance; store in the fridge until needed.",
            "DOTDASH MEREDITH FOOD STUDIOS"
        ]
        for credit in credits_to_remove:
            text = text.replace(credit, '').strip()

        # Download step image if present, but don't store in JSON
        img_tag = li.find('img')
        if img_tag:
            img_url = img_tag.get('data-src') or img_tag.get('src')
            if img_url:
                ext = os.path.splitext(urlparse(img_url).path)[1] or '.jpg'
                img_path = os.path.join(recipe_dir, f"step_{idx}{ext}")
                download_image(img_url, img_path)

        numbered_text = f"{idx}. {text}"
        step_texts.append(numbered_text)

    prep_time = cook_time = nutrition = None
    if ld:
        try:
            prep_time = data.get('prepTime')
            cook_time = data.get('cookTime')
            nutrition = data.get('nutrition')
        except Exception:
            pass

    recipe = {
        'title': title,
        'main_image': main_image_path,
        'ingredients': ingredients,
        'steps': step_texts,
        'prep_time': prep_time,
        'cook_time': cook_time,
        'nutrition': nutrition,
        'source_url': url
    }
    return recipe


if __name__ == '__main__':
    urls = [
        'https://www.allrecipes.com/chicken-primavera-pasta-bake-recipe-11734183',
        'https://www.allrecipes.com/recipe/81108/classic-macaroni-salad/',
        'https://www.allrecipes.com/recipe/16080/judys-strawberry-pretzel-salad/',
        'https://www.allrecipes.com/pulled-chicken-shawarma-sandwich-recipe-11733785',
        'https://www.allrecipes.com/strawberry-rhubarb-crumble-recipe-11724393',
        'https://www.allrecipes.com/recipe/15022/veggie-pizza/',
        'https://www.allrecipes.com/recipe/12775/spicy-grilled-shrimp/',
        'https://www.allrecipes.com/recipe/236197/california-club-chicken-wraps/',
        'https://www.allrecipes.com/recipe/25842/real-nawlins-muffuletta/',
        'https://www.allrecipes.com/recipe/134483/chicago-style-hot-dog/',
        'https://www.allrecipes.com/recipe/75290/tex-mex-burger-with-cajun-mayo/',
        'https://www.allrecipes.com/recipe/254804/chef-johns-nashville-hot-chicken/',
        'https://www.allrecipes.com/bang-bang-chicken-casserole-recipe-11733732',
        'https://www.allrecipes.com/swedish-princess-cake-prinsesstarta-recipe-11730456',
        'https://www.allrecipes.com/recipe/23882/asparagus-casserole-with-hard-boiled-eggs/',
        'https://www.allrecipes.com/recipe/7946/sour-cream-banana-cake/',
        'https://www.allrecipes.com/recipe/238423/dads-creamy-cucumber-salad/',
        'https://www.allrecipes.com/recipe/215041/campfire-pepperoni-pizza/',
        'https://www.allrecipes.com/recipe/215435/crescent-pizza-pockets/'
    ]
    output_dir = 'recipes_output'
    os.makedirs(output_dir, exist_ok=True)

    all_recipes = []
    for url in urls:
        try:
            recipe = scrape_allrecipes(url, output_dir)
            all_recipes.append(recipe)
            time.sleep(2)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    with open(os.path.join(output_dir, 'recipes_data.json'), 'w', encoding='utf-8') as f:
        json.dump(all_recipes, f, ensure_ascii=False, indent=2)

    print(f"Scraped {len(all_recipes)} recipes. Data saved in {output_dir}.")
