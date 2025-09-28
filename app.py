from flask import Flask, request, render_template, url_for
import pandas as pd
import os
import difflib

app = Flask(__name__)

# Load recipes from external CSV file (safe path resolution)
def load_recipes():
    csv_path = os.path.join(app.root_path, "recipes.csv")
    if not os.path.exists(csv_path):
        # Return empty DataFrame with expected columns if CSV not found
        return pd.DataFrame(columns=["RecipeName", "Ingredients", "Instructions"])
    # Use try/except in case of encoding/format issues
    try:
        return pd.read_csv(csv_path)
    except Exception as e:
        print("Error loading recipes.csv:", e)
        return pd.DataFrame(columns=["RecipeName", "Ingredients", "Instructions"])

# Function to recommend recipes based on user ingredients
def normalize_ingredient_list(text):
    # Accept list or comma-separated string and return a set of normalized strings
    if isinstance(text, (list, tuple, set)):
        items = text
    else:
        items = [i.strip() for i in str(text).split(",") if i.strip()]
    return set(i.lower() for i in items)

def build_normalized_set_with_map(text):
    # Returns (set_lowercased, original_token_map_lower_to_original)
    if isinstance(text, (list, tuple, set)):
        items = text
    else:
        items = [i.strip() for i in str(text).split(",") if i.strip()]
    lower_to_original = {}
    for token in items:
        lower_to_original[token.lower()] = token
    return set(lower_to_original.keys()), lower_to_original

def recommend_recipes(user_ingredients_list, recipes_df):
    # Build user sets and maps for fuzzy display
    user_set, user_map = build_normalized_set_with_map(user_ingredients_list)
    matches = []

    for _, row in recipes_df.iterrows():
        # Split recipe ingredients by comma, semicolon, or " and " (basic handling)
        raw = row.get("Ingredients", "")
        # Replace common separators to simplify splitting
        raw = str(raw).replace(";", ",").replace(" and ", ",")
        recipe_set, recipe_map = build_normalized_set_with_map(raw)

        if not recipe_set:
            continue

        # First compute exact overlaps
        exact_matches = recipe_set.intersection(user_set)

        # For remaining recipe ingredients not exactly matched, try fuzzy matching
        remaining_recipe = sorted(list(recipe_set - exact_matches))
        remaining_user = sorted(list(user_set - exact_matches))

        fuzzy_pairs = []
        fuzzy_threshold = 0.8  # tune as desired
        for r in remaining_recipe:
            # find closest user ingredient
            if not remaining_user:
                break
            candidate = difflib.get_close_matches(r, remaining_user, n=1, cutoff=fuzzy_threshold)
            if candidate:
                fuzzy_pairs.append((r, candidate[0]))

        # Build matched and missing sets for scoring and display
        matched_set = set(exact_matches)
        for r, u in fuzzy_pairs:
            matched_set.add(r)

        matched_count = len(matched_set)
        total_needed = len(recipe_set)
        if matched_count == 0:
            continue

        coverage_score = matched_count / max(total_needed, 1)
        missing_set = recipe_set - matched_set

        # Prepare display-friendly lists with original casing
        matched_display = []
        # Include exact matches and fuzzy pairs with arrows for clarity
        for token in sorted(exact_matches):
            matched_display.append(user_map.get(token, token))
        for r, u in fuzzy_pairs:
            matched_display.append(f"{user_map.get(u, u)} → {recipe_map.get(r, r)}")

        missing_display = [recipe_map.get(m, m) for m in sorted(missing_set)]

        matches.append({
            "RecipeName": row.get("RecipeName", "Unnamed Recipe"),
            "Ingredients": row.get("Ingredients", ""),
            "Instructions": row.get("Instructions", ""),
            "Matched": ", ".join(matched_display),
            "Missing": ", ".join(missing_display),
            "_score": coverage_score,
            "_matched": matched_count,
            "_missing": len(missing_set),
            "_total": total_needed
        })

    if not matches:
        return pd.DataFrame(columns=["RecipeName", "Ingredients", "Instructions", "Matched", "Missing"]) 

    df = pd.DataFrame(matches)
    # Sort: highest coverage, fewest missing, then more matched, then shorter list
    df = df.sort_values(by=["_score", "_missing", "_matched", "_total"], ascending=[False, True, False, True])
    # Return only display columns; sorting already applied
    return df[["RecipeName", "Ingredients", "Instructions", "Matched", "Missing"]]

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    message = None
    results = None

    if request.method == "POST":
        raw = request.form.get("ingredients", "")
        if not raw.strip():
            error = "Please enter at least one ingredient."
        else:
            # Prepare user ingredients set
            user_ingredients = [i.strip().lower() for i in raw.split(",") if i.strip()]
            recipes = load_recipes()
            results_df = recommend_recipes(user_ingredients, recipes)

            if results_df.empty:
                message = "No recipes found that use only the given ingredients."
            else:
                # Show top 10 closest recipes
                top_df = results_df.head(10)
                results = top_df.to_dict("records")
                message = f"Showing {len(results)} closest recipes."

    return render_template("index.html", results=results, error=error, message=message)

if __name__ == "__main__":
    # Use 0.0.0.0 if you want it reachable from other devices on the local network
    app.run(debug=True)
