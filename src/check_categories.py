import pandas as pd
import os
from pathlib import Path

def check_dataset():
    """Check if the dataset contains products in the specified categories"""
    print("Running category check diagnostic...")
    
    # Try multiple possible locations for the CSV file
    possible_paths = [
        Path(__file__).parent.parent / "ecommerce dataset.csv",  # project root
        Path("ecommerce dataset.csv"),  # current directory
        Path(__file__).parent / "ecommerce dataset.csv",  # src directory
        Path.cwd() / "ecommerce dataset.csv"  # current working directory
    ]
    
    # Find the first path that exists
    data_path = None
    for path in possible_paths:
        if path.exists():
            data_path = path
            break
    
    if data_path is None:
        print(f"Could not find CSV file. Searched in: {[str(p) for p in possible_paths]}")
        return
    
    print(f"Using data from: {data_path}")
    
    # Try to load with different encodings
    try:
        df = pd.read_csv(data_path, encoding='latin-1')
    except Exception as e1:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
        except Exception as e2:
            print(f"Error loading data: {e2}")
            return
    
    # Print basic info
    print(f"Original dataset size: {len(df)} products")
    print("\nCategory counts:")
    print(df['Category'].value_counts())
    
    # Check specific categories
    problem_categories = ['Luxury Jewelry', 'Make up']
    
    for category in problem_categories:
        category_df = df[df['Category'] == category]
        print(f"\n{category} category:")
        print(f"- Total products: {len(category_df)}")
        
        if len(category_df) > 0:
            print(f"Sample {category} products:")
            for i, row in category_df.head(3).iterrows():
                product_name = row['Product'] if 'Product' in row else 'Unknown'
                image_url = row['Product Image URL'] if 'Product Image URL' in row else 'No URL'
                print(f"  - {product_name} | URL: {image_url}")
                
            # Check for missing values
            missing_values = category_df.isnull().sum()
            print(f"\nMissing values in {category} category:")
            for col, count in missing_values.items():
                if count > 0:
                    print(f"  - {col}: {count} missing values")
    
    print("\nCheck complete!")

if __name__ == "__main__":
    check_dataset()
