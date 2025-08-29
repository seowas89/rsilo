import streamlit as st
import requests
import pandas as pd
from urllib.parse import urljoin
from bs4 import BeautifulSoup
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
**Power up your Pillar Page** by identifying supporting pages from your sitemap that should link to your pillar page.
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
    st.caption("Get your key from [SerpApi](https://serpapi.com/).")
    st.markdown("---")
    st.info("""
    **How it works:**
    1. Enter your Pillar Page URL and sitemap.
    2. The app fetches all URLs from your sitemap.
    3. It checks if these pages already link to your pillar.
    4. You get a list of pages to add internal links from.
    """)

# Main form for inputs
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        pillar_url = st.text_input("Pillar Page URL", st.session_state.pillar_url, 
                                  placeholder="https://yourdomain.com/ultimate-guide/")
    with col2:
        sitemap_url = st.text_input("Sitemap URL", st.session_state.sitemap_url, 
                                   placeholder="https://yourdomain.com/sitemap.xml")
    
    serpapi_key = st.text_input("SerpApi Key (optional)", type="password")
    
    submitted = st.form_submit_button("Analyze Website")

# Function to fetch and parse sitemap
def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()
        
        # Simple XML parsing without external dependencies
        if "<urlset" in response.text:
            # Basic XML parsing for sitemaps
            urls = []
            lines = response.text.split("\n")
            for line in lines:
                if "<loc>" in line and "</loc>" in line:
                    start = line.find("<loc>") + 5
                    end = line.find("</loc>")
                    if start < end:
                        urls.append(line[start:end].strip())
            return urls
        else:
            st.error("Sitemap format not recognized. Please provide a valid sitemap URL.")
            return []
    except Exception as e:
        st.error(f"Error parsing sitemap: {e}")
        return []

# Function to check if a page links to the pillar URL
def check_internal_link(page_url, pillar_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(page_url, timeout=8, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all links on the page
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(page_url, href)
            # Check if the link points to the pillar page
            if absolute_url == pillar_url:
                return True
        return False
    except Exception as e:
        st.warning(f"Could not check {page_url}: {e}")
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
            
            # Filter out the pillar URL itself
            supporting_urls = [url for url in all_urls if url != pillar_url]
            
            # For demo purposes, let's limit to 10 URLs to avoid timeouts
            if len(supporting_urls) > 10:
                st.info(f"Limiting analysis to first 10 URLs for demo. Found {len(supporting_urls)} total.")
                supporting_urls = supporting_urls[:10]
            
            st.info(f"Analyzing {len(supporting_urls)} pages...")
            
            results = []
            
            for i, url in enumerate(supporting_urls):
                st.write(f"Checking: {url}")
                
                # Check if the page already links to the pillar
                has_link = check_internal_link(url, pillar_url)
                
                results.append({
                    "url": url,
                    "already_linked": has_link,
                    "action": "✅ Linked" if has_link else "🔴 Add Link"
                })
                
                # Add a small delay to be respectful to servers
                time.sleep(1)
            
            if results:
                # Create DataFrame
                df = pd.DataFrame(results)
                
                st.session_state.results = df
                
                # Summary statistics
                linked_count = df['already_linked'].sum()
                unlinked_count = len(df) - linked_count
                
                st.subheader("📊 Results Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Pages", len(df))
                col2.metric("Already Linked", linked_count)
                col3.metric("Opportunities", unlinked_count)
                
                # Display the results table
                st.subheader("📋 Page Analysis")
                st.dataframe(
                    df,
                    column_config={
                        "url": "Page URL",
                        "already_linked": "Already Linked?",
                        "action": "Recommended Action"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Display recommendations
                st.subheader("🎯 Linking Opportunities")
                opportunities = df[df['already_linked'] == False]
                
                if not opportunities.empty:
                    st.write("These pages should link to your pillar page:")
                    for _, row in opportunities.iterrows():
                        st.markdown(f"- [{row['url']}]({row['url']})")
                else:
                    st.success("🎉 All pages are already linked to your pillar page!")
            else:
                st.warning("No pages were analyzed.")

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
