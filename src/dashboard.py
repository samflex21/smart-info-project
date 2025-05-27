import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from recommender import ProductRecommender
import numpy as np
from pathlib import Path
import altair as alt

# Set page configuration
st.set_page_config(
    page_title="Smart Product Recommendations",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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
    
    div.product-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        margin: 10px 0;
        height: 500px;
        display: flex;
        flex-direction: column;
    }
    div.product-image {
        width: 180px;
        height: 180px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
    }
    div.product-image img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        max-width: 180px;
        max-height: 180px;
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

# Initialize recommender
@st.cache_resource
def load_recommender():
    project_root = Path(__file__).parent.parent
    data_path = project_root / "ecommerce dataset.csv"
    try:
        df = pd.read_csv(data_path, encoding='latin-1')
    except:
        df = pd.read_csv(data_path, encoding='cp1252')
    
    # Filter products with valid image URLs and sort by rating
    df = df[df['Product Image URL'].notna()]
    df['has_valid_image'] = df['Product Image URL'].apply(is_valid_url)
    df = df[df['has_valid_image']]
    df = df.nlargest(100, 'Rating')
    return ProductRecommender(str(data_path)), df

recommender, df = load_recommender()

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
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.5)

# Sort options
sort_by = st.sidebar.selectbox(
    "Sort by",
    ["Rating (High to Low)", "Price (Low to High)", "Price (High to Low)"]
)

# No need for sidebar recommendations selector

# Filter products
filtered_data = df.copy()
if selected_category != 'All':
    filtered_data = filtered_data[filtered_data['Category'] == selected_category]
if selected_country != 'All':
    filtered_data = filtered_data[filtered_data['Country'] == selected_country]
filtered_data = filtered_data[filtered_data['Rating'] >= min_rating]

# Create a separate dataframe for 5-star recommended products
recommended_products = filtered_data[filtered_data['Rating'] == 5.0].copy()
# Remove the recommended products from the main display to avoid duplication
filtered_data = filtered_data[filtered_data['Rating'] < 5.0]

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

# Function to display a row of products
def display_product_row(products, start_idx, section_id='normal', count=3):
    if start_idx >= len(products):
        return
    
    cols = st.columns(3)
    for j in range(count):
        if start_idx + j < len(products):
            product = products.iloc[start_idx + j]
            with cols[j]:
                with st.container():
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    # Product image container
                    st.markdown('<div class="product-image">', unsafe_allow_html=True)
                    try:
                        if pd.notna(product['Product Image URL']) and is_valid_url(product['Product Image URL']):
                            st.image(product['Product Image URL'])
                        else:
                            st.image("https://via.placeholder.com/180x180?text=No+Image")
                    except Exception as e:
                        st.image("https://via.placeholder.com/180x180?text=Image+Error")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Product title with consistent height
                    st.markdown(f'<div class="product-title">**{product["Product"]}**</div>', unsafe_allow_html=True)
                    
                    # Price and category
                    st.markdown(f'<span class="price">${product["Sales"]:.2f}</span>', unsafe_allow_html=True)
                    st.markdown(f'<div class="category">{product["Category"]} | {product["Country"]}</div>', unsafe_allow_html=True)
                    
                    # Rating as stars
                    rating = int(product["Rating"])
                    st.markdown(f'<div class="rating">{"★" * rating}{"☆" * (5-rating)}</div>', unsafe_allow_html=True)
                    
                    # Generate a unique key for each button by combining section_id, row index, and column position
                    unique_button_key = f"{section_id}_{start_idx}_{j}_{product['Product ID']}"
                    
                    # View details button
                    if st.button(f"View Details", key=unique_button_key):
                        st.session_state['selected_product'] = product["Product"]
                    
                    st.markdown('</div>', unsafe_allow_html=True)

# Display products in alternating pattern (2 rows normal, 1 row recommended)
row = 0
normal_product_index = 0
recommended_product_index = 0

