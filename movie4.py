import streamlit as st
import pandas as pd
import sqlite3

# Function to establish database connection
def get_connection():
    conn = sqlite3.connect('tutorial.db')
    return conn

# Function to get similar movies based on scores
def get_similar_movies(movie_name, rating):
    similar_ratings = corrMatrix[movie_name] * (rating - 2.5)
    similar_ratings = similar_ratings.sort_values(ascending=False)
    return similar_ratings

# Reading all parquet data files
# Replace with your actual file paths
##movie_df = pd.read_parquet(path="movies.parquet", engine='auto')
corrMatrix = pd.read_parquet(path="corrmatrix.parquet", engine="auto")
merged = pd.read_parquet(path="movie_rating.parquet", engine="auto")

# Set page title and favicon
st.set_page_config(page_title="Movie Magic", page_icon="🎬")

# Title of the app
st.title("🍿 Welcome to Movie Magic! 🎥")

# Main content container
col1, col2 = st.columns([1, 3])

# Sidebar for user options
with col1:
    st.sidebar.title("User Options")
    userid = st.sidebar.number_input(label="Enter Your User ID", step=1)
    userid = int(userid)

    # Check if the user exists
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM movie_ratings WHERE userid = ?", (userid,))
        existing_user = c.fetchone()
        if existing_user:
            st.sidebar.success("Welcome back!")
        else:
            st.sidebar.info("New user? No worries, let's get started!")

# Main content area
with col2:
    # Select function dropdown
    selected_function = st.selectbox("What would you like to do today?", options=["Get Movie Recommendations", "Update Your Ratings"])

    # Get movie recommendations
    if selected_function == "Get Movie Recommendations":
        st.header("🌟 Rate a Movie:")
        st.write("Let's find the perfect movie for you! Rate a movie you've watched recently and get personalized recommendations.")

        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT DISTINCT title FROM movie_ratings")
            movie_titles = [row[0] for row in c.fetchall()]

        selected_movie = st.selectbox("Select a Movie", movie_titles)
        rating = st.slider("How would you rate this movie? (1-5)", 1, 5)

        if st.button("Submit Rating"):
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("INSERT INTO movie_ratings (userid, title, rating) VALUES (?, ?, ?)", (userid, selected_movie, rating))
                conn.commit()
                temp_df = get_similar_movies(selected_movie, rating)
                st.write(temp_df.head())
                st.success(f"Your rating for '{selected_movie}' has been submitted. 🎉")

    # Update movie ratings
    elif selected_function == "Update Your Ratings":
        st.header("🔄 Update Your Ratings:")
        st.write("Have your tastes changed? Update your ratings for movies you've previously watched.")

        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT DISTINCT title FROM movie_ratings")
            movie_titles = [row[0] for row in c.fetchall()]

        selected_movie = st.selectbox("Select a Movie to Update", movie_titles)
        rating = st.slider("Update your rating for this movie (1-5)", 1, 5)

        if st.button("Update Rating"):
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM movie_ratings WHERE userid = ? AND title = ?", (userid, selected_movie))
                existing_rating = c.fetchone()
                if existing_rating:
                    # Updating rating
                    c.execute("UPDATE movie_ratings SET rating = ? WHERE userid = ? AND title = ?", (rating, userid, selected_movie))
                    conn.commit()
                    st.success(f"Your rating for '{selected_movie}' has been updated. 🔄")
                else:
                    # Inserting the new rating
                    c.execute("INSERT INTO movie_ratings (userid, title, rating) VALUES (?, ?, ?)", (userid, selected_movie, rating))
                    conn.commit()
                    st.success(f"Your rating for '{selected_movie}' has been submitted. 🎬")
