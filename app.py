import streamlit as st
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urljoin, urlparse
import time

# Set page title and icon
st.set_page_config(
    page_title="Reverse Silo Architect",
    page_icon="🔗"
)

# Title and description
st.title("🔗 Reverse Silo Architect")
st.markdown("""
This tool helps you identify which pages from your website should link to your pillar page.
Enter your website URL and pillar page URL below.
""")

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Main form for inputs
with st.form("input_form"):
    website_url = st.text_input("Website URL", placeholder="https://yourdomain.com")
    pillar_url = st.text_input("Pillar Page URL", placeholder="https://yourdomain.com/ultimate-guide/")
    
    submitted = st.form_submit_button("Analyze Website")

# Function to generate a simple sitemap by crawling the homepage
def get_site_urls(website_url):
    try:
        # Just return some example URLs for demonstration
        # In a real implementation, you would crawl the site
        example_urls = [
            f"{website_url}/blog/post1",
            f"{website_url}/blog/post2", 
            f"{website_url}/services",
            f"{website_url}/about",
            f"{website_url}/contact"
        ]
        return example_urls
    except Exception as e:
        st.error(f"Error: {e}")
        return []

# Process the analysis when the form is submitted
if submitted and website_url and pillar_url:
    # Validate URLs
    if not website_url.startswith('http'):
        st.error("Please enter a valid Website URL with http:// or https://")
    elif not pillar_url.startswith('http'):
        st.error("Please enter a valid Pillar Page URL with http:// or https://")
    else:
        with st.spinner("Analyzing your website..."):
            # Get URLs (in a real app, this would crawl your site)
            all_urls = get_site_urls(website_url)
            
            # Simulate analysis
            time.sleep(2)
            
            # Create sample results
            results = [
                {"url": f"{website_url}/blog/post1", "should_link": True, "reason": "Related topic"},
                {"url": f"{website_url}/blog/post2", "should_link": True, "reason": "Related topic"},
                {"url": f"{website_url}/services", "should_link": False, "reason": "Not relevant"},
                {"url": f"{website_url}/about", "should_link": True, "reason": "Authority building"},
                {"url": f"{website_url}/contact", "should_link": False, "reason": "Not relevant"}
            ]
            
            st.session_state.results = results
            
            # Display results
            st.subheader("Analysis Results")
            
            opportunities = [r for r in results if r["should_link"]]
            
            if opportunities:
                st.success(f"Found {len(opportunities)} pages that should link to your pillar page:")
                for result in opportunities:
                    st.write(f"- {result['url']} ({result['reason']})")
            else:
                st.info("No linking opportunities found.")
                
            st.info("Note: This is a demonstration version. A full implementation would crawl your actual website.")

elif submitted:
    st.error("Please fill in both URL fields.")

# Add some information about reverse silos
with st.expander("What is a Reverse Silo?"):
    st.markdown("""
    A Reverse Silo is an SEO strategy where you:
    
    1. Create a comprehensive pillar page on a core topic
    2. Identify all related pages on your website
    3. Add links from those pages back to your pillar page
    
    This helps search engines understand your content structure and boosts the authority of your pillar page.
    """)

# Add a footer
st.markdown("---")
st.caption("Reverse Silo Architect Tool - This is a simplified demonstration version.")
