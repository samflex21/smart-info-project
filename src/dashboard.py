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
        width: 200px;
        height: 200px;
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
    data_path = project_root / "Enhanced_Ecommerce_Dataset.csv"
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

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.5)

# Sort options
sort_by = st.sidebar.selectbox(
    "Sort by",
    ["Rating (High to Low)", "Price (Low to High)", "Price (High to Low)"]
)

# Filter products
filtered_data = df.copy()
if selected_category != 'All':
    filtered_data = filtered_data[filtered_data['Category'] == selected_category]
filtered_data = filtered_data[filtered_data['Rating'] >= min_rating]

# Sort data
if sort_by == "Rating (High to Low)":
    filtered_data = filtered_data.sort_values('Rating', ascending=False)
elif sort_by == "Price (Low to High)":
    filtered_data = filtered_data.sort_values('Sales', ascending=True)
else:
    filtered_data = filtered_data.sort_values('Sales', ascending=False)

# Display products in a grid
st.subheader(f"Top Rated Products {f'in {selected_category}' if selected_category != 'All' else ''}")

# Create rows of 3 products each
for i in range(0, len(filtered_data), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(filtered_data):
            product = filtered_data.iloc[i + j]
            with cols[j]:
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
                    
                    # Product title with consistent height
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
                    
                    # Show similar products in an expander
                    with st.expander("Show Similar Products"):
                        recommendations = recommender.get_recommendations(product['Product'], n=3)
                        for rec in recommendations:
                            st.write(f"• {rec['name']}")
                            st.write(f"  ${rec['price']:.2f} | ⭐{rec['rating']:.1f}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)


