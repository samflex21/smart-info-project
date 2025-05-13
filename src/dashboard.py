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
    return ProductRecommender(str(data_path)), pd.read_csv(data_path)

recommender, df = load_recommender()

# Sidebar
with st.sidebar:
    st.title("🛍️ Navigation")
    page = st.radio(
        "Choose a page",
        ["Product Explorer", "Recommendation Engine", "Analytics Dashboard", "Smart Product Recommendations"]
    )
    
    st.markdown("---")
    st.markdown("### Filters")
    
    # Category filter
    categories = ["All"] + sorted(df['category'].unique().tolist())
    selected_category = st.selectbox("Select Category", categories)
    
    # Price range filter
    price_range = st.slider(
        "Price Range ($)",
        min_value=float(df['price'].min()),
        max_value=float(df['price'].max()),
        value=(float(df['price'].min()), float(df['price'].max()))
    )
    
    # Rating filter
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 0.0, 0.5)

# Apply filters
filtered_df = df.copy()
if selected_category != "All":
    filtered_df = filtered_df[filtered_df['category'] == selected_category]
filtered_df = filtered_df[
    (filtered_df['price'] >= price_range[0]) &
    (filtered_df['price'] <= price_range[1]) &
    (filtered_df['avg_rating'] >= min_rating)
]

# Main content
if page == "Product Explorer":
    st.title("🔍 Product Explorer")
    
    # Product metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>Total Products</h3>
                <h2>{}</h2>
            </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h3>Avg Price</h3>
                <h2>${:.2f}</h2>
            </div>
        """.format(filtered_df['price'].mean()), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <h3>Avg Rating</h3>
                <h2>⭐ {:.1f}</h2>
            </div>
        """.format(filtered_df['avg_rating'].mean()), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class="metric-card">
                <h3>Categories</h3>
                <h2>{}</h2>
            </div>
        """.format(filtered_df['category'].nunique()), unsafe_allow_html=True)
    
    st.markdown("### Product Distribution")
    
    # Interactive scatter plot
    fig = px.scatter(
        filtered_df,
        x='price',
        y='avg_rating',
        size='total_ratings',
        color='category',
        hover_name='name',
        title='Price vs Rating Distribution',
        template='plotly_white'
    )
    fig.update_layout(
        plot_bgcolor='white',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Product table
    st.markdown("### Product List")
    st.dataframe(
        filtered_df[['name', 'category', 'price', 'avg_rating', 'total_ratings']],
        use_container_width=True
    )

elif page == "Recommendation Engine":
    st.title("🎯 Recommendation Engine")
    
    # Product selection
    selected_product = st.selectbox(
        "Select a product to get recommendations",
        filtered_df['name'].tolist()
    )
    
    if selected_product:
        # Get recommendations
        recommendations = recommender.get_recommendations(selected_product)
        rec_df = pd.DataFrame(recommendations)
        
        # Display selected product details
        product = filtered_df[filtered_df['name'] == selected_product].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Selected Product")
            st.markdown(f"""
                <div class="metric-card">
                    <h3>{product['name']}</h3>
                    <p>Category: {product['category']}</p>
                    <p>Price: ${product['price']:.2f}</p>
                    <p>Rating: {'⭐' * int(product['avg_rating'])} ({product['avg_rating']:.1f})</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Similarity visualization
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=recommendations[0]['similarity'] * 100,
                title={'text': "Top Recommendation Similarity"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "#4A90E2"},
                       'steps': [
                           {'range': [0, 33], 'color': "#FF9999"},
                           {'range': [33, 66], 'color': "#FFD700"},
                           {'range': [66, 100], 'color': "#90EE90"}
                       ]}
            ))
            st.plotly_chart(fig)
        
        # Display recommendations
        st.markdown("### Recommended Products")
        for i, rec in enumerate(recommendations[:5]):
            st.markdown(f"""
                <div class="metric-card">
                    <h4>{i+1}. {rec['name']}</h4>
                    <p>Similarity: {rec['similarity']*100:.1f}%</p>
                    <p>Category: {rec['category']}</p>
                    <p>Price: ${rec['price']:.2f}</p>
                    <p>Rating: {'⭐' * int(rec['avg_rating'])} ({rec['avg_rating']:.1f})</p>
                </div>
            """, unsafe_allow_html=True)

