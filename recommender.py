import pandas as pd
import pickle

def load(movies_path="artifacts/movies.parquet", sim_path="artifacts/similarity.pkl"):
    movies = pd.read_parquet(movies_path)
    with open(sim_path, "rb") as f:
        similarity = pickle.load(f)
    return movies, similarity

def recommend_by_title(title, movies, similarity, top_k=5):
    idx_list = movies.index[movies['title_clean'] == title].tolist()
    if not idx_list:
        return []
    idx = idx_list[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    results = []
    for movie_idx, sim in scores[1: top_k+6]:
        row = movies.iloc[movie_idx]
        results.append({
            "title": row["title"],
            "year": row.get("year"),
            "genres": row.get("genres"),
            "score": float(sim),
        })
        if len(results) >= top_k:
            break
    return results
