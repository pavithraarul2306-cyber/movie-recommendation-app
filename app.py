import pickle
import streamlit as st
import requests
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if not poster_path:
            return None
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_movies() -> pd.DataFrame:
    return pickle.load(open('model/movie_list.pkl','rb'))


@st.cache_data(show_spinner=True)
def compute_similarity_from_movies(movies_df: pd.DataFrame) -> np.ndarray:
    # Ensure a 'tags' column exists by deriving from available columns if needed
    if 'tags' not in movies_df.columns:
        def parse_name_list(text, limit=None, job_filter=None):
            try:
                items = ast.literal_eval(text) if isinstance(text, str) else (text or [])
            except Exception:
                items = []
            names = []
            for item in items:
                if not isinstance(item, dict):
                    continue
                if job_filter is not None and item.get('job') != job_filter:
                    continue
                name = item.get('name')
                if name:
                    names.append(name.replace(" ", ""))
            if limit is not None:
                names = names[:limit]
            return names

        titles_tokens = movies_df.get('title', pd.Series([], dtype=str)).fillna('').apply(lambda t: str(t).split())
        cast_tokens = movies_df.get('cast', pd.Series([], dtype=object)).apply(lambda x: parse_name_list(x, limit=3))
        # Prefer directors in crew; if not available, take first few crew names
        director_tokens = movies_df.get('crew', pd.Series([], dtype=object)).apply(lambda x: parse_name_list(x, job_filter='Director'))
        crew_fallback = movies_df.get('crew', pd.Series([], dtype=object)).apply(lambda x: parse_name_list(x, limit=2))
        combined_crew = [d if d else f for d, f in zip(director_tokens, crew_fallback)]

        movies_df = movies_df.copy()
        movies_df['tags'] = [
            " ".join(tokens)
            for tokens in [
                list(titles_tokens.iloc[i]) + list(cast_tokens.iloc[i]) + list(combined_crew[i])
                for i in range(len(movies_df))
            ]
        ]
    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(movies_df['tags']).toarray()
    return cosine_similarity(vectors)

def recommend(movie_title: str, movies_df: pd.DataFrame, sim_matrix: np.ndarray):
    index = movies_df[movies_df['title'] == movie_title].index[0]
    distances = list(enumerate(sim_matrix[index]))
    distances.sort(key=lambda x: x[1], reverse=True)
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies_df.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies_df.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters


st.header('Movie Recommender System')
movies = load_movies()
try:
    similarity = compute_similarity_from_movies(movies)
except Exception as e:
    st.error(f"Failed to compute similarity: {e}")
    similarity = None

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    if similarity is None:
        st.warning('Recommendations unavailable due to similarity computation error.')
    else:
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie, movies, similarity)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(recommended_movie_names[0])
            if recommended_movie_posters[0]:
                st.image(recommended_movie_posters[0])
        with col2:
            st.text(recommended_movie_names[1])
            if recommended_movie_posters[1]:
                st.image(recommended_movie_posters[1])
        with col3:
            st.text(recommended_movie_names[2])
            if recommended_movie_posters[2]:
                st.image(recommended_movie_posters[2])
        with col4:
            st.text(recommended_movie_names[3])
            if recommended_movie_posters[3]:
                st.image(recommended_movie_posters[3])
        with col5:
            st.text(recommended_movie_names[4])
            if recommended_movie_posters[4]:
                st.image(recommended_movie_posters[4])