elif page == "Analytics Dashboard":
    st.title("📊 Analytics Dashboard")
    
    # Category distribution
    st.markdown("### Category Distribution")
    cat_dist = filtered_df['category'].value_counts()
    fig = px.pie(
        values=cat_dist.values,
        names=cat_dist.index,
        title='Products by Category',
        template='plotly_white',
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Price distribution
    st.markdown("### Price Distribution")
    fig = px.histogram(
        filtered_df,
        x='price',
        nbins=30,
        title='Price Distribution',
        template='plotly_white',
        color_discrete_sequence=['#4A90E2']
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Rating analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Rating Distribution")
        fig = px.box(
            filtered_df,
            y='avg_rating',
            x='category',
            title='Ratings by Category',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Price vs Ratings")
        fig = px.density_heatmap(
            filtered_df,
            x='price',
            y='avg_rating',
            title='Price vs Rating Density',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top rated products
    st.markdown("### Top Rated Products")
    top_rated = filtered_df.nlargest(10, 'avg_rating')[
        ['name', 'category', 'price', 'avg_rating', 'total_ratings']
    ]
    st.dataframe(top_rated, use_container_width=True)

else:  # Smart Product Recommendations
    st.title("🛍️ Smart Product Recommendations")
    st.markdown("""
    This dashboard helps you discover similar products based on user behavior and item similarity.
    Search for products, filter by category, and rate them to get personalized recommendations!
    """)
    
    # Create three columns for layout
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col1:
        st.subheader("Find Products")
        
        # Add search box
        search_term = st.text_input("🔍 Search products", "")
        
        # Add category filter
        categories = ["All Categories"] + recommender.get_categories()
        selected_category = st.selectbox("📁 Filter by category", categories)
        
        # Get filtered product list
        all_products = recommender.get_all_product_names()
        filtered_products = recommender.filter_products(all_products, search_term, selected_category)
        
        if not filtered_products:
            st.warning("No products found matching your criteria.")
        else:
            selected_product = st.selectbox(
                "Choose a product:",
                options=filtered_products
            )
            
            if selected_product:
                # Show product details
                product_details = recommender.get_product_details(selected_product)
                with st.expander("Product Details", expanded=True):
                    st.markdown(f"""
                    **Category:** {product_details['category']}
                    **Average Rating:** {'⭐' * int(product_details['avg_rating'])} ({product_details['avg_rating']:.1f})
                    **Total Ratings:** {product_details['total_ratings']}
                    """)
                
                # Add rating section
                st.subheader("Rate this Product")
                rating = st.slider(
                    "Rate from 1 to 5 stars:",
                    min_value=1,
                    max_value=5,
                    value=3,
                    step=1
                )
                
                if st.button("Submit Rating"):
                    product_id = recommender.get_product_id_by_name(selected_product)
                    try:
                        recommender.add_rating(
                            st.session_state.user_id,
                            product_id,
                            rating
                        )
                        st.success(f"Thanks for rating {selected_product}!")
                    except Exception as e:
                        st.error(f"Error submitting rating: {str(e)}")
    
        if selected_product:
            # Get product ID from name
            product_id = recommender.get_product_id_by_name(selected_product)
            
            if product_id:
                # Get similar products
                similar_products = recommender.get_similar_products(product_id)
                
                with col2:
                    st.subheader("Recommended Similar Products")
                    
                    # Display recommendations in a nice format
                    for i, (product_name, similarity) in enumerate(similar_products, 1):
                        with st.container():
                            product_details = recommender.get_product_details(product_name)
                            st.markdown(f"""
                            #### {i}. {product_name}
                            **Category:** {product_details['category']}
                            **Average Rating:** {'⭐' * int(product_details['avg_rating'])} ({product_details['avg_rating']:.1f})
                            **Similarity Score:** {similarity:.2f}
                            """)
                            st.divider()
    
    with col3:
        st.subheader("Your Ratings")
        user_ratings = recommender.get_user_ratings(st.session_state.user_id)
        
        if user_ratings:
            # Group ratings by category
            ratings_by_category = {}
            for product_name, rating in user_ratings:
                category = recommender.get_product_category(product_name)
                if category not in ratings_by_category:
                    ratings_by_category[category] = []
                ratings_by_category[category].append((product_name, rating))
            
            # Display ratings grouped by category
            for category in sorted(ratings_by_category.keys()):
                with st.expander(f"📁 {category}", expanded=True):
                    for product_name, rating in ratings_by_category[category]:
                        st.markdown(f"**{product_name}**: {'⭐' * int(rating)}")
        else:
            st.info("You haven't rated any products yet.")
