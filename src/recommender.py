import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
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
        
        # Print the columns and first few rows for debugging
        print("Columns in dataset:", list(self.data.columns))
        print("\nFirst few rows:")
        print(self.data.head())
        
        # Ensure required columns exist
        required_columns = ['price', 'category', 'product_name']
        if not all(col.lower() in [c.lower() for c in self.data.columns] for col in required_columns):
            # If columns don't match, try to map similar column names
            column_mapping = {}
            for col in self.data.columns:
                col_lower = col.lower()
                if 'price' in col_lower:
                    column_mapping[col] = 'price'
                elif 'category' in col_lower:
                    column_mapping[col] = 'category'
                elif 'name' in col_lower or 'product' in col_lower:
                    column_mapping[col] = 'product_name'
            
            # Rename columns if mapping exists
            if column_mapping:
                self.data = self.data.rename(columns=column_mapping)
        
        # Ensure numeric columns
        if 'price' in self.data.columns:
            self.data['price'] = pd.to_numeric(self.data['price'], errors='coerce')
        
        self._update_similarity_matrix()

    def _update_similarity_matrix(self):
        """Update the similarity matrix based on product features."""
        # Select available numeric features
        numeric_features = self.data.select_dtypes(include=['int64', 'float64']).columns
        feature_cols = [col for col in numeric_features if col != 'id']  # exclude ID column if present
        
        if len(feature_cols) == 0:
            # If no numeric features found, create a simple feature
            self.data['feature'] = 1
            feature_cols = ['feature']
        
        # Create feature matrix
        feature_matrix = self.data[feature_cols].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(feature_matrix)
        
        # Calculate similarity matrix
        self.similarity_matrix = cosine_similarity(scaled_features)

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

    def get_recommendations(self, product_name, n=5):
        """Get product recommendations based on similarity."""
        try:
            # Find the index of the product
            product_col = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()][0]
            idx = self.data[self.data[product_col] == product_name].index[0]
            
            # Get similarity scores
            sim_scores = list(enumerate(self.similarity_matrix[idx]))
            
            # Sort products by similarity
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            
            # Get top N most similar products (excluding itself)
            sim_scores = sim_scores[1:n+1]
            
            # Get product indices
            product_indices = [i[0] for i in sim_scores]
            
            # Return recommendations with similarity scores
            recommendations = []
            for idx, score in zip(product_indices, [s[1] for s in sim_scores]):
                product = self.data.iloc[idx]
                recommendations.append({
                    'name': product[product_col],
                    'category': product.get('category', 'Unknown'),
                    'price': product.get('price', 0),
                    'similarity': score
                })
            
            return recommendations
        
        except (IndexError, KeyError) as e:
            print(f"Error getting recommendations: {str(e)}")
            return []

    def get_all_product_names(self):
        """Get list of all product names."""
        # Find the product name column
        name_columns = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()]
        if not name_columns:
            print("No product name column found in:", list(self.data.columns))
            return []
        product_col = name_columns[0]
        return list(self.data[product_col].dropna())
    
    def get_product_id_by_name(self, product_name: str) -> str:
        """Get product ID from product name."""
        product_col = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()][0]
        product_id = self.data[self.data[product_col] == product_name].index.values
        return product_id[0] if len(product_id) > 0 else None

    def get_categories(self):
        """Get list of unique categories."""
        if 'category' not in self.data.columns:
            return []
        return sorted(list(set(self.data['category'].dropna())))
    
    def get_product_category(self, product_name):
        """Get category for a given product name."""
        # Find the product name column
        name_columns = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()]
        if not name_columns:
            return "Unknown"
        product_col = name_columns[0]
        
        try:
            return self.data[self.data[product_col] == product_name]['category'].iloc[0]
        except (KeyError, IndexError):
            return "Unknown"
    
    def get_product_details(self, product_name):
        """Get details for a specific product."""
        # Find the product name column
        name_columns = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()]
        if not name_columns:
            return None
        product_col = name_columns[0]
        
        try:
            product = self.data[self.data[product_col] == product_name].iloc[0]
            return {
                'category': product.get('category', 'Unknown'),
                'price': float(product.get('price', 0)),
                'avg_rating': float(product.get('rating', 0)),
                'total_ratings': int(product.get('total_ratings', 0))
            }
        except (IndexError, KeyError):
            return None
