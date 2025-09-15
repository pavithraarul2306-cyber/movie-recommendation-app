import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Instructions:
# 1) Download MovieLens "ml-latest-small" from https://grouplens.org/datasets/movielens/
# 2) Unzip; then set MOVIELENS_DIR to the folder containing movies.csv (e.g., ./ml-latest-small)
# 3) Run: python data_prep.py
# 4) This will create artifacts/movies.parquet and artifacts/similarity.pkl

MOVIELENS_DIR = os.environ.get("MOVIELENS_DIR", "ml-latest-small")  # change if needed
ARTIFACTS_DIR = "artifacts"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

movies_path = os.path.join(MOVIELENS_DIR, "movies.csv")

if not os.path.exists(movies_path):
    raise FileNotFoundError(f"movies.csv not found at {movies_path}. Set MOVIELENS_DIR correctly.")

# Load movies
movies = pd.read_csv(movies_path)  # columns: movieId,title,genres

# Extract year from title if present, e.g., "Toy Story (1995)"
def extract_year(title):
    if isinstance(title, str) and title.strip().endswith(")") and "(" in title:
        try:
            return int(title.strip()[-5:-1])
        except Exception:
            return None
    return None

movies["year"] = movies["title"].apply(extract_year)

# Clean title for matching (drop year in brackets)
def clean_title(title):
    if not isinstance(title, str):
        return ""
    if "(" in title:
        return title[: title.rfind("(")].strip()
    return title.strip()

movies["title_clean"] = movies["title"].apply(clean_title)

# Prepare text corpus: title + genres (replace '|' with space)
movies["genres"] = movies["genres"].fillna("").replace("(no genres listed)", "").astype(str)
movies["genres_space"] = movies["genres"].str.replace("|", " ", regex=False)
movies["text"] = (movies["title_clean"].fillna("") + " " + movies["genres_space"].fillna("")).str.lower()

# TF-IDF
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies["text"].values)

# Cosine similarity matrix
similarity = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Save artifacts
movies_out = movies[["movieId", "title", "title_clean", "year", "genres"]].copy()
movies_out.to_parquet(os.path.join(ARTIFACTS_DIR, "movies.parquet"), index=False)

with open(os.path.join(ARTIFACTS_DIR, "similarity.pkl"), "wb") as f:
    pickle.dump(similarity, f)

print("Artifacts created in ./artifacts")
