import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import altair as alt

# Import recommender - handle both module import approaches
try:
    from recommender import ProductRecommender  # When running from src directory
except ModuleNotFoundError:
    from src.recommender import ProductRecommender  # When running as a module

# Set page configuration
st.set_page_config(
    page_title="Smart Product Recommendations",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with comprehensive fixes for box duplication
st.markdown("""
<style>
    /* Modern color scheme */
    :root {
        --primary-color: #4A90E2;
        --secondary-color: #F39C12;
        --background-color: #F5F7FA;
        --text-color: #2C3E50;
    }
    
    /* Main content styling */
    .main {
        background-color: var(--background-color);
        color: var(--text-color);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: white;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--primary-color);
    }
    
    /* Metric cards */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Charts */
    .chart-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Super aggressive reset of ALL box styling */
    div, section, article, aside, main, header, footer, nav,
    [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
    .stMarkdown, .row-widget, .block-container, .element-container,
    .main, .sidebar, .stApp, [class^="css-"] {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Specifically target the row containers that show boxes after each row */
    div[data-testid="stHorizontalBlock"],
    div.row-widget.stRow,
    div.css-ocqkz7,
    div.css-1r6slb0,
    div.css-1kyxreq,
    div.css-12w0qpk,
    div.e1f1d6gn1 {
        background-color: transparent !important;
        box-shadow: none !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        flex-wrap: wrap !important;
    }
    
    /* Only apply box styling to product cards and nothing else */
    div.product-card {
        background-color: white !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
        margin: 10px !important;
        height: auto !important;
        min-height: 320px !important;
        max-height: 360px !important;
        display: flex !important;
        flex-direction: column !important;
        position: relative !important;
        z-index: 10 !important;
    }
    
    /* More aggressive removal of ALL container styling */
    div.element-container, div[data-testid="column"], div[data-testid="stVerticalBlock"],
    div.stColumn, div.row-widget, div.stContainer, div.block-container {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Target specifically the outer boxes from column styling */
    div.css-1r6slb0, div.css-1n76uvr, div.css-12w0qpk, div.css-1kyxreq {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important; 
        margin: 5px !important;
    }
    
    /* Make sure ONLY product-card divs have the box styling */
    div:not(.product-card) > div.stMarkdown {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Reduce extra padding and margins */
    .css-1544g2n {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    div.product-title {
        font-size: 16px;
        font-weight: bold;
        margin-top: 8px;
        margin-bottom: 10px;
        height: 40px;
        overflow: hidden;
    }
    div.product-image {
        width: 140px;
        height: 140px;
        margin: 0 auto 15px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        border: 1px solid #f0f0f0;
        border-radius: 8px;
        padding: 5px;
        background-color: white;
    }
    div.product-image img {
        width: 130px !important;
        height: 130px !important;
        object-fit: contain !important;
        display: block !important;
    }
    /* Override Streamlit's image styling */
    .stImage > img {
        width: 130px !important;
        height: 130px !important;
        object-fit: contain !important;
    }
    
    .recommended-section {
        background-color: #f8f1e5;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        border-left: 4px solid #F39C12;
    }
    
    .recommended-title {
        color: #F39C12;
        font-size: 1.5em;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .price { color: #B12704; font-weight: bold; font-size: 1.2em; }
    .rating { color: #FFA41C; }
    .category { color: #565959; font-size: 0.9em; }
    .product-title {
        margin-top: 1rem;
        min-height: 3em;
        overflow: hidden;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
</style>
""", unsafe_allow_html=True)

import re
from urllib.parse import urlparse

def is_valid_url(url):
    """Check if a URL is valid and points to an image.
    This is a simplified version that always returns True to avoid filtering out products.
    """
    # Always return True to ensure all products are shown
    return True
        
def display_uniform_image(image_url):
    """Display an image with uniform dimensions."""
    try:
        if not isinstance(image_url, str) or not image_url.strip():
            st.image("https://via.placeholder.com/140x140?text=No+Image", width=140)
            return
            
        # Apply direct width control
        st.image(image_url, width=140)
    except Exception as e:
        # Fallback to a placeholder image if there's any error
        st.image("https://via.placeholder.com/140x140?text=Image+Error", width=140)

# Initialize recommender
@st.cache_resource
def load_recommender():
    # Try multiple possible locations for the CSV file (prioritize the new cleaned dataset)
    possible_paths = [
        Path(__file__).parent.parent / "ecommerce_dataset.csv",  # new cleaned dataset
        Path("ecommerce_dataset.csv"),  # current directory
        Path(__file__).parent / "ecommerce_dataset.csv",  # src directory
        Path(__file__).parent.parent / "ecommerce_dataset_updated.csv",  # fallback to other updated
        Path(__file__).parent.parent / "ecommerce dataset.csv",  # fallback to original
        Path("ecommerce dataset.csv"),
        Path(__file__).parent / "ecommerce dataset.csv"
    ]
    
    # Find the first path that exists
    data_path = None
    for path in possible_paths:
        if path.exists():
            data_path = path
            break
    
    if data_path is None:
        st.error(f"Could not find CSV file. Searched in: {[str(p) for p in possible_paths]}")
        return None
    
    print(f"Using data from: {data_path}")
    
    # Load the recommender model with the correct data path
    recommender = ProductRecommender(str(data_path))
    
    # Get the dataframe
    df = recommender.data
    
    # Print basic info
    print(f"Loaded dataset with {len(df)} products")
    print("Category counts:")
    print(df['Category'].value_counts())
    
    # CRITICAL FIX: DO NOT FILTER OUT ANY PRODUCTS
    # Simply replace missing/broken image URLs with placeholders
    
    # First, ensure all products have an image URL by replacing missing/empty ones
    for index, row in df.iterrows():
        if not isinstance(row['Product Image URL'], str) or not row['Product Image URL'].strip():
            category = row['Category'].replace(' ', '+') if isinstance(row['Category'], str) else 'Product'
            df.at[index, 'Product Image URL'] = f"https://via.placeholder.com/140x140?text={category}"
    
    # Special handling for problematic categories to ensure they're visible
    # Make sure Luxury Jewelry and Make up categories have products and valid images
    problem_categories = ['Luxury Jewelry', 'Make up']
    for category in problem_categories:
        category_df = df[df['Category'] == category]
        
        # Skip displaying sample products to avoid encoding errors
    
    # Print final category counts
    print("\nFinal category counts:")
    print(df['Category'].value_counts())
    
    # Add message about placeholder images
    placeholder_count = len(df[df['Product Image URL'].str.contains('placeholder.com', na=False)])
    if placeholder_count > 0:
        st.sidebar.info(f"ℹ️ Note: {placeholder_count} products are displayed with placeholder images.")
    
    # Update the recommender's dataframe with our modified version
    recommender.data = df
    
    return recommender
    
# Load the recommender and get the dataframe
recommender = load_recommender()
if recommender is None:
    st.error("Could not load product data. Please check that 'ecommerce dataset.csv' exists.")
    st.stop()

# Get the dataframe from the recommender
df = recommender.data

# Clean up any rows with missing values
df['Rating'] = df['Rating'].fillna(0)
df['Sales'] = df['Sales'].fillna(0)
df['Category'] = df['Category'].fillna('Uncategorized')
df['Product'] = df['Product'].fillna('Unnamed Product')
df['Country'] = df['Country'].fillna('Unknown')

# Print information about each category
categories_count = df.groupby('Category').size().reset_index(name='count')
print("\nCategories and product counts:")
for idx, row in categories_count.iterrows():
    print(f"  - {row['Category']}: {row['count']} products")

# If no data was found, show an error message
if recommender is None or df.empty:
    st.error("No product data available. Please make sure 'ecommerce dataset.csv' is in the project directory.")
    st.stop()

# Create a minimal empty column between sidebar and content for spacing
# This creates a physical gap that cannot be overridden by CSS
_, content_area = st.columns([0.03, 0.97])

# All content will go inside this column
with content_area:
    # Additional CSS for styling the spacing
    st.markdown("""
    <style>
        /* Enhanced sidebar with stronger border and shadow */
        [data-testid="stSidebar"] {
            border-right: 2px solid #C8E6C9;
            box-shadow: 3px 0px 10px rgba(0,0,0,0.1);
        }
        
        /* Add extra margin to all content inside the main area */
        .element-container {
            margin-left: 1rem !important;
        }
        
        /* Product cards get extra spacing */
        .product-card {
            margin-left: 0.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Modern header with green gradient background
    st.markdown("""
<div style="background: linear-gradient(90deg, #1E5631 0%, #0B3C1A 100%); padding: 1.2rem; border-radius: 8px; margin-bottom: 1.5rem; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <span style="font-size: 30px; color: #E8F5E9; margin-right: 12px;">🛍️</span>
    <span style="color: #E8F5E9; font-size: 30px; font-weight: bold; letter-spacing: 1px;">S&N SMART STORE</span>
</div>
""", unsafe_allow_html=True)

# Responsive design with cross-device compatibility
st.markdown("""
<style>
    /* Modern green sidebar styling with fixed width */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E8F5E9 0%, #C8E6C9 100%);
        border-right: 1px solid #A5D6A7;
        min-width: 230px !important;
        max-width: 250px !important;
    }
    
    /* Page background with responsive container */
    .main .block-container {
        background-color: #F9FFF9;
        max-width: 1200px;
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 4rem; /* Much larger left padding to create more space from sidebar */
        padding-bottom: 1rem;
        margin-left: 25px; /* Significantly increased margin from sidebar */
    }
    
    /* Ensure product cards stay in grid */
    div.row-widget.stHorizontal {
        flex-wrap: wrap;
        justify-content: flex-start; /* Changed from space-between to create more even spacing */
        gap: 20px; /* Increased gap between cards */
        padding-left: 10px; /* Additional padding for product grid */
    }
    
    /* Make sure images don't overflow */
    img {
        max-width: 100%;
        height: auto;
    }
    
    /* Fixed heights for product cards */
    div[data-testid="column"] > div:first-child {
        height: 100%;
    }
    
    /* Reduced spacing for sidebar elements */
    .sidebar .element-container {margin-bottom: 0.2rem !important;}
    
    /* Compact radio buttons with modern styling */
    div.row-widget.stRadio > div {flex-direction: column; gap: 1px !important;}
    .stRadio [data-testid="stMarkdownContainer"] p {font-size: 0.9rem; margin: 0 !important; padding: 0 !important; color: #2E7D32;}
    
    /* Enhance radio button styling */
    .stRadio input[type='radio'] {accent-color: #2E7D32 !important;}
    
    /* Enhance slider styling */
    .stSlider [data-baseweb="slider"] div {background-color: #2E7D32 !important;}
    
    /* Compact header styling */
    .sidebar .stSubheader {margin-top: 0.5rem !important; margin-bottom: 0.1rem !important; padding-bottom: 0 !important;}
    
    /* Dividers match color scheme */
    .sidebar hr {margin: 0.3rem 0 !important; border-color: #A5D6A7;}
    
    /* Make slider more compact */
    .stSlider {margin: 0.2rem 0 !important; padding: 0 !important;}
    
    /* Selectbox more compact */
    .stSelectbox {margin: 0 !important; padding: 0 !important;}
    
    /* Selectbox styling */
    .stSelectbox [data-baseweb="select"] {border-color: #2E7D32 !important;}
    
    /* Style all headers with the brand color */
    h1, h2, h3, h4, h5 {color: #1E5631 !important;}
    
    /* Media queries for different screen sizes */
    @media (max-width: 768px) {
        .main .block-container {
            padding: 0.5rem 0.5rem 0.5rem 2.5rem; /* Increased left padding on mobile */
        }
    }
    
    /* Additional space between sidebar and content on all screen sizes */
    .main {
        margin-left: 30px;
    }
    
    /* Force main content area to start with significant gap from sidebar */
    .stApp > header + div > div:nth-child(2) {
        margin-left: 40px !important;
    }
    
    /* Create visual separation between sidebar and main content with a subtle divider */
    [data-testid="stSidebar"] {
        border-right: 1px solid #C8E6C9;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# Get all categories from the dataset
all_category_values = list(df['Category'].unique())

# Make sure these categories exist - direct user can filter by them
required_categories = ['Body care', 'Face care', 'Hair care', 'Home and Accessories', 'Luxury Jewelry', 'Make up']
for cat in required_categories:
    if cat not in all_category_values:
        print(f"Warning: Category '{cat}' not found in dataset or has no products")

# Create the full list with all required categories
all_categories = ['All'] + sorted(set(all_category_values + required_categories))

# Smaller sidebar title
st.sidebar.markdown("<h3 style='margin: 0 0 0.3rem 0; padding:0; font-size:1.2rem;'>Filters</h3>", unsafe_allow_html=True)

# More compact category header
st.sidebar.markdown("<p style='margin:0.3rem 0 0 0; padding:0; font-weight:bold; color:#444; font-size:0.9rem;'>Category</p>", unsafe_allow_html=True)

# Radio buttons for categories with proper accessibility
selected_category = st.sidebar.radio(
    "Category options",
    all_categories,
    index=0,  # Default to 'All'
    key="category_radio",
    label_visibility="collapsed"
)

# Define category-based color schemes with green variants
category_colors = {
    'Body care': {'primary': '#C8E6C9', 'secondary': '#A5D6A7', 'accent': '#2E7D32'},
    'Face care': {'primary': '#DCEDC8', 'secondary': '#C5E1A5', 'accent': '#558B2F'},
    'Hair care': {'primary': '#E8F5E9', 'secondary': '#C8E6C9', 'accent': '#388E3C'},
    'Home and Accessories': {'primary': '#F1F8E9', 'secondary': '#DCEDC8', 'accent': '#33691E'},
    'Luxury Jewelry': {'primary': '#E0F2F1', 'secondary': '#B2DFDB', 'accent': '#00796B'},
    'Make up': {'primary': '#E8F5E9', 'secondary': '#A5D6A7', 'accent': '#1B5E20'}
}

# Compact country header
st.sidebar.markdown("<p style='margin:0.3rem 0 0 0; padding:0; font-weight:bold; color:#444; font-size:0.9rem;'>Country</p>", unsafe_allow_html=True)

# Get all countries from the dataset
countries = ['All'] + sorted(df['Country'].unique().tolist())
selected_country = st.sidebar.selectbox(
    "Choose a country",
    countries,
    index=0,  # Default to 'All'
    key="country_select",
    label_visibility="collapsed"
)

# Compact divider and rating header
st.sidebar.markdown("<hr style='margin:0.4rem 0 0.2rem 0; padding:0; border-color:#eee;'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='margin:0.1rem 0 0 0; padding:0; font-weight:bold; color:#444; font-size:0.9rem;'>Rating</p>", unsafe_allow_html=True)

# Rating filter with proper label
min_rating = st.sidebar.slider(
    "Minimum star rating",
    0.0, 5.0, 0.0, 0.5, 
    format="%.1f★",
    key="rating_slider",
    label_visibility="collapsed"
)
filter_by_rating = min_rating > 0

# Compact divider and sort header
st.sidebar.markdown("<hr style='margin:0.4rem 0 0.2rem 0; padding:0; border-color:#eee;'>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='margin:0.1rem 0 0 0; padding:0; font-weight:bold; color:#444; font-size:0.9rem;'>Sort By</p>", unsafe_allow_html=True)

# Sort options with proper label
sort_options = ["Rating (High to Low)", "Price (Low to High)", "Price (High to Low)"]
sort_by = st.sidebar.radio("Sort options", sort_options, index=0, key="sort_radio", label_visibility="collapsed")

# No need for sidebar recommendations selector

# Filter products
filtered_data = df.copy()


# Apply filters to the data - NO MOCK DATA, ONLY REAL PRODUCTS
if selected_category != 'All':
    # Direct category filtering - no special cases, no mock products
    category_filter = filtered_data['Category'] == selected_category
    filtered_data = filtered_data[category_filter]
    
    # Print debug info
    print(f"Filtered to {len(filtered_data)} products in category '{selected_category}'")
    
    # If no products found, show a warning but don't add any mock data
    if len(filtered_data) == 0:
        st.warning(f"No products found in the '{selected_category}' category.")
        print(f"No products found in category: {selected_category}")
        print("Available categories:")
        print(df['Category'].value_counts())

if selected_country != 'All':
    filtered_data = filtered_data[filtered_data['Country'] == selected_country]
if filter_by_rating:
    filtered_data = filtered_data[filtered_data['Rating'] >= min_rating]

# Sort data
if sort_by == "Rating (High to Low)":
    filtered_data = filtered_data.sort_values('Rating', ascending=False)
elif sort_by == "Price (Low to High)":
    filtered_data = filtered_data.sort_values('Sales', ascending=True)
else:
    filtered_data = filtered_data.sort_values('Sales', ascending=False)

# Display products in a grid
filter_text = ""
if selected_category != 'All' and selected_country != 'All':
    filter_text = f"in {selected_category} from {selected_country}"
elif selected_category != 'All':
    filter_text = f"in {selected_category}"
elif selected_country != 'All':
    filter_text = f"from {selected_country}"

# This subheader is now handled in the product display sections below

# Function to display a row of products using Streamlit-friendly approach
def display_product_row(products, start_idx, section_id='normal', count=3):
    # Check if we're past the end of the products list
    if start_idx >= len(products):
        return False
        
    # Calculate how many products we can actually show
    actual_count = min(count, len(products) - start_idx)
    
    # Create columns
    cols = st.columns(actual_count)
    
    # Display each product in its column
    for i, col in enumerate(cols):
        if i < actual_count:
            with col:
                product = products.iloc[start_idx + i]
                
                # Get category-specific colors
                category = product.get('Category', 'Uncategorized')
                colors = category_colors.get(category, {'primary': '#fff8ec', 'secondary': '#f8f1e5', 'accent': '#F39C12'})
                
                # Create clickable container for the entire product card
                product_container = st.container()
                
                # Make the container clickable
                with product_container.container():
                    # Create product card container with category-specific background
                    primary_color = colors['primary']
                    accent_color = colors['accent']
                    st.markdown(f'<div class="product-card" style="background-color: {primary_color}; border-left: 4px solid {accent_color}; cursor: pointer;">', unsafe_allow_html=True)
                
                # Product image
                if pd.notna(product.get('Product Image URL', None)):
                    st.image(product['Product Image URL'], width=130)
                else:
                    st.image("https://via.placeholder.com/140x140?text=No+Image", width=130)
                
                # Product name
                st.markdown(f"<div class='product-title'>{product['Product']}</div>", unsafe_allow_html=True)
                
                # Price
                st.markdown(f"<div class='price'>${product['Sales']:.2f}</div>", unsafe_allow_html=True)
                
                # Rating stars
                rating = int(product.get('Rating', 0))
                st.markdown(f"<div class='rating'>{'★' * rating}{'☆' * (5-rating)}</div>", unsafe_allow_html=True)
                
                # Category and country with custom styling
                st.markdown(f"<div class='category' style='color: {colors['accent']};'>{category} | {product.get('Country', '')}</div>", unsafe_allow_html=True)
                
                # Close card container
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Make the entire product card clickable
                if product_container.button('👆 Click for similar products', key=f"product_{section_id}_{start_idx}_{i}", use_container_width=True):
                    st.session_state['selected_product'] = product["Product"]
                    # Force rerun to show similar products
                    st.experimental_rerun()
                
    return True





# Display similar products if a product is selected
def display_similar_products():
    if 'selected_product' in st.session_state and st.session_state['selected_product']:
        selected_product = st.session_state['selected_product']
        
        # Get recommendations for the selected product
        similar_products = recommender.get_recommendations(selected_product, n=6)
        
        if similar_products:
            # Display a header for similar products section
            st.markdown(f"""
            <div style="margin: 2rem 0 1rem 0; padding: 20px; background: linear-gradient(135deg, rgba(195, 106, 45, 0.1) 0%, rgba(74, 101, 130, 0.1) 100%); border-radius: 8px;">
                <h2 style="color: var(--terracotta); margin: 0; position: relative; display: inline-block;">
                    Similar to: <span style="color: var(--slate-blue);">{selected_product}</span>
                </h2>
                <p style="margin-top: 0.5rem; color: #333;">Based on category, price, and other factors</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create columns for similar products
            cols = st.columns(3)
            
            # Display each similar product
            for i, product in enumerate(similar_products[:min(6, len(similar_products))]):
                col_idx = i % 3
                with cols[col_idx]:
                    # Get similarity score as percentage
                    similarity = int(product['similarity'] * 100)
                    
                    # Create a product card
                    st.markdown(f'''
                    <div style="background-color: white; border-radius: 8px; padding: 15px; margin-bottom: 15px; 
                                border: 1px solid rgba(74, 101, 130, 0.3); box-shadow: 0 2px 6px rgba(0,0,0,0.05);">
                        <div style="text-align: center; margin-bottom: 10px;">
                            <img src="{product['image_url']}" style="max-width: 120px; max-height: 120px; object-fit: contain;">
                        </div>
                        <h4 style="margin: 10px 0; min-height: 2.5em; color: var(--slate-blue);">{product['name']}</h4>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: bold; color: var(--terracotta); font-size: 1.1em;">${product['price']:.2f}</span>
                            <span style="background-color: rgba(195, 106, 45, 0.1); color: var(--terracotta); 
                                     padding: 3px 8px; border-radius: 12px; font-size: 0.85em;">
                                {similarity}% match
                            </span>
                        </div>
                        <div style="margin-top: 8px;">
                            <span style="color: #FFA41C;">{'★' * int(product['rating'])}{'☆' * (5-int(product['rating']))}</span>
                        </div>
                        <div style="font-size: 0.9em; color: #555; margin-top: 5px;">{product['category']}</div>
                    </div>
                    ''', unsafe_allow_html=True)
            
            # Add a button to clear selection
            if st.button("❌ Clear Selection", key="clear_selection"):
                del st.session_state['selected_product']
                st.experimental_rerun()
        else:
            st.info(f"No similar products found for {selected_product}")

# All remaining dashboard content continues in the content_area column
with content_area:
    if len(filtered_data) > 0:
        # Show the top rated products section first
        st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h2 style="color: #1E5631; margin-bottom: 0.5rem; font-weight: 600; letter-spacing: 0.5px;">
            <span style="color: #F5B041; margin-right: 8px;">⭐</span> Top Rated Products
        </h2>
        <p style="color: #2E7D32; margin: 0; font-size: 1rem;">Products our customers love the most</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get top 3 highest rated products from entire dataset
    top_rated = df.sort_values(by='Rating', ascending=False).head(3).reset_index(drop=True)
    
    # Create columns for top rated products
    top_cols = st.columns(3)
    
    # Display top rated products
    for top_col in range(min(len(top_rated), 3)):
        product = top_rated.iloc[top_col]
        
        # Display product in this column
        with top_cols[top_col]:
            # Get category-specific colors for styling
            category = product.get('Category', 'Uncategorized')
            colors = category_colors.get(category, {'primary': '#fff8ec', 'secondary': '#f8f1e5', 'accent': '#F39C12'})
            
            # Create a modern box for the product with green styling
            st.markdown(f"""
            <div style='border: 1px solid #A5D6A7; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05); transition: transform 0.3s, box-shadow 0.3s; height: 100%; background-color: white;'>
                <div style='background: linear-gradient(45deg, {colors['primary']} 0%, {colors['secondary']} 100%); padding: 12px; position: relative;'>
                    <h4 style='color: #1E5631; margin: 0; font-weight: 600; font-size: 16px;'>{product['Product']}</h4>
                    <div style='position: absolute; top: 8px; right: 8px; background-color: rgba(255,255,255,0.9); border-radius: 4px; padding: 2px 6px;'>
                        <span style='color: #1E5631; font-weight: bold;'>TOP RATED</span>
                    </div>
                </div>
                <div style='padding: 15px;'>
            """, unsafe_allow_html=True)
            
            # Display the product image if available
            if pd.notna(product.get('Product Image URL', None)):
                st.image(product['Product Image URL'], width=200)
            else:
                # Use a styled placeholder with the category name
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {colors['primary']} 0%, {colors['secondary']} 100%); 
                            height: 180px; display: flex; align-items: center; justify-content: center; 
                            margin-bottom: 15px; border-radius: 6px;'>
                    <p style='color: #2A416A; text-align: center; font-weight: 500; font-size: 18px;'>{product['Category']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display price with currency sign using green styling
            st.markdown(f"<h3 style='color: #1E5631; margin: 8px 0; font-weight: 700;'>${product['Sales']:.2f}</h3>", unsafe_allow_html=True)
            
            # Display rating as stars
            rating_stars = "⭐" * int(product['Rating'])
            if product['Rating'] % 1 >= 0.5:
                rating_stars += "½"
            st.markdown(f"<div style='margin-bottom: 8px;'>{rating_stars}</div>", unsafe_allow_html=True)
            
            # Show category and country with matching styling
            if 'Category' in product and 'Country' in product:
                st.markdown(f"<p style='color: #566573; margin-bottom: 12px; font-size: 14px;'>{product['Category']} | {product['Country']}</p>", unsafe_allow_html=True)
            
            # Close the inner div
            st.markdown("</div>", unsafe_allow_html=True)
            
            # View Details button removed as requested
            st.markdown(f"""</div></div>""", unsafe_allow_html=True)
    
    # Add some space after the top rated section
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
    
    # SECOND: Show regular filtered products
    if filter_text:
        st.subheader(f"Filtered {filter_text}")
    else:
        st.subheader("All Products")
    
    # Calculate number of rows needed
    products_per_row = 3
    num_products = len(filtered_data)
    num_rows = (num_products + products_per_row - 1) // products_per_row
            
    # Check if we have any products to display after filtering
    if len(filtered_data) > 0:
        # Process each row of regular products
        for row in range(num_rows):
            # Create columns for this row
            cols = st.columns(products_per_row)
            
            # Fill the columns with products
            for col in range(products_per_row):
                # Calculate the product index
                idx = row * products_per_row + col
                
                # Check if we still have products to display
                if idx < num_products:
                    product = filtered_data.iloc[idx]
                    
                    # Display product in this column
                    with cols[col]:
                        # Create a clean card-like container with CSS
                        st.markdown('<div style="background-color: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; height: 100%">', unsafe_allow_html=True)
                        
                        # Product image
                        if pd.notna(product['Product Image URL']):
                            st.image(product['Product Image URL'], width=130)
                        else:
                            st.image("https://via.placeholder.com/140x140?text=No+Image", width=130)
                        
                        # Product details
                        st.markdown(f"**{product['Product']}**")
                        st.markdown(f"<span style='color: #B12704; font-weight: bold; font-size: 18px;'>${product['Sales']:.2f}</span>", unsafe_allow_html=True)
                        st.markdown(f"<span style='color: #565959; font-size: 14px;'>{product['Category']} | {product['Country']}</span>", unsafe_allow_html=True)
                        
                        # Rating as stars
                        rating = int(product["Rating"])
                        st.markdown(f"<span style='color: #FFA41C;'>{'★' * rating}{'☆' * (5-rating)}</span>", unsafe_allow_html=True)
                        
                        # Close the card container
                        st.markdown('</div>', unsafe_allow_html=True)
                # Close the column
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the row
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Display message if no products match the filters
        st.info("No products match your selected filters. Try adjusting your filters to see more products.")
        
    # Display similar products section if a product is selected
    display_similar_products()


    # Initialize session state for selected product
    if 'selected_product' in st.session_state:
        st.markdown("---")
        st.header("🔍 Products Similar to: " + st.session_state['selected_product'])
        
        # Get similar products
        similar_products = recommender.get_recommendations(st.session_state['selected_product'], n=4)
        
        if similar_products:
            # Create a container with styling
            st.markdown('<div style="background-color: #f8f1e5; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #F39C12;">', unsafe_allow_html=True)
            
            # Create columns for the similar products
            cols = st.columns(len(similar_products))
            
            # Display each product in its column
            for i, (col, product) in enumerate(zip(cols, similar_products)):
                with col:
                    # Get category-specific colors
                    category = product.get('category', 'Uncategorized')
                    colors = category_colors.get(category, {'primary': '#fff8ec', 'secondary': '#f8f1e5', 'accent': '#F39C12'})
                    
                    # Create a clean card container with category-specific styling
                    primary_color = colors['primary']
                    accent_color = colors['accent']
                    st.markdown(f'<div style="background-color: {primary_color}; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; height: 100%; border-left: 4px solid {accent_color};">', unsafe_allow_html=True)
                    
                    # Product image
                    if pd.notna(product.get('image_url', None)):
                        st.image(product['image_url'], width=120)
                    else:
                        st.image("https://via.placeholder.com/120x120?text=No+Image", width=120)
                    
                    # Product details
                    st.markdown(f"<div style='font-weight: bold; font-size: 16px;'>{product['name']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='color: #B12704; font-weight: bold;'>${product.get('price', '0.00')}</div>", unsafe_allow_html=True)
                    
                    # Close container
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Rating stars
                    rating = int(product["rating"])
                    st.markdown(f"<span style='color: #FFA41C;'>{'★' * rating}{'☆' * (5-rating)}</span>", unsafe_allow_html=True)
                    
                    # Category with custom styling
                    accent_color = colors['accent']
                    st.markdown(f"<span style='color: {accent_color}; font-size: 14px;'>{product['category']}</span>", unsafe_allow_html=True)
                    
                    # Similarity score
                    accent_color = colors['accent']
                    st.markdown(f"<span style='color: {accent_color}; font-weight: bold;'>Similarity: {product['similarity']:.2f}</span>", unsafe_allow_html=True)
                # Similarity score
                accent_color = colors['accent']
                st.markdown(f"<span style='color: {accent_color}; font-weight: bold;'>Similarity: {product['similarity']:.2f}</span>", unsafe_allow_html=True)
                
                # Close the card container
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the recommendation section
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No similar products found.")
