import csv
import json
import os

# --- CONFIGURATION ---
CATEGORIES_FILE = 'categories.csv'
IMAGES_FILE = 'images.csv'
ANIMALS_FILE = 'animals.csv'
OUTPUT_FILE = 'data.js'

def load_csv_data(filename):
    """Reads a CSV file and returns a list of dictionaries."""
    if not os.path.exists(filename):
        print(f"❌ Error: Could not find {filename}")
        return []
    
    with open(filename, mode='r', encoding='utf-8-sig') as f:
        # distinct_reader automatically uses the header row as keys
        reader = csv.DictReader(f)
        return list(reader)

def main():
    print("⚙️  Starting Build Process...")

    # 1. Load Categories
    # We want these exactly as they are in the CSV
    categories_raw = load_csv_data(CATEGORIES_FILE)
    print(f"   ...Loaded {len(categories_raw)} categories.")

    # 2. Load Images
    # We convert this list into a Dictionary for faster lookup
    # Format: { "Lion": "images/lion.jpg", ... }
    images_raw = load_csv_data(IMAGES_FILE)
    image_map = {row['id']: row['filepath'] for row in images_raw}
    print(f"   ...Loaded {len(image_map)} image paths.")

    # 3. Load Animal Scores & Combine
    animals_raw = load_csv_data(ANIMALS_FILE)
    final_animals_obj = {}

    for row in animals_raw:
        # The 'Animal' column is the key (e.g., "Lion")
        # Pop it off so it's not included in the score list
        animal_name = row.pop('id', None)
        
        if not animal_name:
            continue

        # Convert all score strings ("100") to integers (100)
        # We assume all remaining columns are category scores
        scores = {}
        for cat_id, score_str in row.items():
            if score_str.strip() == "":
                scores[cat_id] = 0
            else:
                try:
                    scores[cat_id] = int(score_str)
                except ValueError:
                    print(f"⚠️  Warning: Invalid score for {animal_name} in {cat_id}. Setting to 0.")
                    scores[cat_id] = 0

        # Inject the image path if it exists
        if animal_name in image_map:
            scores['image'] = image_map[animal_name]
        else:
            print(f"⚠️  Warning: No image found for {animal_name}")

        # Add to final object
        final_animals_obj[animal_name] = scores

    print(f"   ...Processed {len(final_animals_obj)} animals.")

    # 4. Construct Final Data Structure
    game_config = {
        "categories": categories_raw,
        "animals": final_animals_obj
    }

    # 5. Write to .js file
    # We add "const GAME_CONFIG =" so the browser can read it
    js_content = f"const GAME_CONFIG = {json.dumps(game_config, indent=4)};"
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"\n✅ Success! Created {OUTPUT_FILE}")
    print("   Open index.html to see your changes.")

if __name__ == "__main__":
    main()