# Calculate total number of rows needed
total_normal_rows = (len(filtered_data) + 2) // 3  # Ceiling division
total_recommended_rows = max(1, (len(recommended_products) + 2) // 3)

while normal_product_index < len(filtered_data) or recommended_product_index < len(recommended_products):
    # Display 2 rows of normal products
    for row_num in range(2):
        if normal_product_index < len(filtered_data):
            display_product_row(filtered_data, normal_product_index, section_id=f"normal_{row}_{row_num}")
            normal_product_index += 3
    
    # Display recommended products if available
    if recommended_product_index < len(recommended_products):
        st.markdown('<div class="recommended-section">', unsafe_allow_html=True)
        st.markdown('<div class="recommended-title">⭐ Top Rated Recommended Products ⭐</div>', unsafe_allow_html=True)
        display_product_row(recommended_products, recommended_product_index, section_id=f"recommended_{row}")
        st.markdown('</div>', unsafe_allow_html=True)
        recommended_product_index += 3
    row += 1

# Get top-rated products
top_products = df.nlargest(4, 'Rating')

# Display recommendations in a grid (1 row of 4)
cols = st.columns(4)
for i in range(min(4, len(top_products))):
    product = top_products.iloc[i]
    with cols[i]:
        with st.container():
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            # Product image container
            st.markdown('<div class="product-image">', unsafe_allow_html=True)
            try:
                if pd.notna(product['Product Image URL']) and is_valid_url(product['Product Image URL']):
                    st.image(product['Product Image URL'])
                else:
                    st.image("https://via.placeholder.com/200x200?text=No+Image")
            except Exception as e:
                st.image("https://via.placeholder.com/200x200?text=Image+Error")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Product title
            st.markdown(f'<div class="product-title">**{product["Product"]}**</div>', unsafe_allow_html=True)
            
            # Product details
            st.markdown(f"<p class='price'>${product['Sales']:.2f}</p>", unsafe_allow_html=True)
            
            # Rating with stars
            stars = "⭐" * int(product['Rating'])
            if product['Rating'] % 1 >= 0.5:
                stars += "½"
            st.markdown(f"<p class='rating'>{stars} ({product['Rating']:.1f})</p>", unsafe_allow_html=True)
            
            # Category
            st.markdown(f"<p class='category'>{product['Category']}</p>", unsafe_allow_html=True)
            
            # Recommendation button
            if st.button(f"See similar products", key=f"rec_btn_{i}"):
                st.session_state['selected_product'] = product['Product']
                st.experimental_rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state for selected product
if 'selected_product' in st.session_state:
    st.markdown("---")
    st.header("🔍 Products Similar to: " + st.session_state['selected_product'])
    
    # Get similar products
    similar_products = recommender.get_recommendations(st.session_state['selected_product'], n=4)
    
    if similar_products:
        # Display similar products
        sim_cols = st.columns(4)
        for i in range(min(4, len(similar_products))):
            rec = similar_products[i]
            with sim_cols[i]:
                with st.container():
                    st.markdown('<div class="product-card">', unsafe_allow_html=True)
                    
                    # Product image container
                    st.markdown('<div class="product-image">', unsafe_allow_html=True)
                    try:
                        if pd.notna(rec['image_url']) and is_valid_url(rec['image_url']):
                            st.image(rec['image_url'])
                        else:
                            st.image("https://via.placeholder.com/200x200?text=No+Image")
                    except Exception as e:
                        st.image("https://via.placeholder.com/200x200?text=Image+Error")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Product title
                    st.markdown(f'<div class="product-title">**{rec["name"]}**</div>', unsafe_allow_html=True)
                    
                    # Product details
                    st.markdown(f"<p class='price'>${rec['price']:.2f}</p>", unsafe_allow_html=True)
                    
                    # Rating with stars
                    stars = "⭐" * int(rec['rating'])
                    if rec['rating'] % 1 >= 0.5:
                        stars += "½"
                    st.markdown(f"<p class='rating'>{stars} ({rec['rating']:.1f})</p>", unsafe_allow_html=True)
                    
                    # Category
                    st.markdown(f"<p class='category'>{rec['category']}</p>", unsafe_allow_html=True)
                    
                    # Similarity score
                    st.markdown(f"<p>Similarity: {rec['similarity']:.2f}</p>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No similar products found.")
