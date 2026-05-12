import streamlit as st
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load data
ratings = pd.read_csv(
    r"C:\Users\danam\OneDrive\Desktop\ML_journey\project_02_movie_recommender\datasets\u.data",
    sep='\t',
    names=['user_id', 'movie_id', 'rating', 'timestamp']
)

movies = pd.read_csv(
    r"C:\Users\danam\OneDrive\Desktop\ML_journey\project_02_movie_recommender\datasets\u.item",
    sep='|',
    encoding='latin-1',
    usecols=[0, 1],
    names=['movie_id', 'title'],
    header=None
)

# Merge ratings and movies
df = ratings.merge(movies, on='movie_id')

# Create user-movie matrix
user_movie_matrix = df.pivot_table(
    index='user_id',
    columns='title',
    values='rating'
).fillna(0)

# Calculate user similarity
user_similarity = cosine_similarity(user_movie_matrix)
user_similarity_df = pd.DataFrame(
    user_similarity,
    index=user_movie_matrix.index,
    columns=user_movie_matrix.index
)

# Recommendation function
def get_recommendations(user_id, n=5):
    
    # Get similar users
    similar_users = user_similarity_df[user_id].sort_values(ascending=False)
    
    # Remove the user themselves
    similar_users = similar_users.drop(user_id)
    
    # Take top 10 similar users
    similar_users = similar_users.head(10)
    
    # Get movies similar users watched
    similar_users_movies = user_movie_matrix.loc[similar_users.index]
    
    # Get movies user hasn't watched
    user_watched = user_movie_matrix.loc[user_id]
    user_unwatched = user_watched[user_watched == 0.0].index
    
    # Calculate average rating for unwatched movies
    movie_scores = similar_users_movies[user_unwatched].mean()
    
    # Sort and return top N
    recommendations = movie_scores.sort_values(ascending=False).head(n)
    
    return recommendations


# ── STREAMLIT APP ──────────────────────

# App title
st.title("🎬 Movie Recommendation Engine")
st.subheader("Find movies you'll love!")

# Sidebar
st.sidebar.header("Settings")

# User ID input
user_id = st.sidebar.number_input(
    "Enter User ID (1-943):",
    min_value=1,
    max_value=943,
    value=1
)

# Number of recommendations
n_recommendations = st.sidebar.slider(
    "Number of Recommendations:",
    min_value=1,
    max_value=20,
    value=5
)

# Button
if st.sidebar.button("Get Recommendations!"):
    st.subheader(f"Top {n_recommendations} Movies for User {user_id}:")
    recommendations = get_recommendations(user_id, n_recommendations)
    
    for i, (movie, score) in enumerate(recommendations.items()):
        st.write(f"{i+1}. {movie} — Score: {score:.2f}")
