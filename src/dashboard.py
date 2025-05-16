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
</style>
""", unsafe_allow_html=True)

# Initialize recommender
@st.cache_resource
def load_recommender():
    data_path = Path(r"C:\Users\samuel\Desktop\smart information\Enhanced_Ecommerce_Dataset.csv")
    # Try different encodings
    try:
        df = pd.read_csv(data_path, encoding='latin-1')
    except:
        df = pd.read_csv(data_path, encoding='cp1252')
    
    # Print columns for debugging
    print("Columns in dataset:", list(df.columns))
    print("\nFirst few rows:")
    print(df.head())
    
    return ProductRecommender(str(data_path)), df

recommender, df = load_recommender()

# Sidebar
with st.sidebar:
    st.title("🛍️ Navigation")
    page = st.radio(
        "Select a page:",
        ["Product Explorer", "Recommendation Engine", "Analytics Dashboard"]
    )

# Main content
if page == "Product Explorer":
    st.title("Product Explorer")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        # Get categories safely
        all_categories = recommender.get_categories()
        categories = ["All Categories"] + all_categories if all_categories else ["All Categories"]
        category = st.selectbox("Select Category", categories)
    
    with col2:
        # Get price range safely
        min_price = float(df['price'].min()) if 'price' in df.columns else 0.0
        max_price = float(df['price'].max()) if 'price' in df.columns else 1000.0
        price_range = st.slider(
            "Price Range",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price)
        )
    
    with col3:
        min_rating = st.slider(
            "Minimum Rating",
            min_value=0.0,
            max_value=5.0,
            value=0.0
        )
    
    # Product metrics
    st.subheader("Product Metrics")
    metric1, metric2, metric3, metric4 = st.columns(4)
    
    with metric1:
        st.metric("Total Products", len(df))
    
    with metric2:
        avg_price = df['price'].mean() if 'price' in df.columns else 0
        st.metric("Average Price", f"${avg_price:.2f}")
    
    with metric3:
        rating_col = next((col for col in df.columns if 'rating' in col.lower()), None)
        avg_rating = df[rating_col].mean() if rating_col in df.columns else 0
        st.metric("Average Rating", f"{avg_rating:.1f}")
    
    with metric4:
        if 'category' in df.columns:
            category_count = len(set(df['category'].dropna()))
            st.metric("Categories", category_count)
        else:
            st.metric("Categories", 0)

elif page == "Recommendation Engine":
    st.title("Product Recommendations")
    
    # Product selection
    product_names = recommender.get_all_product_names()
    if product_names:
        selected_product = st.selectbox("Select a product:", product_names)
        
        if selected_product:
            # Display product details
            product_details = recommender.get_product_details(selected_product)
            
            if product_details:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Category", product_details.get('category', 'Unknown'))
                with col2:
                    st.metric("Price", f"${product_details.get('price', 0):.2f}")
                with col3:
                    st.metric("Rating", f"{product_details.get('avg_rating', 0):.1f}")
                
                # Get and display recommendations
                recommendations = recommender.get_recommendations(selected_product)
                
                if recommendations:
                    st.subheader("Similar Products")
                    for rec in recommendations:
                        with st.container():
                            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                            with col1:
                                st.write(rec['name'])
                            with col2:
                                st.write(f"Category: {rec['category']}")
                            with col3:
                                st.write(f"Price: ${rec['price']:.2f}")
                            with col4:
                                st.write(f"{rec['similarity']:.2%} match")
                else:
                    st.info("No recommendations found for this product.")
            else:
                st.error("Could not find product details.")
    else:
        st.error("No products found in the dataset.")

else:  # Analytics Dashboard
    st.title("Analytics Dashboard")
    
    # Category Distribution
    if 'category' in df.columns:
        st.subheader("Category Distribution")
        category_counts = df['category'].value_counts()
        fig = px.pie(values=category_counts.values, names=category_counts.index)
        st.plotly_chart(fig)
    
    # Price Distribution
    if 'price' in df.columns:
        st.subheader("Price Distribution")
        fig = px.histogram(df, x='price', nbins=50)
        st.plotly_chart(fig)
    
    # Rating Analysis
    rating_col = next((col for col in df.columns if 'rating' in col.lower()), None)
    if rating_col and 'category' in df.columns:
        st.subheader("Rating Analysis")
        fig = px.box(df, x='category', y=rating_col)
        st.plotly_chart(fig)
