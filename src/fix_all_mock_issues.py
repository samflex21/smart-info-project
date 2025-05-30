"""
This script performs a complete clean-up of the dashboard and recommender code
to remove ALL mock data and ensure ALL products from the dataset are displayed.
"""
import os
import re

def clean_dashboard_file():
    """Remove any remaining mock data or special handling from dashboard.py"""
    print("Cleaning dashboard.py to remove ALL mock data...")
    
    try:
        with open('dashboard.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("Could not read dashboard.py")
        return False
    
    # Check for any direct category fix remnants
    if "==== DIRECT CATEGORY FIX ====" in content:
        print("Found direct category fix code - removing it")
        
        # Find the start and end of the direct fix
        start_marker = "# ==== DIRECT CATEGORY FIX ===="
        start_pos = content.find(start_marker)
        if start_pos > 0:
            # Find the end of the fix (st.stop() command)
            end_marker = "st.stop()"
            end_pos = content.find(end_marker, start_pos)
            if end_pos > 0:
                # Remove the entire direct fix section
                content = content[:start_pos] + content[end_pos + len(end_marker):]
                print("Removed direct category fix section")
    
    # Replace all filtering code with simple filtering that doesn't show mock data
    filtering_pattern = r"# Apply filters to the data\nif selected_category != 'All':(.*?)if selected_country != 'All':"
    simple_filtering = """
# Apply filters to the data
if selected_category != 'All':
    # Simple category filtering - no mock data
    filtered_data = filtered_data[filtered_data['Category'] == selected_category]
    print(f"Filtered to {len(filtered_data)} products in category '{selected_category}'")
    
if selected_country != 'All':
"""
    
    # Use regex with DOTALL flag to match across multiple lines
    new_content = re.sub(filtering_pattern, simple_filtering, content, flags=re.DOTALL)
    
    if new_content != content:
        # Write the cleaned file
        try:
            with open('dashboard.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("Successfully cleaned dashboard.py")
            return True
        except Exception as e:
            print(f"Error writing to dashboard.py: {e}")
            return False
    else:
        print("No changes needed in dashboard.py")
        return True

def check_recommender_for_limiting():
    """Check recommender.py for any code that limits products"""
    print("Checking recommender.py for product limiting code...")
    
    try:
        with open('recommender.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        print("Could not read recommender.py")
        return False
    
    # Look for any code that might be limiting products
    limiting_patterns = [
        "top_", "nlargest", "head(", "limit", "max(", "[:100]", "[0:100]", 
        "balanced_data = pd.DataFrame()", "sample("
    ]
    
    found_limiting = False
    for pattern in limiting_patterns:
        if pattern in content:
            print(f"Potential limiting code found: '{pattern}'")
            found_limiting = True
    
    # Ensure we're using all products
    if "balanced_data = self.data.copy()" not in content:
        print("WARNING: Not using all products from dataset!")
        found_limiting = True
    
    return not found_limiting

if __name__ == "__main__":
    print("===== FIXING ALL MOCK DATA ISSUES =====")
    
    # Clean the dashboard
    dashboard_cleaned = clean_dashboard_file()
    
    # Check recommender
    recommender_ok = check_recommender_for_limiting()
    
    if dashboard_cleaned and recommender_ok:
        print("\n✅ All fixes applied successfully!")
        print("Restart the dashboard to see all real products from your dataset.")
    else:
        print("\n⚠️ Some issues could not be fixed automatically.")
        print("Please check the output above for details.")
