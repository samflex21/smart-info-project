import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict
import datetime

class ProductRecommender:
    def __init__(self, data_path: str):
        """Initialize the recommender system with the dataset path."""
        self.data_path = data_path
        self.data = None
        self.similarity_matrix = None
        self.product_names = None
        self.user_ratings = {}  # Store new user ratings
        self.load_and_prepare_data()

    def load_and_prepare_data(self):
        """Load and preprocess the product dataset."""
        try:
            self.data = pd.read_csv(self.data_path, encoding='latin-1')
        except:
            self.data = pd.read_csv(self.data_path, encoding='cp1252')
        self._update_similarity_matrix()

    def _update_similarity_matrix(self):
        """Update similarity matrix with current data and user ratings."""
        # Convert user_ratings to DataFrame
        if self.user_ratings:
            new_ratings = pd.DataFrame(self.user_ratings).T.reset_index()
            new_ratings.columns = ['User ID', 'Product ID', 'Rating', 'Timestamp']
            # Combine with existing data
            combined_data = pd.concat([
                self.data[['User ID', 'Product ID', 'Rating']],
                new_ratings[['User ID', 'Product ID', 'Rating']]
            ])
        else:
            combined_data = self.data[['User ID', 'Product ID', 'Rating']]

        # Create user-item matrix
        user_item_matrix = pd.pivot_table(
            combined_data,
            values='Rating',
            index='User ID',
            columns='Product ID',
            fill_value=0
        )
        
        # Calculate item-item similarity matrix
        self.similarity_matrix = cosine_similarity(user_item_matrix.T)
        
        # Create a mapping of product IDs to their details
        self.product_names = self.data[['Product ID', 'Product Name', 'Category']].drop_duplicates()
        self.product_names.set_index('Product ID', inplace=True)
        
        # Convert similarity matrix to DataFrame
        self.similarity_matrix = pd.DataFrame(
            self.similarity_matrix,
            index=user_item_matrix.columns,
            columns=user_item_matrix.columns
        )

    def add_rating(self, user_id: str, product_id: str, rating: float):
        """Add a new user rating."""
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
            
        key = f"{user_id}_{product_id}"
        self.user_ratings[key] = {
            'User ID': user_id,
            'Product ID': product_id,
            'Rating': rating,
            'Timestamp': datetime.datetime.now().isoformat()
        }
        # Update similarity matrix with new rating
        self._update_similarity_matrix()

    def get_user_ratings(self, user_id: str) -> List[Tuple[str, float]]:
        """Get all ratings for a specific user."""
        user_ratings = []
        for key, data in self.user_ratings.items():
            if data['User ID'] == user_id:
                product_name = self.product_names.loc[data['Product ID'], 'Product Name']
                user_ratings.append((product_name, data['Rating']))
        return user_ratings

    def get_similar_products(self, product_id: str, n: int = 5) -> List[Tuple[str, float]]:
        """Get n most similar products for a given product ID."""
        if product_id not in self.similarity_matrix.index:
            return []
        
        # Get similarity scores for the product
        sim_scores = self.similarity_matrix[product_id]
        
        # Sort products by similarity (excluding the product itself)
        similar_products = sim_scores.sort_values(ascending=False)[1:n+1]
        
        # Get product names and similarity scores
        recommendations = []
        for pid, score in similar_products.items():
            product_name = self.product_names.loc[pid, 'Product Name']
            recommendations.append((product_name, score))
        
        return recommendations

    def get_all_product_names(self) -> List[str]:
        """Return a list of all product names."""
        return self.product_names['Product Name'].tolist()

    def get_product_id_by_name(self, product_name: str) -> str:
        """Get product ID from product name."""
        product_id = self.product_names[
            self.product_names['Product Name'] == product_name
        ].index.values
        return product_id[0] if len(product_id) > 0 else None

    def get_categories(self) -> List[str]:
        """Get list of unique product categories."""
        return sorted(self.product_names['Category'].unique().tolist())

    def get_product_category(self, product_name: str) -> str:
        """Get category for a given product name."""
        return self.product_names[
            self.product_names['Product Name'] == product_name
        ]['Category'].iloc[0]

    def get_product_details(self, product_name: str) -> Dict:
        """Get detailed information about a product."""
        # Get product ratings
        product_id = self.get_product_id_by_name(product_name)
        product_ratings = self.data[self.data['Product ID'] == product_id]['Rating']
        
        # Calculate statistics
        avg_rating = product_ratings.mean() if not product_ratings.empty else 0
        total_ratings = len(product_ratings)
        
        return {
            'category': self.get_product_category(product_name),
            'avg_rating': avg_rating,
            'total_ratings': total_ratings
        }
