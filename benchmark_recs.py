import pandas as pd

# --- Load your Data ---
try:
    df = pd.read_csv('ecommerce_dataset.csv')
    # Basic data cleaning
    df.dropna(subset=['Product', 'Category'], inplace=True)
    
    # Check if Country column exists
    if 'Country' in df.columns:
        df.dropna(subset=['Country'], inplace=True)
    else:
        # If Country column doesn't exist, create it with default value
        df['Country'] = 'Global'
        print("Note: Country column was missing and has been added with default value 'Global'")
    
    # Handle Rating and Price columns
    if 'Rating' in df.columns:
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    else:
        df['Rating'] = 5.0  # Default rating if column missing
        print("Note: Rating column was missing and has been added with default value 5.0")
    
    if 'Price' in df.columns:
        # Clean and convert Price: remove '$', ',', convert to numeric
        df['Price'] = df['Price'].astype(str).str.replace(r'[$,]', '', regex=True)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df['Price'].fillna(0, inplace=True)
    else:
        df['Price'] = 0.0  # Default price if column missing
        print("Note: Price column was missing and has been added with default value 0.0")

except FileNotFoundError:
    print("Error: ecommerce_data.csv not found. Make sure it's in the same directory.")
    exit()
except Exception as e:
    print(f"Error loading or cleaning data: {e}")
    print("Attempting to continue with available data...")

if df.empty:
    print("DataFrame is empty after loading/cleaning. Cannot proceed.")
    exit()

# Print data summary
print(f"\nData Summary:\n{'-'*40}")
print(f"Total products: {len(df)}")
print(f"Unique products: {df['Product'].nunique()}")
print(f"Categories: {df['Category'].nunique()} unique values")
print(f"Countries: {df['Country'].nunique()} unique values")
print(f"Rating range: {df['Rating'].min()} to {df['Rating'].max()}")
print(f"Price range: {df['Price'].min()} to {df['Price'].max()}")
print(f"{'-'*40}\n")

# --- Recommendation Algorithms ---

def recommend_v1_by_category(product_name, data_df, n=5):
    """Recommends N products from the same category, excluding the product itself."""
    if product_name not in data_df['Product'].values:
        return pd.DataFrame()
    
    target_product_series = data_df[data_df['Product'] == product_name]
    if target_product_series.empty:
        return pd.DataFrame()
    target_category = target_product_series.iloc[0]['Category']
    
    similar_df = data_df[
        (data_df['Category'] == target_category) & 
        (data_df['Product'] != product_name)
    ]
    
    if len(similar_df) == 0:
        return pd.DataFrame()
    # Sort by rating to make sampling a bit more relevant if many options
    return similar_df.sort_values(by='Rating', ascending=False).head(n)

def recommend_v2_by_category_and_country(product_name, data_df, n=5):
    """Recommends N products from the same category AND country, excluding the product itself."""
    if product_name not in data_df['Product'].values:
        return pd.DataFrame()
        
    target_product_series = data_df[data_df['Product'] == product_name]
    if target_product_series.empty:
        return pd.DataFrame()
    target_category = target_product_series.iloc[0]['Category']
    target_country = target_product_series.iloc[0]['Country']
    
    similar_df = data_df[
        (data_df['Category'] == target_category) & 
        (data_df['Country'] == target_country) & 
        (data_df['Product'] != product_name)
    ]
    
    if len(similar_df) == 0:
        return pd.DataFrame()
    return similar_df.sort_values(by='Rating', ascending=False).head(n)

def recommend_v3_by_global_popularity(data_df, n=5, exclude_product_name=None):
    """Recommends N globally most popular products based on Rating, excluding a specific product if provided."""
    temp_df = data_df.copy()
    if exclude_product_name and exclude_product_name in temp_df['Product'].values:
        temp_df = temp_df[temp_df['Product'] != exclude_product_name]
        
    # Sort by Rating (descending), then by Price (ascending as tie-breaker, optional)
    # Ensure unique products are recommended if multiple have same top rating
    popular_df = temp_df.sort_values(by=['Rating', 'Price'], ascending=[False, True])
    popular_df = popular_df.drop_duplicates(subset=['Product']).head(n)
    return popular_df

# --- Benchmarking Logic ---

