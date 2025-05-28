from kaggle_secrets import UserSecretsClient
from huggingface_hub import login
from transformers import AutoProcessor, Gemma3ForConditionalGeneration
from PIL import Image
import torch
import argparse
import os

def load_model():
    # Hugging Face Login
    user_secrets = UserSecretsClient()
    secret_value_0 = user_secrets.get_secret("huggingface_key")
    login(token=secret_value_0)

    # Load the Model
    model_id = "google/gemma-3-4b-it"
    model = Gemma3ForConditionalGeneration.from_pretrained(
        model_id, device_map="auto"
    ).eval()
    processor = AutoProcessor.from_pretrained(model_id)
    
    return model, processor

def create_few_shot_examples(image_dir=None):
    recipes = {
        "noodly tangle": {
            "file": "Classic Macaroni Salad Recipe with Video.jpg",
            "instruction": (
                "• **Cook Pasta**: Boil elbow macaroni in lightly salted water until tender (~8 min), rinse under cold water, and drain.\n"
                "• **Mix Dressing**: Whisk together mayonnaise, sugar, vinegar, mustard, salt, and pepper; toss with pasta.\n"
                "• **Combine & Chill**: Stir in celery, onion, green pepper, carrot, and pimentos. Refrigerate at least 4 hours or overnight."
            )
        },
        "creamy pink layer": {
            "file": "Judys Strawberry Pretzel Salad Recipe.jpg",
            "instruction": (
                "• **Bake Crust**: Preheat oven to 350°F. Mix crushed pretzels, melted butter, and sugar; press into a 9×13-inch pan and bake 10 min.\n"
                "• **Add Filling**: Beat cream cheese with sugar, fold in whipped topping, spread over cooled crust, and chill 30 min.\n"
                "• **Top & Set**: Dissolve Jell-O in boiling water, stir in frozen strawberries until thawed, pour over cream cheese layer, and refrigerate at least 1 hour."
            )
        },
        "spiced shred stack": {
            "file": "Pulled Chicken Shawarma Sandwich Recipe.jpg",
            "instruction": (
                "• **Cook Chicken**: Combine shawarma spices in water with garlic and onion; simmer whole chicken for 1 hour, turning every 20 min. Cool, shred meat, reserve broth.\n"
                "• **Reduce Broth**: Add bones back with water, simmer 1–2 hours, strain, and reduce broth by half.\n"
                "• **Finish & Serve**: Return shredded chicken to broth, cook until saucy, season with lemon juice and extra spices. Serve in bread or wraps."
            )
        },
        "veggie garden layers": {
            "file": "Veggie Pizza Recipe.jpg",
            "instruction": (
                "• **Bake Base**: Preheat oven to 350°F, spray a 15×10-inch pan, press crescent roll dough into pan, bake 10 min, and cool.\n"
                "• **Spread Cream**: Whip sour cream, cream cheese, ranch mix, dill, and garlic salt; spread over crust.\n"
                "• **Top & Chill**: Arrange broccoli, radish, onion, bell pepper, carrot, and celery; chill 1–2 hours, then cut into squares."
            )
        },
        "charred sea pops": {
            "file": "Spicy Grilled Shrimp Recipe.jpg",
            "instruction": (
                "• **Make Paste**: Preheat grill to medium. Crush garlic and salt, stir in paprika, cayenne, olive oil, and lemon juice to form a paste.\n"
                "• **Grill Shrimp**: Toss shrimp with paste. Oil grill grate lightly, grill shrimp 2–3 min per side until opaque.\n"
                "• **Serve Fresh**: Serve with lemon wedges."
            )
        },
        "folded veggie bundle": {
            "file": "California Club Chicken Wraps Recipe.jpg",
            "instruction": (
                "• **Make Spread**: Whisk mayonnaise, yogurt, and chipotle chiles. Microwave tortillas for 30 sec to warm.\n"
                "• **Assemble Wrap**: Spread chipotle mayo down center, top with lettuce, cheese, avocado, bacon, onion, tomato, and chicken.\n"
                "• **Roll & Serve**: Fold opposing edges over filling and roll into a tight wrap."
            )
        },
        "layered olive loaf": {
            "file": "Real Nawlins Muffuletta Recipe.jpg",
            "instruction": (
                "• **Prep Salad**: Chop olives, pepperoncini, cauliflower, cocktail onions, garlic, capers, celery, and carrot; mix with oregano, basil, pepper, celery seed, oils, and vinegar. Refrigerate covered 8 hours or overnight.\n"
                "• **Assemble Loaf**: Halve Italian loaves, hollow centers, spread olive salad on both halves.\n"
                "• **Layer & Slice**: Layer salami, ham, mortadella, mozzarella, and provolone; reassemble loaf and slice into quarters."
            )
        },
        "poppy crunch tube": {
            "file": "Chicago-Style Hot Dog Recipe.jpg",
            "instruction": (
                "• **Cook Dog**: Poach hot dog in simmering water 5 min, steam poppy-seed bun 2 min.\n"
                "• **Add Toppings**: Place dog in bun, layer mustard, relish, onion, tomato wedges, pickle spear, sport peppers.\n"
                "• **Finish Up**: Sprinkle celery salt on top—no ketchup."
            )
        },
        "spiced beef bun": {
            "file": "Tex-Mex Burger with Cajun Mayo Recipe.jpg",
            "instruction": (
                "• **Prep Grill & Sauce**: Preheat grill to medium-high, oil grate. Mix mayo with 1 tsp Cajun seasoning; set aside.\n"
                "• **Make Patties**: Combine beef, onion, 3 tsp seasoning, jalapeño, garlic, and Worcestershire; form patties.\n"
                "• **Grill & Build**: Grill 5 min per side, top with cheese in last 2 min. Spread Cajun mayo on buns, add burger, lettuce, and tomato."
            )
        },
        "cheesy wheel": {
            "file": "Campfire Pepperoni Pizza Recipe.jpg",
            "instruction": (
                "• **Prep Fire & Dough**: Place pizza stone on grill over wood fire. Roll dough to thickness.\n"
                "• **Cook Pizza**: Cook one side 10 min, flip, spread sauce, cheese, and pepperoni. Tent with foil and cook until cheese melts (~10 min).\n"
                "• **Serve Slices**: Cool slightly, slice, and serve."
            )
        }
    }
    
    messages = []
    messages.append({
        "role": "system",
        "content": [{
            "type": "text",
            "text": "You are a multimodal AI assistant specialized in cooking and recipe understanding. Your task is to generate concise cooking instructions (2–3 steps) from a food image and a noisy or vague dish title. Use your understanding of food preparation, ingredients, and cooking processes to infer what the dish likely is and how it is made, even when the input title is unclear or imprecise. Use natural, human-like language, and ensure that the instructions are practical and accurate for preparing the dish.You are also trained to mimic human-written summaries using few-shot examples provided. Do not invent exotic or unsafe steps. Prioritize clarity, brevity, and relevance in your response."
        }]
    })

    if image_dir and os.path.exists(image_dir):
        for vague_title, data in recipes.items():
            img_path = f"{image_dir}/{data['file']}"
            if os.path.exists(img_path):
                img = Image.open(img_path)
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "image", "image": img},
                        {"type": "text", "text": f'Vague Title: "{vague_title}"\nInstruction:'}
                    ]
                })
                messages.append({
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": data['instruction']}
                    ]
                })
    
    return messages

