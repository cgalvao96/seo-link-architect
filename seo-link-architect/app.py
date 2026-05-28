import streamlit as st
import google.genai as genai
from google.genai import types
import pandas as pd
import json

# Page configurations
st.set_page_config(
    page_title="Internal Link SEO Architect",
    page_icon="🕸️",
    layout="wide"
)

# Application Header
st.title("🕸️ Internal Link SEO Architect")
st.subheader("Micro-SaaS Prototype: Semantic Link Mapping Engine")

# Sidebar Configuration & Monetization Anchors
with st.sidebar:
    st.header("⚙️ API Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    st.markdown("---")
    st.markdown("### 💰 Asset Valuation Data")
    st.metric(label="Target Acquisition Value", value="$1,500")
    st.markdown("**Target Audience:** Blog Flippers, SEO Agencies")
    st.markdown("**Engine State:** Stateless / Cloud-Ready")

# Helper function for Gemini semantic mapping
def generate_link_suggestions(csv_data_string, api_key):
    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = (
            "You are an expert SEO data architect. Analyze the provided web pages and keywords. "
            "Identify pairs of pages that share semantic relevance. Recommend strategic internal links. "
            "You MUST reply ONLY with a valid JSON array of objects. Do not include markdown code blocks or wrapping. "
            "Each object must strictly contain these keys: 'source_url', 'target_url', 'anchor_text', and 'relevance_rationale'."
        )
        
        prompt = f"Analyze this site data and output the JSON mapping array:\n\n{csv_data_string}"
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

# Main UI Layout
st.markdown("### 1. Upload Content Inventory")
st.write("Upload a CSV containing your site URLs, Page Titles, and Target Keywords.")

# Sample template download button
sample_data = pd.DataFrame({
    'url': ['https://mysite.com', 'https://mysite.com', 'https://mysite.com'],
    'title': ['Top 10 Running Shoes 2026', 'Ultimate Guide to Marathon Training', 'Beginner Keto Meal Plan'],
    'target_keyword': ['running shoes', 'marathon training', 'keto diet']
})

st.download_button(
    label="📥 Download Sample CSV Template",
    data=sample_data.to_csv(index=False),
    file_name="seo_template.csv",
    mime="text/csv"
)

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.markdown("#### Previewing Uploaded Data")
    st.dataframe(df, use_container_width=True)
    
    # Validation checks
    required_cols = ['url', 'title', 'target_keyword']
    if not all(col in df.columns for col in required_cols):
        st.error(f"CSV must contain these exact columns: {required_cols}")
    else:
        st.markdown("### 2. Generate Semantic Architecture")
        if st.button("⚡ Analyze & Map Internal Links"):
            if not api_key:
                st.warning("Please enter your Gemini API key in the sidebar.")
            else:
                with st.spinner("Analyzing semantic relationships with Gemini 2.5-Flash..."):
                    # Convert dataframe to string chunk for the LLM context
                    csv_payload = df.to_csv(index=False)
                    raw_json = generate_link_suggestions(csv_payload, api_key)
                    
                    if raw_json:
                        try:
                            # Clean up potential markdown formatting blockages
                            clean_json = raw_json.strip().strip("```json").strip("```")
                            results_list = json.loads(clean_json)
                            results_df = pd.DataFrame(results_list)
                            
                            st.success("🎉 Semantic Internal Link Mapping Complete!")
                            
                            # Display metrics
                            st.metric(label="Total Opportunities Identified", value=len(results_df))
                            
                            # Render actionable table
                            st.markdown("#### Internal Link Blueprint")
                            st.dataframe(results_df, use_container_width=True)
                            
                            # Export features
                            st.download_button(
                                label="💾 Export Blueprint to CSV",
                                data=results_df.to_csv(index=False),
                                file_name="internal_link_blueprint.csv",
                                mime="text/csv"
                            )
                        except Exception as parse_error:
                            st.error("Failed to parse API response. Please try clicking the button again.")
                            st.code(raw_json)
