import streamlit as st
import urllib.request
import urllib.parse
import urllib.error
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET
import time

# Set page title and icon
st.set_page_config(
    page_title="Reverse Silo Architect",
    page_icon="🔗",
    layout="wide"
)

# Title and description
st.title("🔗 Reverse Silo Architect")
st.markdown("""
**Power up your Pillar Page** by identifying which pages from your sitemap should link to it.
This tool uses the Reverse Silo SEO strategy.
""")

# Initialize session state variables
if 'results' not in st.session_state:
    st.session_state.results = None
if 'pillar_url' not in st.session_state:
    st.session_state.pillar_url = ""
if 'sitemap_url' not in st.session_state:
    st.session_state.sitemap_url = ""

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    st.markdown("---")
    st.info("""
    **How it works:**
    1. Enter your Pillar Page URL and sitemap.
    2. The app fetches all URLs from your sitemap.
    3. You get a list of pages that could potentially link to your pillar.
    """)

# Main form for inputs
with st.form("input_form"):
    pillar_url = st.text_input("Pillar Page URL", st.session_state.pillar_url, 
                              placeholder="https://yourdomain.com/ultimate-guide/")
    sitemap_url = st.text_input("Sitemap URL", st.session_state.sitemap_url, 
                               placeholder="https://yourdomain.com/sitemap.xml")
    
    submitted = st.form_submit_button("Analyze Website")

# Function to fetch and parse sitemap using standard library only
def get_urls_from_sitemap(sitemap_url):
    try:
        # Fetch the sitemap
        with urllib.request.urlopen(sitemap_url) as response:
            sitemap_content = response.read().decode('utf-8')
        
        # Parse the XML
        root = ET.fromstring(sitemap_content)
        
        # Extract URLs
        urls = []
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        # Find all URL elements
        for url_elem in root.findall('ns:url', namespace):
            loc_elem = url_elem.find('ns:loc', namespace)
            if loc_elem is not None:
                urls.append(loc_elem.text)
        
        return urls
    except Exception as e:
        st.error(f"Error parsing sitemap: {e}")
        return []

# Function to check if a page might be related to the pillar topic
def is_potentially_related(page_url, pillar_url):
    # Simple heuristic: check if the page is on the same domain and path
    page_domain = urlparse(page_url).netloc
    pillar_domain = urlparse(pillar_url).netloc
    
    # If same domain, it's potentially related
    if page_domain == pillar_domain:
        return True
    
    # Add more heuristics here if needed
    return False

# Process the analysis when the form is submitted
if submitted and pillar_url and sitemap_url:
    st.session_state.pillar_url = pillar_url
    st.session_state.sitemap_url = sitemap_url
    
    # Validate URLs
    if not pillar_url.startswith('http'):
        st.error("Please enter a valid Pillar Page URL with http:// or https://")
    elif not sitemap_url.startswith('http'):
        st.error("Please enter a valid Sitemap URL with http:// or https://")
    else:
        with st.spinner("🔄 Fetching and parsing sitemap..."):
            all_urls = get_urls_from_sitemap(sitemap_url)
        
        if not all_urls:
            st.error("No URLs found in the sitemap. Please check the URL.")
        else:
            st.success(f"Found {len(all_urls)} URLs in the sitemap.")
            
            # Filter out the pillar URL itself and find potentially related pages
            supporting_urls = [url for url in all_urls if url != pillar_url and is_potentially_related(url, pillar_url)]
            
            # For demo purposes, let's limit to 10 URLs
            if len(supporting_urls) > 10:
                st.info(f"Limiting analysis to first 10 URLs. Found {len(supporting_urls)} total.")
                supporting_urls = supporting_urls[:10]
            
            st.info(f"Found {len(supporting_urls)} potentially related pages.")
            
            # Display results
            st.subheader("📋 Pages That Could Link to Your Pillar")
            
            for i, url in enumerate(supporting_urls):
                st.write(f"{i+1}. [{url}]({url})")
            
            st.session_state.results = supporting_urls
            
            st.success("Analysis complete! These pages could potentially link to your pillar page.")

elif submitted:
    st.error("Please fill in all required fields (Pillar URL and Sitemap URL).")

# If we have results from a previous run, show them
if st.session_state.results is not None:
    st.sidebar.markdown("---")
    st.sidebar.info("Previous analysis results are loaded.")
    if st.sidebar.button("Clear Results & Start New Analysis"):
        st.session_state.results = None
        st.session_state.pillar_url = ""
        st.session_state.sitemap_url = ""
        st.experimental_rerun()
