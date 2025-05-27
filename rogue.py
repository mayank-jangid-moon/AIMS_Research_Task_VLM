import json
import sys
import evaluate

JSON_PATH = "/home/mayank/work_space/AIMS_Research/data_scraping/recipes_data_high_rouge.json"

def load_recipes(path):
    """Load list of recipes from a JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compute_aggregate_rouge(predictions, references):
    """Compute aggregate ROUGE scores over all pairs."""
    rouge = evaluate.load("rouge")
    return rouge.compute(predictions=predictions, references=references, use_stemmer=True)

def compute_per_recipe_rouge(recipes):
    """Compute ROUGE scores for each recipe individually."""
    rouge = evaluate.load("rouge")
    per_recipe = []
    for recipe in recipes:
        summary = recipe.get('instruction_summary', '')
        steps   = recipe.get('steps', '')
        scores  = rouge.compute(
            predictions=[summary],
            references=[steps],
            use_stemmer=True
        )
        per_recipe.append({
            'title': recipe.get('title', 'Untitled'),
            'rouge1_f1': scores['rouge1'],
            'rouge2_f1': scores['rouge2'],
            'rougeL_f1': scores['rougeL'],
        })
    return per_recipe

def main():
    # 1. Load data
    recipes = load_recipes(JSON_PATH)

    # 2. Prepare lists for aggregate
    preds = [r.get('instruction_summary','') for r in recipes]
    refs  = [r.get('steps','')                for r in recipes]

    # 3. Compute and print aggregate ROUGE
    agg_scores = compute_aggregate_rouge(preds, refs)
    print("\n=== Aggregate ROUGE (F1) ===")
    print(f"ROUGE-1 : {agg_scores['rouge1']:.3f}")
    print(f"ROUGE-2 : {agg_scores['rouge2']:.3f}")
    print(f"ROUGE-L : {agg_scores['rougeL']:.3f}")

    # 4. Compute and print per-recipe ROUGE
    print("\n=== Per-recipe ROUGE (F1) ===")
    per_recipe = compute_per_recipe_rouge(recipes)
    for rec in per_recipe:
        print(f"- {rec['title']}")
        print(f"    ROUGE-1 : {rec['rouge1_f1']:.3f}")
        print(f"    ROUGE-2 : {rec['rouge2_f1']:.3f}")
        print(f"    ROUGE-L : {rec['rougeL_f1']:.3f}")

if __name__ == "__main__":
    main()
