"""
This script modifies the dashboard to prioritize real data from the dataset for all categories.
"""

import re

def apply_real_data_fix():
    print("Applying fix to prioritize real dataset products...")
    
    # Read the dashboard.py file
    try:
        with open('dashboard.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("Could not read dashboard.py")
        return False
    
    # Create improved category handling code
    real_data_fix = """
# ==== IMPROVED CATEGORY FIX ====
# This section prioritizes real data but ensures something always displays

# Special handling for problematic categories
if selected_category in ['Luxury Jewelry', 'Make up']:
    print(f"Handling category: {selected_category}")
    
    # First try to get real products from the dataset
    real_products = df[df['Category'] == selected_category]
    
    # If we found real products, use them
    if len(real_products) > 0:
        print(f"Found {len(real_products)} real products in {selected_category}")
        filtered_data = real_products.copy()
        st.success(f"Showing {len(filtered_data)} products from your dataset in the '{selected_category}' category")
    else:
        # Fall back to sample products only if necessary
        print(f"No real products found for {selected_category}, using samples")
        if selected_category == 'Luxury Jewelry':
            sample_products = [
                {
                    'Product': 'Diamond Tennis Bracelet',
                    'Category': 'Luxury Jewelry',
                    'Rating': 4.8,
                    'Sales': 899.99,
                    'Country': 'United States',
                    'Product Image URL': 'https://via.placeholder.com/140x140?text=Diamond+Bracelet'
                },
                {
                    'Product': 'Pearl Necklace Set',
                    'Category': 'Luxury Jewelry',
                    'Rating': 4.7,
                    'Sales': 599.99,
                    'Country': 'Italy',
                    'Product Image URL': 'https://via.placeholder.com/140x140?text=Pearl+Necklace'
                },
                {
                    'Product': 'Gold Hoop Earrings',
                    'Category': 'Luxury Jewelry',
                    'Rating': 4.6,
                    'Sales': 349.99,
                    'Country': 'France',
                    'Product Image URL': 'https://via.placeholder.com/140x140?text=Gold+Earrings'
                }
            ]
        else:  # Make up
            sample_products = [
                {
                    'Product': 'Luxury Eyeshadow Palette',
                    'Category': 'Make up',
                    'Rating': 4.9,
                    'Sales': 89.99,
                    'Country': 'France',
                    'Product Image URL': 'https://via.placeholder.com/140x140?text=Eyeshadow+Palette'
                },
                {
                    'Product': 'Premium Foundation',
                    'Category': 'Make up',
                    'Rating': 4.7,
                    'Sales': 59.99,
                    'Country': 'United States',
                    'Product Image URL': 'https://via.placeholder.com/140x140?text=Foundation'
                },
                {
                    'Product': 'Waterproof Mascara',
                    'Category': 'Make up',
                    'Rating': 4.5,
                    'Sales': 29.99,
                    'Country': 'Italy',
                    'Product Image URL': 'https://via.placeholder.com/140x140?text=Mascara'
                }
            ]
        
        # Convert sample products to DataFrame
        filtered_data = pd.DataFrame(sample_products)
        st.info(f"Showing sample products for the '{selected_category}' category")
else:
    # Regular filtering for other categories
    if selected_category != 'All':
        if selected_category in filtered_data['Category'].values:
            filtered_data = filtered_data[filtered_data['Category'] == selected_category]
        else:
            st.warning(f"No products found in the '{selected_category}' category.")
            filtered_data = pd.DataFrame(columns=filtered_data.columns)
"""

    # Find where to insert our improved fix
    # Replace the entire category filtering block
    search_pattern = """# Apply filters to the data
if selected_category != 'All':"""
    
    # Find the end pattern to replace until
    end_pattern = "if selected_country != 'All':"
    
    if search_pattern in content and end_pattern in content:
        # Extract everything before and after the section we want to replace
        start_idx = content.find(search_pattern)
        end_idx = content.find(end_pattern)
        
        # Create new content
        new_content = content[:start_idx] + search_pattern + real_data_fix + "\n" + end_pattern + content[end_idx + len(end_pattern):]
        
        # Write the modified file
        try:
            with open('dashboard.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Successfully applied real data fix to dashboard.py")
            return True
        except Exception as e:
            print(f"Error writing modified file: {e}")
            return False
    else:
        print(f"Could not find patterns to replace")
        return False

if __name__ == "__main__":
    apply_real_data_fix()
