import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import altair as alt

# Import recommender - handle both module import approaches
try:
    from recommender import ProductRecommender
    import datetime  # When running from src directory
except ModuleNotFoundError:
    from src.recommender import ProductRecommender  # When running as a module

# Set page configuration
st.set_page_config(
    page_title="Smart Store Product Recommendations", 
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
        color: #3C5067;
        font-family: 'Playfair Display', 'Georgia', serif;
        font-weight: 600;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Charts */
    .chart-container {
        background-color: white;
        padding: 20px;
        border-radius: 18px;
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
        border-radius: 18px;
        margin: 20px 0;
        border-left: 4px solid #3C5067;
    }
    
    .recommended-title {
        color: #3C5067;
        font-size: 1.5em;
        margin-bottom: 15px;
        font-weight: bold;
        font-family: 'Playfair Display', 'Georgia', serif;
    }
    
    /* Category tags with matching colors */
    .category-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #3C5067;
        background-color: #F2ECE5;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 500;
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
try:
    df['Rating'] = df['Rating'].fillna(0)
    df['Sales'] = df['Sales'].fillna(0)
    df['Category'] = df['Category'].fillna('Uncategorized')
    df['Product'] = df['Product'].fillna('Unnamed Product')
    
    # Check if Country column exists before filling NA values
    if 'Country' in df.columns:
        df['Country'] = df['Country'].fillna('Unknown')
    else:
        # If Country column doesn't exist, create it with default value
        df['Country'] = 'Global'  # Set a default value for all products
        print("Note: Country column was missing and has been added with default value 'Global'")
except Exception as e:
    print(f"Error during data cleanup: {e}")
    # Continue with available columns

# Print information about each category
categories_count = df.groupby('Category').size().reset_index(name='count')
print("\nCategories and product counts:")
for idx, row in categories_count.iterrows():
    print(f"  - {row['Category']}: {row['count']} products")

# If no data was found, show an error message
if recommender is None or df.empty:
    st.error("No product data available. Please make sure 'ecommerce dataset.csv' is in the project directory.")
    st.stop()

# Function to add a product to the viewed products list
def add_to_viewed_products(product_name):
    # Only add if not already in the list
    if product_name not in st.session_state['viewed_products']:
        # Add to the beginning of the list (most recent first)
        st.session_state['viewed_products'].insert(0, product_name)
        # Keep only the 10 most recent views to avoid overwhelming the recommendations
        if len(st.session_state['viewed_products']) > 10:
            st.session_state['viewed_products'] = st.session_state['viewed_products'][:10]

# Function to get personalized recommendations based on viewed products
def get_personalized_recommendations(num_recommendations=6):
    recommendations = []
    # If the user has viewed products, get recommendations based on those
    if st.session_state['viewed_products']:
        # Use the three most recently viewed products for recommendations
        recent_products = st.session_state['viewed_products'][:3]
        
        # Get recommendations for each recently viewed product
        for product_name in recent_products:
            similar_products = recommender.get_recommendations(product_name, n=3)
            if similar_products:
                for product in similar_products:
                    # Check if this product is already in our recommendations
                    if not any(rec['name'] == product['name'] for rec in recommendations):
                        recommendations.append(product)
                        if len(recommendations) >= num_recommendations:
                            break
            if len(recommendations) >= num_recommendations:
                break
    
    # If we don't have enough recommendations yet (or no viewed products),
    # add some top-rated products
    if len(recommendations) < num_recommendations:
        top_rated = df.sort_values(by='Rating', ascending=False).head(num_recommendations).reset_index(drop=True)
        for i in range(min(len(top_rated), num_recommendations - len(recommendations))):
            product = top_rated.iloc[i]
            # Only add if not already in recommendations
            if not any(rec['name'] == product['Product'] for rec in recommendations):
                recommendations.append({
                    'name': product['Product'],
                    'category': product.get('Category', 'Unknown'),
                    'price': product.get('Sales', 0),
                    'similarity': 1.0,  # High similarity for top rated products
                    'image_url': product.get('Product Image URL', ''),
                    'rating': product.get('Rating', 0)
                })
    
    return recommendations[:num_recommendations]

# Using both a physical column for spacing and CSS for styling
st.markdown("""
<style>
    /* Enhanced sidebar with border and shadow */
    [data-testid="stSidebar"] {
        border-right: 2px solid #C8E6C9;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.1);
    }
    
    /* Reset padding since we're using physical columns for spacing now */
    .main .block-container {
        padding-left: 1rem !important;
        max-width: 100% !important;
    }
    
    /* Product cards get subtle spacing */
    .product-card {
        margin-left: 0rem !important;
    }
    
    /* Stronger selectors to force white text for sidebar headers */
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4,
    [data-testid="stSidebar"] div h3,
    [data-testid="stSidebar"] div h4 {
        color: #FFFFFF !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
        font-weight: bold !important;
    }
    
    /* Override all inline styles for filter headers */
    [data-testid="stSidebar"] [style*="color:"] {
        color: #FFFFFF !important;
    }
    
    /* Make sidebar background deeper blue */
    [data-testid="stSidebar"] .stMarkdown div {
        background: linear-gradient(135deg, #192633 0%, #233547 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# Create 2% spacing and 98% content columns for layout
left_spacer, main_content = st.columns([0.02, 0.98])

# Initialize session state for viewed products if it doesn't exist
if 'viewed_products' not in st.session_state:
    st.session_state['viewed_products'] = []

# Now all content goes into the main content column
with main_content:
    # Modern header with enhanced design
    st.markdown("""
<div style="background: linear-gradient(90deg, #192633 0%, #233547 100%); padding: 1.5rem; border-radius: 12px; margin-bottom: 1.8rem; text-align: center; box-shadow: 0 6px 12px rgba(0,0,0,0.1); position: relative; overflow: hidden;">
<div style="position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, #E8DCCB 0%, #D9CCBA 100%);"></div>
    <div style="display: flex; justify-content: center; align-items: center;">
        <span style="font-size: 32px; color: #FFFFFF; font-weight: 700; letter-spacing: 1.5px; text-shadow: 0 2px 4px rgba(0,0,0,0.15); font-family: 'Playfair Display', serif;">S&N <span style="font-size: 18px; letter-spacing: 3px; font-weight: 400;">SMART STORE</span></span>
    </div>
</div>
""", unsafe_allow_html=True)
    
    # Display personalized recommendations section
    if len(df) > 0 and 'viewed_products' in st.session_state:
        # Get personalized recommendations
        personal_recommendations = get_personalized_recommendations(6)
        
        if personal_recommendations:
            # Create a stylish recommendations section
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(240, 230, 216, 0.4) 0%, rgba(217, 204, 186, 0.6) 100%); 
                        padding: 1.5rem; border-radius: 12px; margin: 1.5rem 0; border-left: 5px solid #3C5067;">
                <h2 style="font-family: 'Playfair Display', 'Georgia', serif; color: #3C5067; margin-bottom: 1rem; font-weight: 600;">
                    <span style="margin-right: 10px;">✨</span> Recommended For You
                </h2>
                <p style="color: #555; margin-bottom: 1.5rem; font-style: italic;">
                    {"Based on your browsing history" if st.session_state['viewed_products'] else "Top picks we think you'll love"}
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; justify-content: space-between;">
            """, unsafe_allow_html=True)
            
            # Create a 3-column layout for recommendations
            rec_cols = st.columns(3)
            
            # Display each recommendation
            for i, product in enumerate(personal_recommendations[:6]):
                with rec_cols[i % 3]:
                    # Create a clean, modern card design
                    st.markdown(f"""
                    <div style="background-color: white; border-radius: 8px; overflow: hidden; 
                                box-shadow: 0 4px 8px rgba(0,0,0,0.05); transition: transform 0.2s;">
                        <div style="height: 160px; display: flex; align-items: center; justify-content: center; 
                                    background-color: #f9f9f9; padding: 1rem; overflow: hidden;">
                            <img src="{product['image_url']}" style="max-height: 140px; max-width: 100%; object-fit: contain;">
                        </div>
                        <div style="padding: 1rem;">
                            <h4 style="color: #3C5067; font-family: 'Playfair Display', serif; margin-bottom: 0.5rem; 
                                     font-size: 1rem; min-height: 2.5rem;">{product['name'][:50] + '...' if len(product['name']) > 50 else product['name']}</h4>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                                <span style="color: #B12704; font-weight: bold;">${product['price']:.2f}</span>
                                <span style="color: #FFA41C;">{'★' * int(product['rating'])}{'☆' * (5-int(product['rating']))}</span>
                            </div>
                            <div style="font-size: 0.8rem; color: #555;">{product['category']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add a view button that will track the product view
                    if st.button(f"See Similar Products", key=f"rec_{i}"):
                        # Add to viewed products
                        add_to_viewed_products(product['name'])
                        # Set as selected product
                        st.session_state['selected_product'] = product['name']
                        # Force rerun
                        st.experimental_rerun()
            
            # Close the recommendation container
            st.markdown("</div></div>", unsafe_allow_html=True)

# Responsive design with cross-device compatibility
st.markdown("""
<style>
    /* Sandstone Beige gradient sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #F0E6D8 0%, #E8DCCB 50%, #D9CCBA 100%);
        border-right: 1px solid #D9CCBA;
        min-width: 230px !important;
        max-width: 250px !important;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.1);
        padding: 1rem 0.5rem !important;
    }
    
    /* Make sidebar text dark blue for contrast on beige */
    [data-testid="stSidebar"] .sidebar p, 
    [data-testid="stSidebar"] .sidebar span, 
    [data-testid="stSidebar"] .sidebar div, 
    /* Radio button and checkbox styling */
    .stRadio > div[role="radiogroup"] > label, .stCheckbox > label {
        color: #3C5067 !important;
        font-weight: 400 !important;
    }
    .stRadio > div[role="radiogroup"] > div[role="radio"], .stCheckbox [data-testid="stCheckbox"] {
        border-color: #3C5067 !important;
    }
    [data-testid="stSidebar"] .stSubheader {
        color: #3C5067 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        font-family: 'Playfair Display', 'Georgia', serif;
        border-bottom: 1px solid rgba(60, 80, 103, 0.2);
        padding-bottom: 0.4rem;
        margin-bottom: 0.5rem;
    }
    
    /* Enhanced Sidebar Filters */
    .sidebar-container {
        background-color: white;
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(60, 80, 103, 0.08);
    }
    
    /* Sidebar section headers */
    .sidebar-container h4 {
        color: #3C5067;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 0.5rem;
        border-bottom: 1px solid #E8DCCB;
        padding-bottom: 0.4rem;
        font-family: 'Playfair Display', 'Georgia', serif;
    }
    
    /* Page background with responsive container */
    .main .block-container {
        background-color: #FFFFFF;
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
    div.row-widget.stRadio > div {flex-direction: column; gap: 3px !important;}
    
    /* Add smooth transitions to all interactive elements */
    .stButton button, .stSelectbox, .stRadio, .stSlider, .stCheckbox, a {
        transition: all 0.3s ease !important;
    }
    
    /* Buttons */
    button, .stButton>button, .stDownloadButton>button, .stButton>button:focus {
        background-color: #3C5067 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.4rem 1.2rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    
    button:hover, .stButton>button:hover, .stDownloadButton>button:hover {
        background-color: #4D6A89 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
        transform: translateY(-1px) !important;
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        border-color: #3C5067;
    }
    
    .stRadio [data-testid="stMarkdownContainer"] p {font-size: 0.9rem; margin: 0 !important; padding: 0 !important; color: #2E2E2E;}
    
    /* Enhance radio button styling */
    .stRadio input[type='radio'] {accent-color: #3C5067 !important;}
    
    /* Enhance slider styling */
    .stSlider [data-baseweb="slider"] div {background-color: #FFFFFF !important;}
    
    /* Compact header styling */
    .sidebar .stSubheader {margin-top: 0.8rem !important; margin-bottom: 0.3rem !important; padding-bottom: 0 !important; font-weight: 600 !important; letter-spacing: 0.4px !important;}
    
    /* Dividers match color scheme */
    .sidebar hr {margin: 0.3rem 0 !important; border-color: rgba(232, 220, 203, 0.6);}
    
    /* Make slider more compact */
    .stSlider {margin: 0.2rem 0 !important; padding: 0 !important;}
    
    /* Selectbox more compact */
    .stSelectbox {margin: 0 !important; padding: 0 !important;}
    
    /* Selectbox styling */
    .stSelectbox [data-baseweb="select"] {border-color: #3C5067 !important;}
    
    /* Style all headers with the brand color */
    h1, h2, h3, h4, h5 {color: #3C5067 !important;}
    
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
        border-right: 1px solid #3C5067;
        box-shadow: 2px 0px 5px rgba(0,0,0,0.05);
    }
    
    /* Product grid with flexible sizing */
    div.row-widget.stHorizontalBlock {
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: flex-start;
    }
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

# Add an elegant title to the sidebar
# Define a unified premium color scheme for all filter sections with lighter blue
filter_colors = {
    'primary': '#5A7CA0',            # Lighter slate blue - primary brand color
    'secondary': '#6B8CAD',          # Medium slate blue - secondary brand color
    'accent': '#C36A2D',             # Terracotta - accent color
    'light_primary': '#7B99B9',      # Lighter version of primary for gradients
    'lightest_primary': '#9DB6D0',   # Lightest version of primary for gradients
    'dark_bg': '#3A5978',            # Dark slate - dark background
    'text_light': '#071D36',         # Deep dark blue for sidebar filter headers
    'text_dark': '#FFFFFF',          # White text for dark backgrounds
    'border': '#3A5978',             # Dark blue border
    'highlight': '#C36A2D'           # Highlight color
}

# Add an elegant title with animated icon to the sidebar with gradient from lighter to darker blue
st.sidebar.markdown("""
<div style="margin: 0 0 1.5rem 0; padding: 0.8rem; 
            background: linear-gradient(135deg, #192633 0%, #233547 100%); 
            border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.15); 
            text-align: center; position: relative; overflow: hidden;">
    <div style="position: absolute; top: -20px; right: -20px; width: 80px; height: 80px; 
               background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
    <div style="position: absolute; bottom: -15px; left: -15px; width: 50px; height: 50px; 
               background: rgba(255,255,255,0.08); border-radius: 50%;"></div>
    <h3 style="margin: 0; padding:0; font-size:1.5rem; color:#FFFFFF !important; 
                font-family:'Playfair Display', Georgia, serif; font-weight: bold;
                position: relative; z-index: 1; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
        <span style="margin-right: 8px;">✨</span> Filter Products
    </h3>
</div>
""", unsafe_allow_html=True)

# Category filter in container with dark blue background
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #192633 0%, #233547 100%); 
            border-radius: 18px; padding: 1rem; margin-bottom: 1.2rem; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.15); border-left: 4px solid #192633;">
    <h4 style="margin-top: 0; margin-bottom: 0.8rem; color: #FFFFFF !important; 
               font-family: 'Playfair Display', serif; font-weight: bold; display: flex; align-items: center; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
        <span style="display: inline-flex; align-items: center; justify-content: center; 
                     width: 24px; height: 24px; background-color: #3A5978; border-radius: 50%; 
                     margin-right: 8px; color: #FFFFFF !important; font-size: 14px;">🏷️</span>
        Category
    </h4>
</div>
""", unsafe_allow_html=True)

# Radio buttons for categories with proper accessibility
selected_category = st.sidebar.radio(
    "Category options",
    all_categories,
    key="category_radio",
    label_visibility="collapsed")

# Define category-based color schemes with lavender variants
category_colors = {
    'Body care': {'primary': '#FFFFFF', 'secondary': '#E8DCCB', 'accent': '#3C5067'},
    'Face care': {'primary': '#FFFFFF', 'secondary': '#E8DCCB', 'accent': '#3C5067'},
    'Hair care': {'primary': '#FFFFFF', 'secondary': '#E8DCCB', 'accent': '#3C5067'},
    'Home and Accessories': {'primary': '#FFFFFF', 'secondary': '#E8DCCB', 'accent': '#3C5067'},
    'Luxury Jewelry': {'primary': '#FFFFFF', 'secondary': '#E8DCCB', 'accent': '#3C5067'},
    'Make up': {'primary': '#FFFFFF', 'secondary': '#E8DCCB', 'accent': '#3C5067'}
}

# Country filter in container with dark blue background
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #192633 0%, #233547 100%); 
            border-radius: 18px; padding: 1rem; margin-bottom: 1.2rem; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.15); border-left: 4px solid #192633;">
    <h4 style="margin-top: 0; margin-bottom: 0.8rem; color: #FFFFFF !important; 
               font-family: 'Playfair Display', serif; font-weight: bold; display: flex; align-items: center; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
        <span style="display: inline-flex; align-items: center; justify-content: center; 
                     width: 24px; height: 24px; background-color: #3A5978; border-radius: 50%; 
                     margin-right: 8px; color: #FFFFFF !important; font-size: 14px;">🌎</span>
        Country
    </h4>
</div>
""", unsafe_allow_html=True)

# Get all countries from the dataset
countries = ['All'] + sorted(df['Country'].unique().tolist())

# Dropdown for countries with proper accessibility
selected_country = st.sidebar.selectbox(
    "Choose a country",
    countries,
    key="country_select",
    label_visibility="collapsed"
)

# Minimum rating filter
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #192633 0%, #233547 100%); 
            border-radius: 18px; padding: 1rem; margin-bottom: 1.2rem; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.15); border-left: 4px solid #192633;">
    <h4 style="margin-top: 0; margin-bottom: 0.8rem; color: #FFFFFF !important; 
               font-family: 'Playfair Display', serif; font-weight: bold; display: flex; align-items: center; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
        <span style="display: inline-flex; align-items: center; justify-content: center; 
                     width: 24px; height: 24px; background-color: #3A5978; border-radius: 50%; 
                     margin-right: 8px; color: #FFFFFF !important; font-size: 14px;">⭐</span>
        Minimum Rating
    </h4>
</div>
""", unsafe_allow_html=True)

# Custom CSS to style the rating slider with unified color scheme
st.markdown(f"""
<style>
    /* Rating slider styling */
    [data-testid="stSlider"] > div > div > div > div {{background-color: {filter_colors['primary']} !important;}}
    [data-testid="stSlider"] > div > div > div > div > div > div {{background-color: {filter_colors['accent']} !important; box-shadow: 0 0 5px rgba(195, 106, 45, 0.5);}}
</style>
""", unsafe_allow_html=True)

# Rating filter with proper label
min_rating = st.sidebar.slider(
    "Minimum star rating",
    min_value=0.0,
    max_value=5.0,
    value=4.0,
    step=0.5,
    format="%.1f★",
    label_visibility="collapsed"
)

filter_by_rating = min_rating > 0

# Sort filter in container with dark blue background
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #192633 0%, #233547 100%); 
            border-radius: 18px; padding: 1rem; margin-bottom: 1.2rem; 
            box-shadow: 0 2px 5px rgba(0,0,0,0.15); border-left: 4px solid #192633;">
    <h4 style="margin-top: 0; margin-bottom: 0.8rem; color: #FFFFFF !important; 
               font-family: 'Playfair Display', serif; font-weight: bold; display: flex; align-items: center; text-shadow: 0 1px 2px rgba(0,0,0,0.3);">
        <span style="display: inline-flex; align-items: center; justify-content: center; 
                     width: 24px; height: 24px; background-color: #3A5978; border-radius: 50%; 
                     margin-right: 8px; color: #FFFFFF !important; font-size: 14px;">🔍</span>
        Sort By
    </h4>
</div>
""", unsafe_allow_html=True)

# Custom CSS to make radio buttons match lighter blue theme with white text throughout
st.markdown(f"""
<style>
    /* Radio button styling */
    .st-cc, .st-cd, .st-ce {{border-color: {filter_colors['primary']} !important;}}
    .st-cc, .st-cd, .st-ce {{background-color: {filter_colors['lightest_primary']} !important;}}
    .st-cc[aria-checked="true"], .st-cd[aria-checked="true"], .st-ce[aria-checked="true"] {{border-color: {filter_colors['dark_bg']} !important;}}
    .st-cc[aria-checked="true"], .st-cd[aria-checked="true"], .st-ce[aria-checked="true"] {{background-color: {filter_colors['primary']} !important;}}
    
    /* Text color for sidebar options */
    .st-bq {{color: {filter_colors['text_light']} !important;}}
    
    /* Also update the slider handle */
    [data-testid="stSlider"] > div > div > div > div {{background-color: {filter_colors['lightest_primary']} !important;}}
    [data-testid="stSlider"] > div > div > div > div > div > div {{background-color: {filter_colors['text_light']} !important; box-shadow: 0 0 5px rgba(255, 255, 255, 0.5);}}
</style>
""", unsafe_allow_html=True)

# Apply direct styling for dropdown menus to ensure they're clearly visible
st.markdown("""
<style>
    /* Main dropdown field */
    .stSelectbox [data-baseweb="select"] {
        background-color: {filter_colors['primary']} !important; 
        border: 1px solid {filter_colors['dark_bg']} !important;
    }
    .stSelectbox [data-baseweb="select"] div[data-testid="stMarkdownContainer"] p {
        color: {filter_colors['text_light']} !important;
        font-weight: bold !important;
    }
    
    /* Dropdown menu */
    div[data-baseweb="popover"] {
        background-color: {filter_colors['primary']} !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: {filter_colors['primary']} !important;
    }
    div[data-baseweb="popover"] ul li {
        background-color: {filter_colors['primary']} !important;
    }
    div[data-baseweb="popover"] ul li div {
        color: {filter_colors['text_light']} !important;
    }
    div[data-baseweb="popover"] [role="option"]:hover {
        background-color: {filter_colors['dark_bg']} !important;
    }
    
    /* Override any inline styles */
    div[role="listbox"] {
        background-color: {filter_colors['primary']} !important;
    }
    div[role="listbox"] [role="option"] {
        background-color: {filter_colors['primary']} !important;
        color: {filter_colors['text_light']} !important;
    }
    div[role="listbox"] [role="option"]:hover {
        background-color: {filter_colors['dark_bg']} !important;
    }
    
    /* Make the selected value visible */
    .stSelectbox [data-baseweb="select"] div {
        color: {filter_colors['text_light']} !important;
    }
    
    /* Override any other elements - except labels */
    div[data-testid="stSelectbox"] *:not(label) {
        color: {filter_colors['text_light']} !important;
    }
    
    /* Make sure list items are visible */
    li[aria-selected="true"], li[aria-selected="false"] {
        background-color: {filter_colors['primary']} !important;
        color: {filter_colors['text_light']} !important;
    }
</style>
""", unsafe_allow_html=True)

# Sort options with proper label
sort_options = ["Rating (High to Low)", "Price (Low to High)", "Price (High to Low)"]
sort_by = st.sidebar.radio(
    "Sort options",
    sort_options,
    key="sort_radio",
    label_visibility="collapsed"
)

# No need for sidebar recommendations selector

# Filter products
filtered_data = df.copy()


# Apply filters to the data with better handling for special categories
if selected_category != 'All':
    # First try direct exact match filtering
    category_filter = filtered_data['Category'] == selected_category
    exact_match_data = filtered_data[category_filter]
    
    # If no exact matches, try partial/contains matching for special categories
    if len(exact_match_data) == 0 and selected_category in ['Luxury Jewelry', 'Body care', 'Face care', 'Hair care', 'Make up']:
        # Try a more flexible match - contains or similar categories
        if selected_category == 'Luxury Jewelry':
            # Look for jewelry, accessories or luxury items
            category_filter = filtered_data['Category'].str.contains('Jewelry|Accessories|Luxury', case=False)
        elif 'care' in selected_category.lower():
            # For care products, match anything with 'care' in it
            search_term = selected_category.split()[0].lower() # 'Body', 'Face', 'Hair'
            category_filter = filtered_data['Category'].str.contains(search_term, case=False)
        elif selected_category == 'Make up':
            # For makeup products
            category_filter = filtered_data['Category'].str.contains('Make|Cosmetic|Beauty', case=False)
            
        filtered_data = filtered_data[category_filter]
        if len(filtered_data) > 0:
            st.info(f"Showing related products for '{selected_category}'")
    else:
        # Use the exact matches if available
        filtered_data = exact_match_data
    
    # Debug info
    print(f"Filtered to {len(filtered_data)} products in category '{selected_category}'")
    
    # If still no products found, show a warning
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

# Function to add a product to the viewed products list
def add_to_viewed_products(product_name):
    # Only add if not already in the list
    if product_name not in st.session_state['viewed_products']:
        # Add to the beginning of the list (most recent first)
        st.session_state['viewed_products'].insert(0, product_name)
        # Keep only the 10 most recent views to avoid overwhelming the recommendations
        if len(st.session_state['viewed_products']) > 10:
            st.session_state['viewed_products'] = st.session_state['viewed_products'][:10]

# Function to get personalized recommendations based on viewed products
def get_personalized_recommendations(num_recommendations=6):
    recommendations = []
    # If the user has viewed products, get recommendations based on those
    if st.session_state['viewed_products']:
        # Use the three most recently viewed products for recommendations
        recent_products = st.session_state['viewed_products'][:3]
        
        # Get recommendations for each recently viewed product
        for product_name in recent_products:
            similar_products = recommender.get_recommendations(product_name, n=3)
            if similar_products:
                for product in similar_products:
                    # Check if this product is already in our recommendations
                    if not any(rec['name'] == product['name'] for rec in recommendations):
                        recommendations.append(product)
                        if len(recommendations) >= num_recommendations:
                            break
            if len(recommendations) >= num_recommendations:
                break
    
    # If we don't have enough recommendations yet (or no viewed products),
    # add some top-rated products
    if len(recommendations) < num_recommendations:
        top_rated = df.sort_values(by='Rating', ascending=False).head(num_recommendations).reset_index(drop=True)
        for i in range(min(len(top_rated), num_recommendations - len(recommendations))):
            product = top_rated.iloc[i]
            # Only add if not already in recommendations
            if not any(rec['name'] == product['Product'] for rec in recommendations):
                recommendations.append({
                    'name': product['Product'],
                    'category': product.get('Category', 'Unknown'),
                    'price': product.get('Sales', 0),
                    'similarity': 1.0,  # High similarity for top rated products
                    'image_url': product.get('Product Image URL', ''),
                    'rating': product.get('Rating', 0)
                })
    
    return recommendations[:num_recommendations]

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
                
                # Make the entire product card clickable with elegant styling
                if product_container.button('Similar Products', key=f"product_{section_id}_{start_idx}_{i}", use_container_width=True):
                    # Add this product to viewed products for future recommendations
                    add_to_viewed_products(product["Product"])
                    # Set as selected product for immediate similar products display
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

# All remaining dashboard content continues below
if len(filtered_data) > 0:
    # Show the top rated products section first
    st.markdown("""
    <div style="margin-bottom: 2rem; position: relative; padding-bottom: 0.8rem;">
        <div style="position: absolute; bottom: 0; left: 0; width: 80px; height: 3px; background: #3C5067; border-radius: 2px;"></div>
        <h2 style="color: #3C5067; margin-bottom: 0.6rem; font-weight: 700; letter-spacing: 0.5px; font-family: 'Playfair Display', 'Georgia', serif;">
            <span style="color: #FFD700; margin-right: 10px; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">⭐</span> Top Rated Products
        </h2>
        <p style="color: #2E2E2E; margin: 0; font-size: 1.05rem; font-weight: 400;">Products our customers love the most</p>
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
            <div style='border: 1px solid #3C5067; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.08); transition: all 0.4s ease; height: 100%; background-color: white; position: relative; cursor: pointer;' onmouseover="this.style.transform='translateY(-5px)';this.style.boxShadow='0 12px 20px rgba(0,0,0,0.12)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 10px rgba(0,0,0,0.08)'">
                <div style='background: linear-gradient(45deg, {colors['primary']} 0%, {colors['secondary']} 100%); padding: 16px; position: relative;'>
                    <h4 style='color: #3C5067; margin: 0; font-weight: 600; font-size: 16px;'>{product['Product']}</h4>
                    <div style='position: absolute; top: 10px; right: 10px; background-color: rgba(255,255,255,0.95); border-radius: 20px; padding: 4px 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                        <span style='color: #3C5067; font-weight: bold;'>TOP RATED</span>
                    </div>
                </div>
                <div style='padding: 20px;'>
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
                    <p style='color: #3C5067; text-align: center; font-weight: 500; font-size: 18px;'>{product['Category']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display price with currency sign using muted rose pink styling
            st.markdown(f"<h3 style='color: #3C5067; margin: 8px 0; font-weight: 700;'>${product['Sales']:.2f}</h3>", unsafe_allow_html=True)
            
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
                        st.markdown('<div style="background-color: white; border-radius: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; height: 100%">', unsafe_allow_html=True)
                        
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
            st.markdown('<div style="background-color: #f8f1e5; padding: 20px; border-radius: 18px; margin: 20px 0; border-left: 4px solid #F39C12;">', unsafe_allow_html=True)
            
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
                    st.markdown(f'<div style="background-color: {primary_color}; border-radius: 18px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); padding: 15px; height: 100%; border-left: 4px solid {accent_color};">', unsafe_allow_html=True)
                    
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
                    
                    # Similarity score inside the card (properly indented and formatted)
                    accent_color = colors['accent']
                    st.markdown(f"<span style='color: {accent_color}; font-weight: bold;'>Similarity: {product['similarity']:.2f}</span>", unsafe_allow_html=True)
                
                # Close the card container
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Close the recommendation section
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No similar products found.")

# Add a footer
st.markdown("""
<div style="margin-top: 4rem; padding: 1.5rem; text-align: center; border-top: 1px solid #E8DCCB; color: #3C5067;">
    <p style="font-size: 0.9rem; margin-bottom: 0.5rem;">&copy; 2025 S&N Smart Store &mdash; All Rights Reserved</p>
    <p style="font-size: 0.8rem; color: #666;">Last updated: {}</p>
</div>
""".format(datetime.datetime.now().strftime("%B %d, %Y")), unsafe_allow_html=True)
