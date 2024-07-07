import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
import numpy as np

# Load datasets
books = pd.read_json('./Recommender_System/UpdatedDatasetSOI .json')
books['book_id'] = range(1, len(books) + 1)
books['book_id'] = books['book_id'].apply(lambda x: str(x).zfill(6))
books['book_id'] = books['book_id'].astype(int)

user_interactions = pd.read_json('./Recommender_System/user_ratings.json')

# Precompute the cosine similarity matrix for content-based filtering
books['combined_features'] = books['title'] + ' ' + books['description'] + ' ' + books['author'] + ' ' + books['genre'] + ' ' + books['department']
tfibooks = TfidfVectorizer(stop_words='english')
tfibooks_matrix = tfibooks.fit_transform(books['combined_features'])
cosine_sim = cosine_similarity(tfibooks_matrix, tfibooks_matrix)

def get_content_based_recommendations(title, cosine_sim=cosine_sim):
    idx = books[books['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:3]
    book_indices = [i[0] for i in sim_scores]
    return books.iloc[book_indices][['title', 'author', 'genre']]

# Create a weighted interaction score
user_interactions['interaction_score'] = user_interactions['rating'] + user_interactions['borrow_count']
# Create a user-item matrix
user_item_matrix = user_interactions.pivot(index='user_id', columns='book_id', values='interaction_score').fillna(0)
# Convert the user-item matrix to a numpy array of floats
user_item_matrix = user_item_matrix.values.astype(float)
# Determine an appropriate value for k
num_users, num_items = user_item_matrix.shape
k = min(num_users, num_items) - 1  # k must be less than the smallest dimension
# Perform matrix factorization using SVD
U, sigma, Vt = svds(user_item_matrix, k=k)
sigma = np.diag(sigma)
# Compute predicted ratings
predicted_ratings = np.dot(np.dot(U, sigma), Vt)
# Convert predicted ratings back to a DataFrame
predicted_ratings_books = pd.DataFrame(predicted_ratings, columns=user_interactions['book_id'].unique())

def get_collaborative_filtering_recommendations(user_id, num_recommendations=3):
    user_idx = user_id - 1  # Adjust user_id to zero-based index
    user_ratings = predicted_ratings_books.iloc[user_idx]
    sorted_indices = np.argsort(user_ratings)[::-1]
    recommended_indices = sorted_indices[:num_recommendations]
    return books[books['book_id'].isin(predicted_ratings_books.columns[recommended_indices])][['title', 'author', 'genre']]

def get_hybrid_recommendations(title, user_id, cosine_sim, num_recommendations=3):
    content_based_recs = get_content_based_recommendations(title, cosine_sim)
    collaborative_recs = get_collaborative_filtering_recommendations(user_id, num_recommendations)
    combined_recs = pd.concat([content_based_recs, collaborative_recs]).drop_duplicates().head(num_recommendations)
    return combined_recs

def most_issued_books(dataset, branch_year):
    """
    This function returns the two most issued books for a given branch and year.
    
    Parameters:
    - dataset: DataFrame containing book issue data with columns 'BookID', 'BranchYear', and 'IssuedCount'
    - branch_year: String representing the branch and year, e.g., 'EE22BT'
    
    Returns:
    - List of the two most issued books (book IDs)
    """
    
    # Filter the dataset for the given branch and year
    filtered_data = dataset[dataset['BranchYear'].str.startswith(branch_year)]
    
    # Sort the filtered data by IssuedCount in descending order
    sorted_data = filtered_data.sort_values(by='IssuedCount', ascending=False)
    
    # Get the top two most issued books
    top_books = sorted_data.head(2)['BookID'].tolist()
    
    return top_books


