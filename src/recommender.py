import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Tuple, Dict
import datetime
from pathlib import Path

class ProductRecommender:
    def __init__(self, data_path: str):
        """Initialize the recommender system with the dataset path."""
        self.data_path = data_path
        self.data = None
        self.similarity_matrix = None
        self.product_names = None
        self.user_ratings = {}  # Store new user ratings
        possible_paths = [
            Path(__file__).parent.parent / "ecommerce_dataset.csv",  # new cleaned dataset
            Path("ecommerce_dataset.csv"),  # current directory
            Path(__file__).parent / "ecommerce_dataset.csv",  # src directory
            Path(__file__).parent.parent / "ecommerce_dataset_updated.csv",  # fallback to other updated
            Path(__file__).parent.parent / "ecommerce dataset.csv",  # fallback to original
            Path("ecommerce dataset.csv"),
            Path(__file__).parent / "ecommerce dataset.csv"
        ]
        for path in possible_paths:
            if path.exists():
                self.data_path = path
                break
        self.load_and_prepare_data()

    def load_and_prepare_data(self):
        """Load and preprocess the product dataset."""
        # Check if the data file exists
        import os
        if not os.path.exists(self.data_path):
            print(f"Warning: Data file not found at {self.data_path}")
            self.data = pd.DataFrame()  # Create empty DataFrame
            return
            
        # Try to load with different encodings
        try:
            self.data = pd.read_csv(self.data_path, encoding='latin-1')
        except Exception as e1:
            try:
                self.data = pd.read_csv(self.data_path, encoding='cp1252')
            except Exception as e2:
                print(f"Error loading data: {e2}")
                self.data = pd.DataFrame()  # Create empty DataFrame
                return
        
        # Print original dataset size
        print(f"Original dataset size: {len(self.data)} products")
        
        # Keep track of original dataset size
        original_size = len(self.data)
        
        # Handle missing image URLs with placeholder images instead of filtering them out
        for index, row in self.data.iterrows():
            if pd.isna(row['Product Image URL']) or not isinstance(row['Product Image URL'], str) or not row['Product Image URL'].strip():
                category = row['Category']
                if pd.isna(category):
                    category = 'Product'
                category_str = str(category).replace(' ', '+')
                self.data.at[index, 'Product Image URL'] = f"https://via.placeholder.com/140x140?text={category_str}"
        
        print(f"Products with image URLs (including placeholders): {len(self.data)}")
        
        # Print counts by category
        print("Products by category:")
        print(self.data['Category'].value_counts())
        
        # Identify important categories for special handling
        important_categories = ['Luxury Jewelry', 'Make up']
        
        # Print only summary information about important categories
        for category in important_categories:
            category_products = self.data[self.data['Category'] == category]
            print(f"Found {len(category_products)} products in category '{category}'")
        
        # IMPORTANT: Use ALL products - no more limiting to 100
        # This ensures all categories have their products displayed
        print(f"Using all {len(self.data)} products from the dataset (no product limit)")
        balanced_data = self.data.copy()
        
        # Update the data with our balanced selection
        self.data = balanced_data.reset_index(drop=True)
        
        print(f"Final dataset size: {len(self.data)} products")
        print("Final category distribution:")
        print(self.data['Category'].value_counts())
        
        # Reset index after filtering
        self.data = self.data.reset_index(drop=True)
        
        # Print only count of selected products to avoid encoding issues
        print(f"\nFinal dataset has {len(self.data)} total products")
        
        # Calculate similarity matrix for this smaller dataset
        self._update_similarity_matrix()

    def _update_similarity_matrix(self):
        """Update the similarity matrix based on product features."""
        # Select features for similarity calculation
        numeric_features = ['Sales', 'Rating']
        categorical_features = ['Category']
        
        # Prepare feature matrix
        feature_matrix = []
        
        # Add normalized numeric features
        for feat in numeric_features:
            if feat in self.data.columns:
                values = self.data[feat].fillna(0)
                # Normalize to 0-1 range
                min_val = values.min()
                max_val = values.max()
                if max_val > min_val:
                    normalized = (values - min_val) / (max_val - min_val)
                    feature_matrix.append(normalized)
        
        # Add one-hot encoded categorical features
        for feat in categorical_features:
            if feat in self.data.columns:
                dummies = pd.get_dummies(self.data[feat], prefix=feat)
                feature_matrix.extend([dummies[col] for col in dummies.columns])
        
        # Convert to numpy array and calculate similarity
        if feature_matrix:
            features = np.vstack(feature_matrix).T
            self.similarity_matrix = cosine_similarity(features)
        else:
            # Fallback to simple similarity
            self.similarity_matrix = np.eye(len(self.data))

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

    def get_recommendations(self, product_name: str, n: int = 5) -> List[Dict]:
        """Get N product recommendations similar to the given product."""
        # Handle case where data is empty
        if self.data is None or self.data.empty:
            print("No data available for recommendations")
            return []
            
        try:
            # Find the index of the product
            product_col = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()][0]
            
            if product_name not in self.data[product_col].values:
                print(f"Product {product_name} not found in the dataset")
                return []
                
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
                    'category': product.get('Category', 'Unknown'),
                    'price': product.get('Sales', 0),
                    'similarity': score,
                    'image_url': product.get('Product Image URL', ''),
                    'rating': product.get('Rating', 0)
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
        if 'Category' not in self.data.columns:
            return []
        return sorted(list(self.data['Category'].dropna().unique()))
        
    def get_countries(self):
        """Get list of unique countries."""
        if 'Country' not in self.data.columns:
            return []
        return sorted(list(self.data['Country'].dropna().unique()))
    
    def get_product_category(self, product_name):
        """Get category for a given product name."""
        # Find the product name column
        name_columns = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()]
        if not name_columns:
            return "Unknown"
        product_col = name_columns[0]
        
        try:
            return self.data[self.data[product_col] == product_name]['Category'].iloc[0]
        except (KeyError, IndexError):
            return "Unknown"
            
    def get_product_country(self, product_name):
        """Get country for a given product name."""
        # Find the product name column
        name_columns = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()]
        if not name_columns:
            return "Unknown"
        product_col = name_columns[0]
        
        try:
            return self.data[self.data[product_col] == product_name]['Country'].iloc[0]
        except (KeyError, IndexError):
            return "Unknown"
    
    def get_product_details(self, product_name):
        """Get details for a specific product."""
        try:
            # Find product name column
            product_col = [col for col in self.data.columns if 'name' in col.lower() or 'product' in col.lower()][0]
            product = self.data[self.data[product_col] == product_name].iloc[0]
            
            return {
                'category': product.get('Category', 'Unknown'),
                'country': product.get('Country', 'Unknown'),
                'price': product.get('Sales', 0),  # Using Sales column for price
                'avg_rating': product.get('Rating', 0),
                'image_url': product.get('Product Image URL', '')
            }
        except (IndexError, KeyError) as e:
            print(f"Error getting product details: {str(e)}")
            return None
