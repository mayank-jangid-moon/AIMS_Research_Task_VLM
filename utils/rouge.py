import os
import warnings

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings('ignore')

import evaluate

def compute_notebook_vs_json_rouge():
    
    # Generated summaries from notebook examples
    generated_summaries = {
        'Dads Creamy Cucumber Salad Recipe.jpg': '• **Slice Cucumbers**: Slice cucumbers into ¼-inch thick rounds.\n• **Make Dressing**: Whisk together yogurt, lemon juice, dill, salt, and pepper.\n• **Combine & Chill**: Gently toss cucumbers with dressing, cover, and refrigerate 30 min before serving.',
        'Bang Bang Chicken Casserole Recipe.jpg': '• **Cook Chicken**: Dice chicken and cook in a skillet with soy sauce, ginger, and garlic until browned.\n• **Layer Rice**: Layer cooked rice in a skillet, top with chicken and sauce.\n• **Bake & Top**: Bake at 375°F (190°C) for 15 minutes, sprinkle with sesame seeds and green onions.',
        'Strawberry Rhubarb Crumble Recipe.jpg': '• **Prepare Fruit**: Slice berries (strawberries, raspberries, blackberries) and toss with sugar and lemon juice.\n• **Make Crumble**: Combine flour, oats, butter, brown sugar, and spices; cut into small pieces.\n• **Assemble & Bake**: Layer fruit in a baking dish, top with crumble mixture, and bake at 375°F for 30-40 min, until golden brown.',
        'Chef Johns Nashville Hot Chicken Recipe.jpg': '• **Marinate Chicken**: Marinate chicken pieces in hot sauce, buttermilk, and spices for 30 min.\n• **Coat & Fry**: Coat chicken in cornstarch, deep fry until golden brown and crispy.\n• **Serve & Top**: Place fried chicken on brioche buns, top with pickles and hot sauce.',
        'Classic Macaroni Salad Recipe with Video.jpg': '• **Cook Pasta**: Cook elbow macaroni according to package directions. Drain and rinse with cold water.\n• **Make Dressing**: Whisk together mayonnaise, relish, onion, celery, and spices.\n• **Combine**: Toss pasta with dressing and mix in chopped red peppers and ham. Chill before serving.'
    }
    
    # Reference summaries extracted from JSON file
    reference_summaries = {
        'Classic Macaroni Salad Recipe with Video.jpg': '• **Cook Pasta**: Boil elbow macaroni in lightly salted water until tender (~8 min), rinse under cold water, and drain.\n• **Mix Dressing**: Whisk together mayonnaise, sugar, vinegar, mustard, salt, and pepper; toss with pasta.\n• **Combine & Chill**: Stir in celery, onion, green pepper, carrot, and pimentos. Refrigerate at least 4 hours or overnight.',
        'Strawberry Rhubarb Crumble Recipe.jpg': '• **Prepare Filling**: Preheat oven to 375°F. Toss strawberries and rhubarb with sugar, cornstarch, and salt; pour into a baking dish.\n• **Make Topping**: Mix flour, almonds, sugar, melted butter, lemon zest, and salt; chill slightly.\n• **Bake & Cool**: Cover fruit with topping and bake about 1 hour until golden and bubbly. Let stand 30 min before serving.',
        'Chef Johns Nashville Hot Chicken Recipe.jpg': '• **Marinate & Dredge**: Marinate chicken in buttermilk, brine, and hot sauce 2-4 hrs. Dredge twice in seasoned flour and rest 15 min.\n• **Fry Chicken**: Fry in 350°F oil 8-10 min per side until internal temp is 160°F.\n• **Make Sauce**: Melt butter and lard with cayenne, sugar, paprika, and seasonings. Brush over chicken and serve.',
        'Bang Bang Chicken Casserole Recipe.jpg': '• **Brown Chicken**: Toss chicken with onion powder, Sriracha, soy sauce, garlic, and flour. Brown in batches in a hot skillet.\n• **Simmer & Bake**: Stir in rice, sauces, vinegar, garlic, and broth. Bring to boil, top with chicken, cover, and bake at 375°F for 22-25 min.\n• **Add Sauce**: Whisk mayo, sweet chili sauce, Sriracha, and vinegar. Drizzle over casserole; garnish with scallions and sesame seeds.',
        'Dads Creamy Cucumber Salad Recipe.jpg': '• **Salt & Drain**: Mix cucumbers and onion with salt; rest 15-30 min. Drain in colander until liquid reduces.\n• **Make Dressing**: Whisk mayo, vinegar, sugar, dill, garlic powder, and pepper until smooth.\n• **Toss & Chill**: Mix cucumbers with dressing. Cover and refrigerate 1-2 hours before serving.'
    }
    
    # Match generated and reference summaries
    matched_pairs = []
    for image_name in generated_summaries:
        if image_name in reference_summaries:
            matched_pairs.append({
                'image': image_name,
                'generated': generated_summaries[image_name],
                'reference': reference_summaries[image_name]
            })
    
    if not matched_pairs:
        print("No matched pairs found.")
        return
    
    # Calculate ROUGE scores
    rouge = evaluate.load("rouge")
    
    predictions = [pair['generated'] for pair in matched_pairs]
    references = [pair['reference'] for pair in matched_pairs]
    
    # Aggregate scores
    agg_scores = rouge.compute(predictions=predictions, references=references, use_stemmer=True)
    
    print("\n=== Notebook vs JSON ROUGE Comparison ===")
    print(f"Total matched recipes: {len(matched_pairs)}")
    print(f"\nAggregate ROUGE Scores:")
    print(f"ROUGE-1 : {agg_scores['rouge1']:.3f}")
    print(f"ROUGE-2 : {agg_scores['rouge2']:.3f}")
    print(f"ROUGE-L : {agg_scores['rougeL']:.3f}")
    
    # Per-recipe scores
    print(f"\n=== Per-Recipe ROUGE Scores ===")
    for i, pair in enumerate(matched_pairs):
        individual_scores = rouge.compute(
            predictions=[pair['generated']], 
            references=[pair['reference']], 
            use_stemmer=True
        )
        print(f"\n{pair['image']}:")
        print(f"  Generated: {pair['generated'][:100]}...")
        print(f"  Reference: {pair['reference'][:100]}...")
        print(f"  ROUGE-1: {individual_scores['rouge1']:.3f}")
        print(f"  ROUGE-2: {individual_scores['rouge2']:.3f}")
        print(f"  ROUGE-L: {individual_scores['rougeL']:.3f}")

def main():
    compute_notebook_vs_json_rouge()

if __name__ == "__main__":
    main()
