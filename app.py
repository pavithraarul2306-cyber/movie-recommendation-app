import os
import streamlit as st
import pandas as pd
import pickle
import requests
from PIL import Image
from streamlit.components.v1 import html

# If running as API, avoid importing Streamlit at module import time
IS_API = os.environ.get("RUN_API") == "1"

if not IS_API:
    st.set_page_config(page_title="🎬 AI Movie Recommender", layout="wide")

# Suppress noisy browser console warning about unused preload links
if not IS_API:
    html(
    """
<script>
(function(){
  const filters = [
    'was preloaded using link preload',
    'Tracking Prevention blocked access to storage',
    'Unrecognized feature:',
    'allow-scripts and allow-same-origin',
    'about:srcdoc'
  ];
  function shouldFilter(args){
    try {
      const msg = Array.from(args).map(String).join(' ');
      return filters.some(f => msg.includes(f));
    } catch(e) { return false; }
  }
  ['warn','error','info','log'].forEach(method => {
    const orig = console[method];
    console[method] = function(){
      if (shouldFilter(arguments)) { return; }
      return orig.apply(console, arguments);
    };
  });
})();
</script>
""",
        height=0,
    )

@st.cache_data
def load_artifacts():
    try:
        movies = pd.read_parquet("artifacts/movies.parquet")
        with open("artifacts/similarity.pkl", "rb") as f:
            similarity = pickle.load(f)
        return movies, similarity, None
    except Exception as e:
        return None, None, e

def get_tmdb_api_key():
    """Fetch TMDB API key from env first; only read st.secrets if a secrets file exists."""
    env_key = os.getenv("TMDB_API_KEY")
    if env_key:
        return env_key
    # Check for secrets.toml existence to avoid streamlit warnings
    project_secrets = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    home_secrets = os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml")
    if os.path.exists(project_secrets) or os.path.exists(home_secrets):
        try:
            return st.secrets.get("TMDB_API_KEY", None)  # type: ignore[attr-defined]
        except Exception:
            return None
    return None

def ensure_local_placeholder(width=300, height=450, color=(200, 200, 200)):
    """Create a local placeholder image if it doesn't exist and return a PIL Image."""
    assets_dir = "assets"
    os.makedirs(assets_dir, exist_ok=True)
    placeholder_path = os.path.join(assets_dir, f"placeholder_{width}x{height}.png")
    if not os.path.exists(placeholder_path):
        img = Image.new("RGB", (width, height), color)
        img.save(placeholder_path)
    return Image.open(placeholder_path)

def fetch_poster(title, year=None):
    """Fetch poster URL from TMDB. Requires TMDB_API_KEY in st.secrets or env."""
    api_key = get_tmdb_api_key()
    if not api_key:
        return ensure_local_placeholder()
    try:
        query = {"api_key": api_key, "query": title}
        if year and str(year).isdigit():
            query["year"] = int(year)
        r = requests.get("https://api.themoviedb.org/3/search/movie", params=query, timeout=10)
        data = r.json()
        if data.get("results"):
            path = data["results"][0].get("poster_path")
            if path:
                return f"https://image.tmdb.org/t/p/w500{path}"
    except Exception:
        pass
    return ensure_local_placeholder()

def recommend(selected_title, movies, similarity, top_k=5):
    # Get index of selected movie
    idx_list = movies.index[movies["title_clean"] == selected_title].tolist()
    if not idx_list:
        return []
    idx = idx_list[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    results = []
    for movie_idx, sim in scores[1: top_k+6]:  # skip self, pull a few extra
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

st.title("🎬 AI-Powered Movie Recommendation System")
st.write("Type a movie name, pick one, and get similar recommendations based on genres & title (content-based).")

movies, similarity, load_err = load_artifacts()

if load_err:
    st.error(f"Artifacts not found. Please run data_prep.py first. Error: {load_err}")
    st.stop()

# Search box with suggestions
query = st.text_input("🔎 Search a movie", placeholder="e.g., Toy Story (1995)")

if query:
    suggestions = movies[movies["title"].str.contains(query, case=False, na=False)].head(20)
    suggestion_titles = suggestions["title"].tolist()
else:
    suggestion_titles = movies["title"].head(50).tolist()

selected = st.selectbox("🎞️ Select a movie", suggestion_titles if len(suggestion_titles)>0 else [""])

top_k = st.slider("How many recommendations?", min_value=5, max_value=15, value=5, step=1)

colA, colB = st.columns([1, 2])

with colA:
    if selected:
        row = movies[movies["title"] == selected].iloc[0]
        poster = fetch_poster(row["title"], row.get("year"))
        st.image(poster, use_column_width=True)
        st.markdown(f"**{row['title']}**")
        st.caption(row.get("genres", ""))

with colB:
    if selected and st.button("✨ Recommend"):
        recs = recommend(row["title_clean"], movies, similarity, top_k=top_k)
        if not recs:
            st.warning("No recommendations found. Try another title.")
        else:
            grid_cols = st.columns(5)
            for i, rec in enumerate(recs):
                with grid_cols[i % 5]:
                    poster = fetch_poster(rec["title"], rec.get("year"))
                    st.image(poster, use_column_width=True)
                    st.markdown(f"**{rec['title']}**")
                    if rec.get("genres"):
                        st.caption(rec["genres"])
                    st.write(f"Similarity: {rec['score']:.2f}")
            st.info("Posters are fetched via TMDB API. Set your TMDB_API_KEY in Streamlit secrets or environment variables for best results.")
