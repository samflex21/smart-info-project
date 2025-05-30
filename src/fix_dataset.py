"""
This script attempts to fix encoding issues in the dataset and create a clean version
that can be properly loaded by the dashboard.
"""
import pandas as pd
import os
import chardet
import csv
from pathlib import Path
import sys

def fix_dataset():
    """Attempt to fix the dataset encoding issues"""
    print("=== DATASET REPAIR UTILITY ===")
    
    # Find the dataset file
    base_dir = Path(__file__).parent.parent
    possible_paths = [
        base_dir / "ecommerce dataset.csv",
        Path("ecommerce dataset.csv"),
        Path(__file__).parent / "ecommerce dataset.csv",
        base_dir / "ecommerce_dataset_updated.csv"
    ]
    
    found_path = None
    for path in possible_paths:
        if path.exists():
            found_path = path
            print(f"Found dataset at: {path}")
            break
    
    if found_path is None:
        print("ERROR: Could not find dataset file")
        return
    
    # Detect encoding
    print("Detecting file encoding...")
    with open(found_path, 'rb') as f:
        raw_data = f.read(10000)  # Read first 10000 bytes for detection
        result = chardet.detect(raw_data)
        detected_encoding = result['encoding']
        confidence = result['confidence']
    
    print(f"Detected encoding: {detected_encoding} (confidence: {confidence:.2f})")
    
    # Try to load file line by line to find problematic rows
    print("\nAttempting to parse file line by line to identify problematic rows...")
    problematic_lines = []
    total_lines = 0
    
    try:
        with open(found_path, 'rb') as file:
            for i, line in enumerate(file):
                total_lines += 1
                try:
                    decoded_line = line.decode('utf-8').strip()
                except UnicodeDecodeError:
                    problematic_lines.append(i+1)
                    if len(problematic_lines) <= 5:  # Show only first 5 problematic lines
                        print(f"Line {i+1} has encoding issues")
    except Exception as e:
        print(f"Error reading file: {e}")
    
    print(f"Total lines in file: {total_lines}")
    print(f"Found {len(problematic_lines)} problematic lines")
    
    # Try to create a cleaned dataset manually
    print("\nAttempting to create a clean dataset...")
    output_path = base_dir / "clean_ecommerce_dataset.csv"
    
    try:
        # First, try to get the header
        with open(found_path, 'rb') as infile:
            for line in infile:
                try:
                    header_line = line.decode('utf-8', errors='replace').strip()
                    break
                except:
                    continue
        
        # Manually parse and write clean file
        with open(found_path, 'rb') as infile, open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            
            # Write header
            header = header_line.split(',')
            writer.writerow(header)
            
            # Process remaining lines
            good_lines = 0
            error_lines = 0
            
            for i, line in enumerate(infile):
                if i == 0:  # Skip header since we already processed it
                    continue
                    
                try:
                    # Try to decode with different encodings
                    for enc in ['utf-8', 'latin-1', 'cp1252']:
                        try:
                            decoded = line.decode(enc, errors='replace')
                            fields = decoded.strip().split(',')
                            
                            # Basic validation - check if field count matches header
                            if len(fields) == len(header):
                                writer.writerow(fields)
                                good_lines += 1
                                break
                        except:
                            continue
                    else:
                        error_lines += 1
                except Exception as e:
                    error_lines += 1
            
            print(f"Processed {good_lines} good lines and skipped {error_lines} problematic lines")
        
        print(f"Created clean dataset at: {output_path}")
        
        # Now try to load the clean dataset
        print("\nTrying to load the clean dataset...")
        try:
            df = pd.read_csv(output_path)
            print(f"Successfully loaded clean dataset with {len(df)} rows and {len(df.columns)} columns")
            
            # Check for Luxury Jewelry and Make up categories
            if 'Category' in df.columns:
                category_counts = df['Category'].value_counts()
                print("\nCategory distribution in clean dataset:")
                print(category_counts)
                
                for category in ['Luxury Jewelry', 'Make up']:
                    count = (df['Category'] == category).sum()
                    print(f"\nProducts in '{category}': {count}")
                    
                    if count > 0:
                        # Create a dedicated file just for these categories
                        cat_df = df[df['Category'] == category]
                        cat_path = base_dir / f"{category.replace(' ', '_')}_products.csv"
                        cat_df.to_csv(cat_path, index=False)
                        print(f"Created specific file for {category} with {len(cat_df)} products at: {cat_path}")
                        
                        # Show sample of the data
                        print("\nSample products:")
                        for _, row in cat_df.head(3).iterrows():
                            print(f"Product: {row.get('Product', 'N/A')}")
                            print(f"Rating: {row.get('Rating', 'N/A')}")
                            if 'Product Image URL' in row:
                                print(f"Image URL: {row.get('Product Image URL', 'N/A')}")
                            print("---")
            else:
                print("WARNING: No 'Category' column found in the clean dataset")
        except Exception as e:
            print(f"Error loading clean dataset: {e}")
    
    except Exception as e:
        print(f"Error creating clean dataset: {e}")
    
    print("\n=== DATASET REPAIR COMPLETED ===")

if __name__ == "__main__":
    fix_dataset()
