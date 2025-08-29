import streamlit as st
import requests
import xmltodict
import pandas as pd
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import os
import time
import sys
import subprocess

# Function to check and install missing packages
def install_missing_packages():
    required = ['requests', 'beautifulsoup4', 'xmltodict', 'pandas', 'lxml']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install any missing packages
install_missing_packages()

# Set page title and icon
st.set_page_config(
    page_title="Reverse Silo Architect",
    page_icon="🔗",
    layout="wide"
)

# Title and description
st.title("🔗 Reverse Silo Architect")
st.markdown("""
**Power up your Pillar Page** by identifying the best supporting pages from your sitemap that are ranking for relevant keywords but are *not* linked to it.
This tool uses the Reverse Silo SEO strategy.
""")

# Initialize session state variables if they don't exist
if 'results' not in st.session_state:
    st.session_state.results = None
if 'pillar_url' not in st.session_state:
    st.session_state.pillar_url = ""
if 'sitemap_url' not in st.session_state:
    st.session_state.sitemap_url = ""

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    serpapi_key = st.text_input("Enter your SerpApi Key", type="password")
    st.caption("Get your key from [SerpApi](https://serpapi.com/).")
    st.markdown("---")
    st.info("""
    **How it works:**
    1. Enter your Pillar Page URL and sitemap.
    2. The app fetches all URLs from your sitemap.
    3. It uses SerpApi to find pages ranking for keywords related to your pillar topic.
    4. It checks if those top-performing pages already link to your pillar.
    5. You get a list of high-potential pages to add internal links from.
    """)

# Main form for inputs
with st.form("input_form"):
    col1, col2 = st.columns(2)
    with col1:
        pillar_url = st.text_input("Pillar Page URL", st.session_state.pillar_url, placeholder="https://yourdomain.com/ultimate-guide/")
    with col2:
        sitemap_url = st.text_input("Sitemap URL", st.session_state.sitemap_url, placeholder="https://yourdomain.com/sitemap.xml")
    
    submitted = st.form_submit_button("Analyze Website")

# Function to fetch and parse sitemap
def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        response.raise_for_status()  # Raises an exception for bad status codes
        data = xmltodict.parse(response.content)
        
        urls = []
        # Handle both regular sitemaps and index sitemaps
        if 'urlset' in data:
            for entry in data['urlset']['url']:
                if isinstance(entry, dict) and 'loc' in entry:
                    urls.append(entry['loc'])
        elif 'sitemapindex' in data:
            for sitemap in data['sitemapindex']['sitemap']:
                if isinstance(sitemap, dict) and 'loc' in sitemap:
                    # Recursively fetch URLs from nested sitemap
                    nested_urls = get_urls_from_sitemap(sitemap['loc'])
                    urls.extend(nested_urls)
        return urls
    except Exception as e:
        st.error(f"Error parsing sitemap: {e}")
        return []

# Function to check if a page links to the pillar URL
def check_internal_link(page_url, pillar_url):
    try:
        response = requests.get(page_url, timeout=8)
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

# Function to get SerpApi data for a URL
def get_serpapi_ranking_data(api_key, url):
    """Fetches the top ranking keywords for a given URL from SerpApi."""
    params = {
        "api_key": api_key,
        "engine": "google_search",
        "q": f"site:{url}",  # Query to find pages indexing this URL
        "hl": "en",
        "gl": "us",
        "num": 20  # Get top 20 results
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params, timeout=30)
        results = response.json()
        
        keywords = []
        # Check if organic results exist
        if 'organic_results' in results:
            for result in results['organic_results']:
                # Check if this result is our target URL
                if 'link' in result and result['link'] == url:
                    # Extract the keyword(s) from the result
                    if 'query' in result:
                        keywords.append(result['query'])
        return keywords
    except Exception as e:
        st.error(f"SerpApi Error for {url}: {e}")
        return []

