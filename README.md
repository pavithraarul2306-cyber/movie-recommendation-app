# 🎬 AI-Powered Movie Recommendation System (Set 2) — Naan Mudhalvan Hackathon Level 2

A **Streamlit** app that recommends similar movies using **content-based filtering** (TF‑IDF over *title + genres* from MovieLens). Shows **poster, title, and genres** for each recommendation.

---

## ✨ Features
- Search & select a movie
- Get **5–15 recommendations**
- For each recommendation: **Poster + Title + Genres + Similarity score**
- **TMDB integration** for posters (optional, but recommended)

---

## 🧱 Project Structure
```
movie-recommender-set2/
├─ app.py                  # Streamlit UI
├─ recommender.py          # (Optional) Reco utilities
├─ data_prep.py            # Builds artifacts from MovieLens
├─ artifacts/              # Created after running data_prep.py
│  ├─ movies.parquet
│  └─ similarity.pkl
├─ requirements.txt
└─ README.md
```

---

## 📦 Setup (Local)

1. **Clone / download** this repo.
2. **Create venv** (recommended) and install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. **Download MovieLens** (small) dataset:
   - https://grouplens.org/datasets/movielens/
   - Unzip to `./ml-latest-small/` so that `./ml-latest-small/movies.csv` exists.

4. **Build artifacts** (TF‑IDF + similarity matrix):
   ```bash
   # from project root
   python data_prep.py  # uses MOVIELENS_DIR=ml-latest-small by default
   ```

5. **(Optional) Set TMDB API key** to fetch posters (strongly recommended):
   - Create an account at TMDB and get an API key.
   - EITHER set it as an environment variable:
     ```bash
     export TMDB_API_KEY=YOUR_KEY
     ```
   - OR add it to **Streamlit secrets** (see deployment).

6. **Run the app**:
   ```bash
   streamlit run app.py
   ```

---

## 🚀 Deployment

### Option A — Streamlit Community Cloud
1. Push this folder to **GitHub**.
2. Create a new app at Streamlit Cloud, pointing to `app.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   TMDB_API_KEY = "YOUR_KEY"
   ```
4. Click **Deploy**. Done!

### Option B — Render
- Create a **Web Service**, use `pip install -r requirements.txt` as build command, and `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` as start command.
- Add `TMDB_API_KEY` in **Environment Variables**.

### Option C — Netlify
- Use **Netlify Functions** or a containerized approach; Render / Streamlit Cloud is simpler for Streamlit apps.

---

## 🧠 How It Works
- Uses MovieLens `movies.csv` (title, genres).
- Cleans titles (removes year in brackets) and extracts release year.
- Builds a **TF‑IDF** representation over `title + genres` and computes **cosine similarity**.
- Recommends the top‑K similar movies to the selected one.
- Fetches **posters** from TMDB by title (and year if available). Falls back to a placeholder if no key / no match.

> You can switch to **collaborative filtering** later using MovieLens `ratings.csv` and a matrix factorization model (e.g., SVD).

---

## ✅ Meets Set 2 Requirements
- ✅ Search & select a movie
- ✅ At least 5 recommendations
- ✅ Poster, Title, Genres per recommendation (via TMDB for posters)
- ✅ Content-based filtering implemented
- ✅ Deployable on Streamlit Cloud / Render
- ✅ GitHub‑ready with clear README and code

---

## 🧪 Quick Test Tips
- Try: `Toy Story (1995)`, `Jumanji (1995)`, `Pulp Fiction (1994)`
- Ensure `artifacts/` exists after running `data_prep.py`

---

## 📌 Notes
- Poster accuracy depends on TMDB search by title/year.
- If you're offline or skip TMDB, the app still runs and shows placeholder posters.

---

## 🛠️ Extend (Nice-to-have)
- Add **overview/keywords** (pull from TMDB in `data_prep.py`) to improve content features.
- Add **collaborative filtering** using `ratings.csv`.
- Add **evaluation** (MAP@K, NDCG) on held-out interactions.
- Add **multilingual** UI and better search.
