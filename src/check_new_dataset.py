"""
Script to check if the new cleaned dataset contains the necessary categories.
"""
import pandas as pd
from pathlib import Path

def check_new_dataset():
    """Check if the new dataset contains all necessary categories"""
    print("=== CHECKING NEW CLEANED DATASET ===")
    
    dataset_path = Path("C:/Users/samuel/Desktop/smart information/smart-info-project/ecommerce_dataset.csv")
    
    if not dataset_path.exists():
        print(f"Dataset not found at {dataset_path}")
        return
    
    print(f"Found dataset at {dataset_path}")
    
    # Try to load with different encodings
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            print(f"Trying to load with {encoding} encoding...")
            df = pd.read_csv(dataset_path, encoding=encoding)
            print(f"Successfully loaded with {encoding} encoding")
            
            # Basic dataset info
            print(f"\nDataset contains {len(df)} rows and {len(df.columns)} columns")
            print("Columns:", df.columns.tolist())
            
            # Check for category column
            if 'Category' not in df.columns:
                print("ERROR: No 'Category' column found in dataset")
                similar_cols = [col for col in df.columns if 'cat' in col.lower()]
                if similar_cols:
                    print(f"Found similar columns: {similar_cols}")
                continue
            
            # Check category values
            print("\nCategory distribution:")
            category_counts = df['Category'].value_counts()
            print(category_counts)
            
            # Check for problematic categories
            problem_categories = ['Luxury Jewelry', 'Make up']
            for category in problem_categories:
                print(f"\n=== Checking for '{category}' ===")
                cat_df = df[df['Category'] == category]
                print(f"Found {len(cat_df)} products with category '{category}'")
                
                if len(cat_df) > 0:
                    print("\nSample products:")
                    for i, row in cat_df.head(3).iterrows():
                        print(f"Row {i}:")
                        for col in ['Product', 'Rating', 'Sales', 'Product Image URL']:
                            if col in row:
                                print(f"  {col}: {row[col]}")
            
            # Successfully loaded, no need to try other encodings
            break
        except Exception as e:
            print(f"Failed with {encoding} encoding: {e}")
    else:
        print("ERROR: Could not load dataset with any encoding")
    
    print("\n=== DATASET CHECK COMPLETE ===")

if __name__ == "__main__":
    check_new_dataset()