# Process the analysis when the form is submitted
if submitted and pillar_url and sitemap_url and serpapi_key:
    st.session_state.pillar_url = pillar_url
    st.session_state.sitemap_url = sitemap_url
    
    # Validate URLs
    if not pillar_url.startswith('http'):
        st.error("Please enter a valid Pillar Page URL with http:// or https://")
    elif not sitemap_url.startswith('http'):
        st.error("Please enter a valid Sitemap URL with http:// or https://")
    else:
        with st.spinner("🔄 Fetching and parsing sitemap... This may take a while for large sites."):
            all_urls = get_urls_from_sitemap(sitemap_url)
        
        if not all_urls:
            st.error("No URLs found in the sitemap. Please check the URL.")
        else:
            st.success(f"Found {len(all_urls)} URLs in the sitemap.")
            
            # Filter out the pillar URL itself and other irrelevant pages
            supporting_urls = [url for url in all_urls if url != pillar_url]
            st.info(f"Analyzing {len(supporting_urls)} supporting pages...")
            
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            analyzed_count = 0
            
            for url in supporting_urls:
                analyzed_count += 1
                status_text.text(f"Analyzing page {analyzed_count}/{len(supporting_urls)}: {url[:60]}...")
                progress_bar.progress(analyzed_count / len(supporting_urls))
                
                # Get ranking keywords from SerpApi
                ranking_keywords = get_serpapi_ranking_data(serpapi_key, url)
                
                # Only proceed if the page is ranking for at least one keyword
                if ranking_keywords:
                    # Check if the page already links to the pillar
                    has_link = check_internal_link(url, pillar_url)
                    
                    results.append({
                        "url": url,
                        "ranking_keywords": ", ".join(ranking_keywords),
                        "keyword_count": len(ranking_keywords),
                        "already_linked": has_link,
                        "action": "✅ Linked" if has_link else "🔴 Add Link"
                    })
                
                # Be nice to the APIs and servers
                time.sleep(0.5)
            
            progress_bar.empty()
            status_text.empty()
            
            if results:
                # Create DataFrame and sort by keyword count (most important first)
                df = pd.DataFrame(results)
                df = df.sort_values(by='keyword_count', ascending=False)
                
                st.session_state.results = df
                
                # Summary statistics
                linked_count = df['already_linked'].sum()
                unlinked_count = len(df) - linked_count
                
                st.subheader("📊 Results Summary")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Analyzed Pages", len(df))
                col2.metric("Already Linked", linked_count, f"{(linked_count/len(df)*100):.1f}%")
                col3.metric("Opportunities", unlinked_count, f"{(unlinked_count/len(df)*100):.1f}%")
                
                # Display the results table
                st.subheader("📋 Page Analysis Details")
                st.dataframe(
                    df,
                    column_config={
                        "url": "Page URL",
                        "ranking_keywords": "Ranking Keywords",
                        "keyword_count": "Keyword Count",
                        "already_linked": "Already Linked?",
                        "action": "Recommended Action"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Display recommendations
                st.subheader("🎯 High-Priority Opportunities")
                opportunities = df[df['already_linked'] == False]
                
                if not opportunities.empty:
                    for _, row in opportunities.head(10).iterrows():
                        st.markdown(f"**Page:** [{row['url']}]({row['url']})")
                        st.markdown(f"**Ranking for:** {row['ranking_keywords']}")
                        st.markdown("---")
                else:
                    st.success("🎉 Amazing! All your top-performing pages are already linked to your pillar page. Your reverse silo is strong!")
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name="reverse_silo_analysis.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No supporting pages were found that are currently ranking for keywords. This could be due to:")
                st.markdown("""
                - The site is very new and not yet ranking
                - SerpApi needs more time to index data
                - The sitemap doesn't contain relevant content pages
                """)

elif submitted:
    st.error("Please fill in all fields (Pillar URL, Sitemap URL, and SerpApi Key) to proceed.")

# If we have results from a previous run, show them
if st.session_state.results is not None:
    st.sidebar.markdown("---")
    st.sidebar.info("Previous analysis results are loaded below.")
    if st.sidebar.button("Clear Results & Start New Analysis"):
        st.session_state.results = None
        st.session_state.pillar_url = ""
        st.session_state.sitemap_url = ""
        st.rerun()
