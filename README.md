# AIMS Research VLM - Recipe Summary Generator

A multimodal AI system that generates concise cooking instructions from food images and vague dish titles using Vision-Language Models (VLM).

## Overview

This project uses the `google/gemma3-4b-it` model to generate recipe instructions by analyzing food images paired with noisy or vague dish titles. The system employs few-shot learning with example recipes to improve instruction quality and consistency.

## Features

- **Multimodal Understanding**: Processes both images and text to generate cooking instructions
- **Few-Shot Learning**: Uses curated examples to improve output quality
- **ROUGE Evaluation**: Comprehensive evaluation metrics for generated instructions
- **Data Collection Pipeline**: Web scraping tools for recipe data and images
- **Flexible Inference**: Command-line interface for easy testing

## Project Structure

```  
├── model.py                      # Main inference script with VLM model
├── utils/  
│   └── rouge.py                  # ROUGE evaluation metrics
├── data_scraping/  
│   ├── scrape.py                 # AllRecipes web scraper
│   ├── recipes_data_train.json   # Training dataset with few-shot examples
│   ├── recipes_data_test.json    # Test dataset for evaluation
│   ├── prompt.json               # Few-shot prompt examples
│   └── recipe_images/  
│       ├── Train/                # AllRecipes web scraper
│       └── Test/                 # Training images for few-shot examples
└── README.md  
```

## Installation

### Install required dependencies:
```bash
pip install transformers torch pillow huggingface_hub kaggle_secrets evaluate
```

### Set up Hugging Face authentication:
   - Store your HF token in Kaggle secrets as "huggingface_key"
   - Or modify the authentication method in `model.py`

## Usage

### Generate Recipe Instructions

```bash
python3 model.py --image path/to/food_image.jpg --title "vague dish description"
```

**Example:**
```bash
python3 model.py --image "data_scraping/recipe_images/Train/Dads Creamy Cucumber Salad Recipe.jpg" --title "chilled green slices"
```

This will compute ROUGE-1, ROUGE-2, and ROUGE-L scores comparing generated instruction summaries against original recipe steps.

### Data Collection

To scrape new recipes from AllRecipes:

```bash
python3 data_scraping/scrape.py
```

The scraper will:
- Download recipe data and images
- Extract ingredients, steps, and metadata
- Save structured JSON data

## Dataset

### Training Data (Few-Shot Examples)
- **10 recipe examples** with vague titles and concise instructions
- Examples include: "green swirl bake", "creamy pink layer", "spiced shred stack"
- Used for in-context learning during inference

### Test Data
- **5 additional recipes** for evaluation
- Examples: "noodly tangle", "chilled green slices", "fiery crunch pieces"

### Data Format
```json
{
  "title": "Recipe Title",
  "main_image": "path/to/image.jpg",
  "ingredients": ["ingredient1", "ingredient2"],
  "steps": "1. Step one...",
  "noisy_title": "vague description",
  "instruction_summary": "Concise cooking instructions..."
}
```

## Model Details

- **Base Model**: google/gemma-3-4b-it
- **Task**: Multimodal recipe instruction generation
- **Input**: Food image + vague title
- **Output**: 2-3 step cooking instructions
- **Technique**: Few-shot in-context learning

## Evaluation

ROUGE metrics compare generated instruction summaries against original recipe steps:

- **ROUGE-1**: Unigram overlap
- **ROUGE-2**: Bigram overlap  
- **ROUGE-L**: Longest common subsequence

Results show both aggregate scores across all recipes and per-recipe breakdowns.

