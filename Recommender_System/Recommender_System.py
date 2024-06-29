#!/usr/bin/env python
# coding: utf-8

# In[166]:


import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
import matplotlib.pyplot as plt


from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# In[167]:


# get_ipython().run_line_magic('matplotlib', 'inline')


# In[168]:


df = pd.read_json("UpdatedDatasetSOI .json")


# In[169]:


df.head()


# In[170]:


df.info()


# In[171]:


df['book_id'] = range(1, len(df) + 1)
df['book_id'] = df['book_id'].apply(lambda x: str(x).zfill(6))
df['book_id'] = df['book_id'].astype(int)


# In[172]:


df.head()


# In[173]:


df.info()


# In[174]:


df_csv = pd.read_csv("datasetnew2.csv")


# In[175]:


df_csv.head()


# In[176]:


df_csv.info()


# In[177]:


are_equal = df_csv.equals(df)
are_equal


# In[178]:


df.columns


# In[179]:


# Index(['title', 'author', 'genre', 'book_id'], dtype='object')
df['book_id']


# # Content-Based Filtering

# recommends items similar to those a user has liked in the past

# In[182]:


# Combine relevant features into a single string
df['combined_features'] = df['title'] + ' ' + df['description'] + ' ' + df['author'] + ' ' + df['genre'] + ' ' + df['department']

# Create a TF-IDF Vectorizer
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['combined_features'])

# Compute the cosine similarity matrix
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Function to get book recommendations based on content similarity
def get_content_based_recommendations(title, cosine_sim=cosine_sim):
    idx = df[df['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:6]  # Get top 10 recommendations
    book_indices = [i[0] for i in sim_scores]
    return df.iloc[book_indices][['title', 'author', 'genre']]
    

# Example usage
# print(get_content_based_recommendations('Introduction to Algorithms').tolist())
get_content_based_recommendations('Introduction to Algorithms')


# # Collaborative Filtering

# recommends items based on the preferences of similar users

# In[183]:


# Sample user interactions data
data = {
    'user_id': [1, 1, 1, 2, 2, 3, 3, 3, 3],
    'book_id': [101, 102, 103, 101, 104, 102, 103, 104, 105],
    'rating': [5, 3, 4, 4, 2, 5, 4, 3, 1],
    'borrow_count': [10, 5, 7, 2, 3, 6, 4, 1, 2]
}

user_interactions = pd.DataFrame(data)


# df = df[['book_id', 'title', 'author', 'genre']]

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
predicted_ratings_df = pd.DataFrame(predicted_ratings, columns=user_interactions['book_id'].unique())

# Function to get collaborative filtering recommendations
def get_collaborative_filtering_recommendations(user_id, num_recommendations=10):
    user_idx = user_id - 1  # Adjust user_id to zero-based index
    user_ratings = predicted_ratings_df.iloc[user_idx]
    sorted_indices = np.argsort(user_ratings)[::-1]
    recommended_indices = sorted_indices[:num_recommendations]
    return df[df['book_id'].isin(predicted_ratings_df.columns[recommended_indices])][['title', 'author', 'genre']]

# Example usage
# print(get_collaborative_filtering_recommendations(1))
get_collaborative_filtering_recommendations(3)


# # Hybrid Approach

#  both content-based and collaborative filtering methods to leverage the strengths of both alogrithm

# In[184]:


def get_hybrid_recommendations(title, user_id, cosine_sim=cosine_sim, num_recommendations=10):
    content_based_recs = get_content_based_recommendations(title, cosine_sim)
    collaborative_recs = get_collaborative_filtering_recommendations(user_id, num_recommendations)
    
    # Combine both recommendations
    combined_recs = pd.concat([content_based_recs, collaborative_recs]).drop_duplicates().head(num_recommendations)
    return combined_recs

# Example usage
# print(get_hybrid_recommendations('Introduction to Algorithms', 1, num_recommendations=5))

get_hybrid_recommendations('Introduction to Algorithms', 2, num_recommendations=10)


# In[ ]:





# In[ ]:




