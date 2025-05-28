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
    """Check if a URL is valid and points to an image."""
    try:
        # Check if it's a string
        if not isinstance(url, str):
            return False
            
        # Check if it's a valid URL format
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            return False
            
        # Check if it points to an image
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
        return any(url.lower().endswith(ext) for ext in image_extensions)
    except:
        return False
        
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
    # Try multiple possible locations for the CSV file
    possible_paths = [
        Path(__file__).parent.parent / "ecommerce dataset.csv",  # project root
        Path("ecommerce dataset.csv"),  # current directory
        Path(__file__).parent / "ecommerce dataset.csv"  # src directory
    ]
    
    # Find the first path that exists
    data_path = None
    for path in possible_paths:
        if path.exists():
            data_path = path
            break
    
    if data_path is None:
        st.error(f"Could not find CSV file. Searched in: {[str(p) for p in possible_paths]}")
        # Create a small sample dataset for demonstration
        return None, pd.DataFrame()
    
    # Try different encodings
    try:
        df = pd.read_csv(data_path, encoding='latin-1')
    except:
        try:
            df = pd.read_csv(data_path, encoding='cp1252')
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return None, pd.DataFrame()
    
    # Filter products with valid image URLs and sort by rating
    df = df[df['Product Image URL'].notna()]
    df['has_valid_image'] = df['Product Image URL'].apply(is_valid_url)
    df = df[df['has_valid_image']]
    df = df.nlargest(100, 'Rating')
    return ProductRecommender(str(data_path)), df

recommender, df = load_recommender()

# If no data was found, show an error message
if recommender is None or df.empty:
    st.error("No product data available. Please make sure 'ecommerce dataset.csv' is in the project directory.")
    st.stop()

# Title
st.title("🛍️ Smart Shopping")

# Sidebar filters
st.sidebar.title("Filters")

# Category filter
categories = ['All'] + sorted(df['Category'].unique().tolist())
selected_category = st.sidebar.selectbox("Category", categories)

# Country filter
countries = ['All'] + sorted(df['Country'].unique().tolist())
selected_country = st.sidebar.selectbox("Country", countries)

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)
filter_by_rating = min_rating > 0

# Sort options
sort_by = st.sidebar.selectbox(
    "Sort by",
    ["Rating (High to Low)", "Price (Low to High)", "Price (High to Low)"]
)

# No need for sidebar recommendations selector

# Filter products
filtered_data = df.copy()

# Apply filters to the data
if selected_category != 'All':
    filtered_data = filtered_data[filtered_data['Category'] == selected_category]
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

st.subheader(f"Products {filter_text}")

# Function to display a row of products using Streamlit-friendly approach
def display_product_row(products, start_idx, section_id='normal', count=3):
    # Check if we're past the end of the products list
    if start_idx >= len(products):
        return False
        
    # Calculate how many actual products we can display in this row
    available_products = min(count, len(products) - start_idx)
    
    # Only create a row if we have at least one product to show
    if available_products <= 0:
        return False
    
    # Create columns for layout but avoid nested containers
    cols = st.columns(available_products)
    
    # Display products in their respective columns
    for j in range(available_products):
        product = products.iloc[start_idx + j]
        
        with cols[j]:
            # Single div for the product card - no nesting of containers
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # Product image
            if pd.notna(product['Product Image URL']):
                st.image(product['Product Image URL'], width=130)
            else:
                st.image("https://via.placeholder.com/140x140?text=No+Image", width=130)
            
            # Product details
            st.markdown(f'<div class="product-title">{product["Product"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price">${product["Sales"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="category">{product["Category"]} | {product["Country"]}</div>', unsafe_allow_html=True)
            
            # Rating as stars
            rating = int(product["Rating"])
            st.markdown(f'<div class="rating">{"★" * rating}{"☆" * (5-rating)}</div>', unsafe_allow_html=True)
            
            # Unique button key to avoid conflicts
            unique_button_key = f"{section_id}_{start_idx}_{j}_{product['Product ID']}"
            
            # View details button
            if st.button("View Details", key=unique_button_key):
                st.session_state['selected_product'] = product["Product"]
                st.experimental_rerun()
                
if len(filtered_data) > 0:
    st.subheader("Products")
    
    # Display products in a simple grid using Streamlit columns
    # Calculate number of rows needed
    products_per_row = 3
    num_products = len(filtered_data)
    num_rows = (num_products + products_per_row - 1) // products_per_row
    
    # Process each row
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
                    
                    # View details button
                    button_id = f"btn_{row}_{col}_{product['Product ID']}"
                    if st.button("View Details", key=button_id):
                        st.session_state['selected_product'] = product["Product"]
                        st.experimental_rerun()
                    
                    # Close the card container
                    st.markdown('</div>', unsafe_allow_html=True)
    
# Display message if no products match the filters
elif len(filtered_data) == 0:
    st.info("No products match your selected filters. Try adjusting your filters to see more products.")


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
                # Create a clean card container
                st.markdown('<div style="background-color: #fff8ec; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; height: 100%;">', unsafe_allow_html=True)
                
                # Product image
                if pd.notna(product.get('image_url', None)):
                    st.image(product['image_url'], width=130)
                else:
                    st.image("https://via.placeholder.com/140x140?text=No+Image", width=130)
                
                # Product details
                st.markdown(f"**{product['name']}**")
                st.markdown(f"<span style='color: #B12704; font-weight: bold; font-size: 18px;'>${product['price']:.2f}</span>", unsafe_allow_html=True)
                
                # Rating stars
                rating = int(product["rating"])
                st.markdown(f"<span style='color: #FFA41C;'>{'★' * rating}{'☆' * (5-rating)}</span>", unsafe_allow_html=True)
                
                # Category
                st.markdown(f"<span style='color: #565959; font-size: 14px;'>{product['category']}</span>", unsafe_allow_html=True)
                
                # Similarity score
                st.markdown(f"<span style='color: #F39C12; font-weight: bold;'>Similarity: {product['similarity']:.2f}</span>", unsafe_allow_html=True)
                
                # Close the card container
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the recommendation section
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No similar products found.")
