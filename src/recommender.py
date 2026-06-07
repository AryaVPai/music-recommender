import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load data once when the module is imported
df = pd.read_csv('../data/cleaned_dataset.csv')
song_matrix = df[['energy', 'valence', 'danceability', 'tempo',
                   'acousticness', 'instrumentalness', 
                   'liveness', 'speechiness']].values

FEATURE_COLS = ['energy', 'valence', 'danceability', 'tempo',
                'acousticness', 'instrumentalness', 'liveness', 'speechiness']

NON_ENGLISH_GENRES = [
    'brazil', 'cantopop', 'forro', 'french', 'german', 'indian',
    'iranian', 'j-dance', 'j-idol', 'j-pop', 'j-rock', 'k-pop',
    'latin', 'latino', 'malay', 'mandopop', 'mpb', 'pagode',
    'reggaeton', 'romance', 'salsa', 'samba', 'sertanejo',
    'spanish', 'swedish', 'tango', 'turkish'
]

MOOD_PROFILES = {
    "happy":     {"valence": 0.8, "energy": 0.7, "danceability": 0.7},
    "sad":       {"valence": 0.2, "energy": 0.3, "danceability": 0.3},
    "angry":     {"valence": 0.2, "energy": 0.9, "danceability": 0.5},
    "chill":     {"valence": 0.5, "energy": 0.2, "danceability": 0.4},
    "energetic": {"valence": 0.6, "energy": 0.9, "danceability": 0.8},
    "romantic":  {"valence": 0.6, "energy": 0.3, "danceability": 0.4},
    "dance":     {"valence": 0.7, "energy": 0.8, "danceability": 0.95},
    "focus":     {"valence": 0.4, "energy": 0.4, "instrumentalness": 0.8},
}


def recommend_by_song(song_name: str, n: int = 10):
    matches = df[df['track_name'].str.lower() == song_name.lower()]

    if matches.empty:
        return None

    song_idx = matches.loc[matches['popularity'].idxmax()].name
    song_vector = song_matrix[song_idx].reshape(1, -1)
    similarities = cosine_similarity(song_vector, song_matrix)[0]
    similar_indices = np.argsort(similarities)[::-1][1:n*3]

    results = df.iloc[similar_indices][['track_name', 'artists', 
                                        'track_genre', 'popularity']].copy()
    results['similarity_score'] = similarities[similar_indices].round(4)
    results = results.sort_values('popularity', ascending=False)
    results = results.drop_duplicates(subset=['track_name', 'artists'])
    results = results.sort_values('similarity_score', ascending=False).head(n)

    return results.to_dict(orient='records')


def recommend_by_mood(mood: str, genre: str = None, 
                      english_only: bool = False, n: int = 10):
    if mood.lower() not in MOOD_PROFILES:
        return None

    pref = {
        "energy": 0.5, "valence": 0.5, "danceability": 0.5,
        "tempo": 0.5, "acousticness": 0.5, "instrumentalness": 0.5,
        "liveness": 0.5, "speechiness": 0.5,
    }
    pref.update(MOOD_PROFILES[mood.lower()])
    user_vector = np.array([[pref[f] for f in FEATURE_COLS]])

    pool = df.copy()
    pool_matrix = song_matrix

    if genre:
        pool = pool[pool['track_genre'].str.lower() == genre.lower()]
        pool_matrix = song_matrix[pool.index]

    if english_only:
        pool = pool[~pool['track_genre'].isin(NON_ENGLISH_GENRES)]
        pool_matrix = song_matrix[pool.index]

    if pool.empty:
        return None

    similarities = cosine_similarity(user_vector, pool_matrix)[0]
    top_indices = np.argsort(similarities)[::-1][:n*3]

    results = pool.iloc[top_indices][['track_name', 'artists', 
                                      'track_genre', 'popularity']].copy()
    results['similarity_score'] = similarities[top_indices].round(4)
    results = results.sort_values('popularity', ascending=False)
    results = results.drop_duplicates(subset=['track_name', 'artists'])
    results = results.sort_values('similarity_score', ascending=False).head(n)

    return results.to_dict(orient='records')