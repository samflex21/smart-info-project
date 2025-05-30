import pandas as pd
import os
from pathlib import Path

def debug_category_display():
    """Comprehensive debugging of category filters"""
    print("=== CATEGORY DISPLAY DEBUGGING ===")
    
    # Check both the original and updated datasets
    file_paths = [
        "ecommerce dataset.csv",
        "ecommerce_dataset_updated.csv"
    ]
    
    for file_path in file_paths:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
            
        print(f"\nAnalyzing file: {file_path}")
        
        # Try different encodings
        for encoding in ['latin-1', 'cp1252', 'utf-8']:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"Successfully loaded with {encoding} encoding")
                break
            except Exception as e:
                print(f"Failed to load with {encoding} encoding: {e}")
        else:
            print("Could not load file with any encoding")
            continue
        
        # Basic dataset info
        print(f"Total products: {len(df)}")
        print("\nCategory counts:")
        print(df['Category'].value_counts())
        
        # Investigate the problematic categories
        problem_categories = ['Luxury Jewelry', 'Make up']
        
        for category in problem_categories:
            print(f"\n--- {category} Category Analysis ---")
            
            # Check if the category exists
            if category not in df['Category'].values:
                print(f"Category '{category}' not found in the dataset")
                continue
                
            # Get products in this category
            category_df = df[df['Category'] == category]
            print(f"Products in {category}: {len(category_df)}")
            
            if len(category_df) == 0:
                print("No products found for this category")
                continue
                
            # Print sample product info
            print("\nSample products:")
            for i, row in category_df.head(3).iterrows():
                print(f"Row {i}:")
                for col in row.index:
                    try:
                        value = row[col]
                        print(f"  {col}: {value}")
                    except:
                        print(f"  {col}: <encoding issue>")
            
            # Check for potential filtering issues
            print("\nChecking for potential filtering issues:")
            
            # Missing values
            missing_cols = category_df.columns[category_df.isna().any()].tolist()
            if missing_cols:
                print(f"Columns with missing values: {', '.join(missing_cols)}")
                for col in missing_cols:
                    missing_count = category_df[col].isna().sum()
                    print(f"  - {col}: {missing_count} missing values out of {len(category_df)}")
            else:
                print("No columns with missing values")
            
            # Empty string values
            for col in ['Product', 'Product Image URL']:
                if col in category_df.columns:
                    empty_count = (category_df[col] == '').sum()
                    if empty_count > 0:
                        print(f"Column '{col}' has {empty_count} empty string values")
                        
            # Verify product display eligibility
            print("\nDisplay eligibility check:")
            for i, row in category_df.head(5).iterrows():
                product_name = row.get('Product', '<missing>')
                has_image = isinstance(row.get('Product Image URL', None), str) and row['Product Image URL'].strip() != ''
                has_rating = not pd.isna(row.get('Rating', None))
                
                print(f"Product '{product_name}':")
                print(f"  - Has image URL: {has_image}")
                print(f"  - Has rating: {has_rating}")
                print(f"  - Would display: {has_image and has_rating}")
                
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_category_display()
