import pandas as pd
import numpy as np

# Load the existing dataset
try:
    df = pd.read_csv('ecommerce dataset.csv', encoding='latin-1')
except:
    try:
        df = pd.read_csv('ecommerce dataset.csv', encoding='cp1252')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit(1)

print(f"Original dataset size: {len(df)} products")

# Create sample products for Luxury Jewelry
luxury_products = []
for i in range(1, 6):
    product = {
        'Row ID': 90000 + i,
        'Order ID': f'SAMPLE-LUX-{i}',
        'Product': f'Luxury Diamond Ring {i}',
        'Category': 'Luxury Jewelry',
        'Rating': 5,
        'Sales': 999.99,
        'Country': 'France',
        'Product Image URL': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60',
        'Product ID': f'LUX-{i}'
    }
    luxury_products.append(product)

# Create sample products for Make up
makeup_products = []
for i in range(1, 6):
    product = {
        'Row ID': 91000 + i,
        'Order ID': f'SAMPLE-MU-{i}',
        'Product': f'Premium Lipstick Collection {i}',
        'Category': 'Make up',
        'Rating': 4.5,
        'Sales': 49.99,
        'Country': 'USA',
        'Product Image URL': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=60',
        'Product ID': f'MU-{i}'
    }
    makeup_products.append(product)

# Add sample products to the dataframe
for product in luxury_products + makeup_products:
    df = df.append(product, ignore_index=True)

print(f"Dataset size after adding samples: {len(df)} products")

# Save the updated dataset
df.to_csv('ecommerce dataset with samples.csv', index=False)
print("Saved updated dataset to 'ecommerce dataset with samples.csv'")

# Verify the categories now
print("\nCategory counts in updated dataset:")
print(df['Category'].value_counts())
