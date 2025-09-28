# Recipe Recommendation System

A small Flask web app that recommends recipes based on provided ingredients. Uses a CSV file (`recipes.csv`) as the recipe data source and performs fuzzy/exact matching to surface closest recipes.

## Features
- Accepts comma-separated ingredients from user input.
- Finds recipes by exact and fuzzy matches (difflib).
- Shows matched and missing ingredients for each recommended recipe.
- Responsive grid layout for results (3 columns × up to 4 rows by default).
- Static assets live under `static/` and templates under `templates/`.

## Repo structure
- app.py — Flask application and recommendation logic  
- templates/index.html — main UI template  
- static/style.css — site styles  
- recipes.csv — (not included) CSV with columns: `RecipeName,Ingredients,Instructions`  
- static/recipe.gif — optional header gif used by the UI

## Requirements
- Python 3.8+ (recommended)
- pip

## Installation & run (quick)
1. Clone the repository:
   git clone <repo-url>
2. Create and activate a virtual environment:
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
3. Install dependencies:
   pip install flask pandas
4. Add recipe data:
   Place `recipes.csv` in the project root (same folder as `app.py`). CSV should include headers: `RecipeName,Ingredients,Instructions`.
5. Run the app:
   python app.py
6. Open http://127.0.0.1:5000 in your browser.

Notes:
- The app will handle an absent `recipes.csv` gracefully (shows no results).
- Results are limited in the UI to the first 12 entries (3 columns × 4 rows). Adjust template or CSS if you need different limits or sizes.
- To make the container fixed-size with internal scrolling, the CSS sets a fixed height on `.container`.

## Screenshots
(Place your screenshots in `static/` as `gbg1.png` and `gbg2.png`.)

<!-- Side-by-side display; GitHub README supports inline HTML -->
<p align="center">
  <img src="static/gbg1.png" alt="Screenshot 1" style="width:45%; margin-right:2%;">
  <img src="static/gbg2.png" alt="Screenshot 2" style="width:45%;">
</p>

## Contributing
- Feel free to submit issues or pull requests.
- For large changes, open an issue first to discuss.

## License
MIT License — include LICENSE file if you want to publish this publicly.