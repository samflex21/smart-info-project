import pandas as pd

# Try to load the CSV file
try:
    df = pd.read_csv('ecommerce dataset.csv', encoding='latin-1')
except:
    try:
        df = pd.read_csv('ecommerce dataset.csv', encoding='cp1252')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit(1)

# Print all categories and count of products in each
print("\nAll categories in dataset:")
category_counts = df['Category'].value_counts()
for category, count in category_counts.items():
    print(f"  - {category}: {count} products")

# Check specifically for Luxury Jewelry and Make up
luxury_count = len(df[df['Category'] == 'Luxury Jewelry'])
makeup_count = len(df[df['Category'] == 'Make up'])

print(f"\nLuxury Jewelry: {luxury_count} products")
print(f"Make up: {makeup_count} products")

# Check first 5 rows
print("\nFirst 5 rows of the dataset:")
print(df.head(5))

# Check all unique categories
print("\nAll unique categories:")
print(df['Category'].unique())
