import pandas as pd

# Load the CSV file
try:
    df = pd.read_csv('ecommerce dataset.csv', encoding='latin-1')
except:
    try:
        df = pd.read_csv('ecommerce dataset.csv', encoding='cp1252')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit(1)

# Function to check if a URL is likely to be a valid image URL
def is_likely_valid_image_url(url):
    if not isinstance(url, str) or not url:
        return False
        
    # Check if it has a valid image extension
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')
    if any(url.lower().endswith(ext) for ext in valid_extensions):
        return True
        
    # Special handling for common image hosts
    if 'placeholder.com' in url:
        return True
        
    # Amazon images need special checking
    if 'amazon.com/images' in url:
        # Must have an extension or be a complete URL
        if any(url.lower().endswith(ext) for ext in valid_extensions):
            return True
        # Likely incomplete URL - reject it
        return False
        
    # Check for other common image hosts
    common_image_hosts = ['cloudfront.net', 'imgur', 'unsplash', 'staticflickr', 'pexels', 'pixabay']
    if any(host in url.lower() for host in common_image_hosts):
        return True
        
    # Default - assume it's not a valid image URL if we can't confirm
    return False

# Count by category before filtering
print("BEFORE FILTERING:")
print(df['Category'].value_counts())
print(f"Total products: {len(df)}")

# Count products by category that have valid image URLs
print("\nProducts with valid image URLs by category:")
valid_image_df = df[df['Product Image URL'].apply(is_likely_valid_image_url)]
print(valid_image_df['Category'].value_counts())
print(f"Total products with valid images: {len(valid_image_df)}")

# Specifically check the problematic categories
print("\nChecking 'Luxury Jewelry' category:")
luxury_df = df[df['Category'] == 'Luxury Jewelry']
print(f"Total Luxury Jewelry products: {len(luxury_df)}")
luxury_with_images = luxury_df[luxury_df['Product Image URL'].apply(is_likely_valid_image_url)]
print(f"Luxury Jewelry products with valid images: {len(luxury_with_images)}")
if len(luxury_with_images) > 0:
    print("Sample Luxury Jewelry products with valid images:")
    print(luxury_with_images[['Product', 'Product Image URL']].head(3))
else:
    print("No Luxury Jewelry products with valid images found.")

print("\nChecking 'Make up' category:")
makeup_df = df[df['Category'] == 'Make up']
print(f"Total Make up products: {len(makeup_df)}")
makeup_with_images = makeup_df[makeup_df['Product Image URL'].apply(is_likely_valid_image_url)]
print(f"Make up products with valid images: {len(makeup_with_images)}")
if len(makeup_with_images) > 0:
    print("Sample Make up products with valid images:")
    print(makeup_with_images[['Product', 'Product Image URL']].head(3))
else:
    print("No Make up products with valid images found.")
