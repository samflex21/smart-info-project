import streamlit as st
import pandas as pd
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Simple Product Display",
    page_icon="🛍️",
    layout="wide"
)

# Title
st.title("🛍️ Category Product Viewer")
st.write("This simplified dashboard focuses on showing products from all categories")

# Load data function
def load_data():
    # Try to load the updated dataset first
    try:
        df = pd.read_csv("ecommerce_dataset_updated.csv", encoding='latin-1')
        st.sidebar.success("Using updated dataset")
    except:
        try:
            df = pd.read_csv("ecommerce dataset.csv", encoding='latin-1')
            st.sidebar.warning("Using original dataset")
        except:
            st.error("Could not load any dataset")
            return None
    
    # Clean data
    df['Rating'] = df['Rating'].fillna(0)
    df['Sales'] = df['Sales'].fillna(0)
    df['Product'] = df['Product'].fillna('Unnamed Product')
    df['Country'] = df['Country'].fillna('Unknown')
    df['Category'] = df['Category'].fillna('Uncategorized')
    
    # Ensure Product Image URL is valid
    for i, row in df.iterrows():
        if pd.isna(row['Product Image URL']) or not isinstance(row['Product Image URL'], str) or row['Product Image URL'].strip() == '':
            category = str(row['Category']).replace(' ', '+')
            df.at[i, 'Product Image URL'] = f"https://via.placeholder.com/140x140?text={category}"
    
    # Print debug info
    st.sidebar.write(f"Total products loaded: {len(df)}")
    category_counts = df['Category'].value_counts().to_dict()
    st.sidebar.write("Products per category:")
    for cat, count in category_counts.items():
        st.sidebar.write(f"- {cat}: {count}")
    
    return df

# Load the data
df = load_data()
if df is None:
    st.stop()

# Category selection
categories = ['All'] + sorted(df['Category'].unique().tolist())
selected_category = st.selectbox('Select a category to view products', categories)

# Filter by category
if selected_category != 'All':
    filtered_df = df[df['Category'] == selected_category]
    st.write(f"Showing {len(filtered_df)} products in category: {selected_category}")
else:
    filtered_df = df
    st.write(f"Showing all {len(filtered_df)} products")

# Display products in a grid
cols_per_row = 3
total_products = len(filtered_df)

for i in range(0, total_products, cols_per_row):
    # Create a row with multiple columns
    cols = st.columns(cols_per_row)
    
    # Add products to each column
    for col_idx in range(cols_per_row):
        product_idx = i + col_idx
        
        # Make sure we don't go beyond the available products
        if product_idx < total_products:
            product = filtered_df.iloc[product_idx]
            
            with cols[col_idx]:
                st.subheader(product['Product'])
                
                # Display image
                image_url = product['Product Image URL']
                if pd.isna(image_url) or image_url == '':
                    image_url = "https://via.placeholder.com/140x140?text=No+Image"
                
                st.image(image_url, width=140)
                
                # Display product details
                st.write(f"**Category:** {product['Category']}")
                st.write(f"**Rating:** {'⭐' * int(product['Rating'])} ({product['Rating']})")
                st.write(f"**Price:** ${product['Sales']:.2f}")
                
                if 'Country' in product and not pd.isna(product['Country']):
                    st.write(f"**Country:** {product['Country']}")
                
                # Add a view details button
                if st.button(f"View Details", key=f"btn_{product_idx}"):
                    st.session_state['selected_product'] = product['Product']

# If a product is selected, show details
if 'selected_product' in st.session_state:
    st.markdown("---")
    st.header(f"Details for: {st.session_state['selected_product']}")
    
    # Get the selected product
    product_details = df[df['Product'] == st.session_state['selected_product']].iloc[0]
    
    # Display all available details
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(product_details['Product Image URL'], width=200)
    
    with col2:
        for col in product_details.index:
            if not pd.isna(product_details[col]) and col not in ['Product Image URL']:
                st.write(f"**{col}:** {product_details[col]}")
