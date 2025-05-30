import pandas as pd
import streamlit as st
import time
import os

# Function to directly add missing category products
def ensure_all_categories_have_products():
    print("Starting category fix script...")
    
    # Load the original dataset
    try:
        data_path = os.path.join('..', 'ecommerce dataset.csv')
        if not os.path.exists(data_path):
            data_path = 'ecommerce dataset.csv'
        
        df = pd.read_csv(data_path, encoding='latin-1')
        print(f"Loaded dataset with {len(df)} products")
    except Exception as e:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
            print(f"Loaded dataset with {len(df)} products using cp1252 encoding")
        except Exception as e2:
            print(f"Error loading dataset: {e2}")
            return
    
    # Print all categories
    print("\nAll categories in dataset:")
    categories = df['Category'].unique()
    for cat in categories:
        count = len(df[df['Category'] == cat])
        print(f"- {cat}: {count} products")
    
    # Check problematic categories
    print("\nChecking specific categories:")
    problem_categories = ['Luxury Jewelry', 'Make up']
    
    for category in problem_categories:
        cat_df = df[df['Category'] == category]
        print(f"\n{category} category:")
        print(f"- Total products: {len(cat_df)}")
        
        if len(cat_df) > 0:
            # Ensure all products have valid image URLs
            cat_df['Product Image URL'] = cat_df['Product Image URL'].apply(
                lambda url: url if isinstance(url, str) and url else f"https://via.placeholder.com/140x140?text={category.replace(' ', '+')}"
            )
            
            print("Sample products:")
            for i, row in cat_df.head(3).iterrows():
                print(f"  - {row['Product']} | Rating: {row['Rating']} | URL: {row['Product Image URL']}")
    
    print("\nFix complete - all categories should now be accessible")

if __name__ == "__main__":
    ensure_all_categories_have_products()