def run_benchmark(data_df, num_recommendations_to_request=5):
    all_products = data_df['Product'].unique()
    num_total_products = len(all_products)

    if num_total_products == 0:
        print("No products to benchmark.")
        return

    # Metrics for Algorithm 1 (Category only)
    v1_got_any_recs = 0
    v1_got_full_recs = 0
    
    # Metrics for Algorithm 2 (Category + Country)
    v2_got_any_recs = 0
    v2_got_full_recs = 0
    
    # Metrics for Algorithm 3 (Global Popularity)
    # V3 will always provide recommendations if n <= total unique products,
    # so coverage isn't the main comparison point for it.
    # We'll focus on its qualitative output.

    print(f"Benchmarking on {num_total_products} unique products...\n")

    for product_name in all_products:
        # Algorithm 1
        recs_v1 = recommend_v1_by_category(product_name, data_df, n=num_recommendations_to_request)
        if not recs_v1.empty:
            v1_got_any_recs += 1
            if len(recs_v1) >= num_recommendations_to_request: # Use >= in case more than n are equally good
                v1_got_full_recs += 1
        
        # Algorithm 2
        recs_v2 = recommend_v2_by_category_and_country(product_name, data_df, n=num_recommendations_to_request)
        if not recs_v2.empty:
            v2_got_any_recs += 1
            if len(recs_v2) >= num_recommendations_to_request:
                v2_got_full_recs += 1

    print("--- Benchmark Results ---")
    print(f"Total unique products: {num_total_products}")
    print(f"Recommendations requested per product (for V1/V2): {num_recommendations_to_request}\n")

    print("Algorithm V1 (Content-Based: Category Only):")
    print(f"  Products receiving at least 1 recommendation: {v1_got_any_recs} ({v1_got_any_recs/num_total_products*100:.2f}%)")
    print(f"  Products receiving full {num_recommendations_to_request} recommendations: {v1_got_full_recs} ({v1_got_full_recs/num_total_products*100:.2f}%)\n")

    print("Algorithm V2 (Content-Based: Category + Country):")
    print(f"  Products receiving at least 1 recommendation: {v2_got_any_recs} ({v2_got_any_recs/num_total_products*100:.2f}%)")
    print(f"  Products receiving full {num_recommendations_to_request} recommendations: {v2_got_full_recs} ({v2_got_full_recs/num_total_products*100:.2f}%)\n")
    
    print("Algorithm V3 (Baseline: Global Popularity by Rating):")
    print(f"  This algorithm typically provides {min(num_recommendations_to_request, len(data_df['Product'].unique()))} global top products.")
    print(f"  Coverage is generally 100% if N <= total unique products.\n")

    # Qualitative comparison for a sample product
    sample_product_name = all_products[0] 
    print(f"--- Qualitative Sample for Product: '{sample_product_name}' ---")
    target_product_details = data_df[data_df['Product'] == sample_product_name].iloc[0]
    print(f"Details of '{sample_product_name}': Category='{target_product_details['Category']}', Country='{target_product_details['Country']}', Rating={target_product_details['Rating']}\n")
    
    recs_v1_sample = recommend_v1_by_category(sample_product_name, data_df, n=3)
    print(f"Recommendations from V1 (Category) for '{sample_product_name}':")
    if not recs_v1_sample.empty:
        print(recs_v1_sample[['Product', 'Category', 'Country', 'Rating', 'Price']])
    else:
        print("  No recommendations.")

    recs_v2_sample = recommend_v2_by_category_and_country(sample_product_name, data_df, n=3)
    print(f"\nRecommendations from V2 (Category + Country) for '{sample_product_name}':")
    if not recs_v2_sample.empty:
        print(recs_v2_sample[['Product', 'Category', 'Country', 'Rating', 'Price']])
    else:
        print("  No recommendations.")

    recs_v3_sample = recommend_v3_by_global_popularity(data_df, n=3, exclude_product_name=sample_product_name)
    print(f"\nRecommendations from V3 (Global Popularity by Rating) - (context of '{sample_product_name}' ignored by V3):")
    if not recs_v3_sample.empty:
        print(recs_v3_sample[['Product', 'Category', 'Country', 'Rating', 'Price']])
    else:
        print("  No recommendations.")

# Run the benchmark
if not df.empty:
    run_benchmark(df, num_recommendations_to_request=5)
else:
    print("Skipping benchmark due to empty DataFrame.")
