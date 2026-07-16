import streamlit as st
import pandas as pd
import joblib
import requests

# ----------------------------
# Page Configuration
# ----------------------------

st.set_page_config(
    page_title="Netflix Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ----------------------------
# TMDB API KEY
# ----------------------------

API_KEY = st.secrets["TMDB_API_KEY"]
# For local testing only:
# API_KEY = "YOUR_API_KEY"

# ----------------------------
# Custom CSS
# ----------------------------

st.markdown("""
<style>

.stApp{
    background-color:#141414;
}

h1{
    color:#E50914;
}

.movie-card{
    background-color:#222222;
    border-radius:15px;
    padding:15px;
    color:white;
    text-align:center;
    box-shadow:0px 0px 10px rgba(255,255,255,0.1);
    transition:0.3s;
}

.movie-card:hover{
    transform:scale(1.03);
}

.stButton>button{
    width:100%;
    background-color:#E50914;
    color:white;
    font-size:18px;
    border-radius:10px;
    border:none;
}

.stButton>button:hover{
    background-color:#ff2d2d;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------
# Load Model
# ----------------------------

movies = joblib.load("movie_list.joblib")
similarity = joblib.load("similarity.joblib")

# ----------------------------
# Recommendation Function
# ----------------------------

def recommend(movie):

    index = movies[movies['title'] == movie].index[0]

    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x:x[1]
    )[1:6]

    recommendations = []

    for i in movie_list:
        recommendations.append(movies.iloc[i[0]].title)

    return recommendations

# ----------------------------
# TMDB Functions
# ----------------------------

def fetch_movie(movie_name):

    search_url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": API_KEY,
        "query": movie_name
    }

    response = requests.get(search_url, params=params).json()

    if response["results"]:

        movie = response["results"][0]

        poster = ""

        if movie["poster_path"]:
            poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

        return {
            "title": movie["title"],
            "poster": poster,
            "rating": movie["vote_average"],
            "overview": movie["overview"],
            "release": movie["release_date"]
        }

    return None

# ----------------------------
# Title
# ----------------------------

st.title("🎬Movie Recommendation System")

st.write("Find movies similar to your favourite films using Machine Learning.")

st.divider()

# ----------------------------
# Select Movie
# ----------------------------

selected_movie = st.selectbox(
    "Choose a Movie",
    movies["title"].values
)

# ----------------------------
# Recommend Button
# ----------------------------

if st.button("Recommend"):

    recommended_movies = recommend(selected_movie)

    st.subheader("Recommended Movies")

    cols = st.columns(5)

    for col, movie in zip(cols, recommended_movies):

        details = fetch_movie(movie)

        if details:

            with col:

                st.image(details["poster"])

                st.markdown(f"### {details['title']}")

                st.write(f"⭐ {details['rating']:.1f}/10")

                st.write(f"📅 {details['release']}")

                st.caption(details["overview"][:120] + "...")
