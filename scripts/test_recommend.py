import pickle
import ast
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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


def main():
    movies = pickle.load(open('model/movie_list.pkl','rb'))
    movies = movies.copy()

    titles_tokens = movies.get('title', pd.Series([], dtype=str)).fillna('').apply(lambda t: str(t).split())
    cast_tokens = movies.get('cast', pd.Series([], dtype=object)).apply(lambda x: parse_name_list(x, limit=3))
    director_tokens = movies.get('crew', pd.Series([], dtype=object)).apply(lambda x: parse_name_list(x, job_filter='Director'))
    crew_fallback = movies.get('crew', pd.Series([], dtype=object)).apply(lambda x: parse_name_list(x, limit=2))
    combined_crew = [d if d else f for d, f in zip(director_tokens, crew_fallback)]

    movies['tags'] = [
        " ".join(list(titles_tokens.iloc[i]) + list(cast_tokens.iloc[i]) + list(combined_crew[i]))
        for i in range(len(movies))
    ]

    cv = CountVectorizer(max_features=5000, stop_words='english')
    vectors = cv.fit_transform(movies['tags']).toarray()
    sim = cosine_similarity(vectors)

    title = movies['title'].iloc[0]
    idx = movies[movies['title'] == title].index[0]
    distances = list(enumerate(sim[idx]))
    distances.sort(key=lambda x: x[1], reverse=True)
    rec = [movies.iloc[i[0]].title for i in distances[1:6]]

    print("Input:", title)
    print("Recommendations:")
    for r in rec:
        print(r)


if __name__ == '__main__':
    main()