def generate_recipe_instruction(model, processor, image_path, vague_title, few_shot_examples=None):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Prepare messages
    messages = few_shot_examples if few_shot_examples else []
    
    # Load and add test image
    test_img = Image.open(image_path)
    messages.append({
        "role": "user",
        "content": [
            {"type": "image", "image": test_img},
            {"type": "text", "text": f'Vague Title: "{vague_title}"\nInstruction:'}
        ]
    })

    # Process and generate
    inputs = processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt"
    ).to(model.device, dtype=torch.bfloat16)

    input_len = inputs["input_ids"].shape[-1]

    with torch.inference_mode():
        generation = model.generate(**inputs, max_new_tokens=1000, do_sample=True, top_p=0.8, top_k=45)
        generation = generation[0][input_len:]

    decoded = processor.decode(generation, skip_special_tokens=True)
    return decoded

def main():
    parser = argparse.ArgumentParser(description="Generate recipe instructions from image and vague title")
    parser.add_argument("--image", required=True, help="Path to the food image")
    parser.add_argument("--title", required=True, help="Vague title for the dish")
    
    args = parser.parse_args()
    
    # Load model
    print("Loading model...")
    model, processor = load_model()
    
    # Create few-shot examples
    print("Loading few-shot examples...")
    few_shot_examples = create_few_shot_examples("data_scraping/recipe_images/Train")
    
    # Generate instruction
    print("Generating recipe instruction...")
    result = generate_recipe_instruction(model, processor, args.image, args.title, few_shot_examples)
    
    print(f"\nVague Title: {args.title}")
    print(f"Generated Instruction: {result}")

if __name__ == "__main__":
    main()
